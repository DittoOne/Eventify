from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from datetime import datetime, date
import os
import uuid
import json

class CertificateGenerator:
    def __init__(self, app):
        self.app = app
        # Certificate storage folder
        self.cert_folder = os.path.join(app.static_folder, 'certificates')
        os.makedirs(self.cert_folder, exist_ok=True)
        
        # Certificate records (JSON file instead of database)
        self.records_file = os.path.join(self.cert_folder, 'certificate_records.json')
        self._init_records_file()
    
    def _init_records_file(self):
        """Initialize certificate records file"""
        if not os.path.exists(self.records_file):
            with open(self.records_file, 'w') as f:
                json.dump({}, f)
    
    def _load_records(self):
        """Load certificate records from JSON"""
        try:
            with open(self.records_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_records(self, records):
        """Save certificate records to JSON"""
        with open(self.records_file, 'w') as f:
            json.dump(records, f, indent=2, default=str)
    
    def _is_event_completed(self, event):
        """Check if event is completed (past end date and time)"""
        from datetime import datetime
        try:
            # Combine end date and time
            event_end = datetime.combine(event.end_date, event.end_time)
            return event_end < datetime.now()
        except:
            # Fallback to start date if end date not available
            event_start = datetime.combine(event.start_date, event.start_time)
            return event_start < datetime.now()
    
    def _is_user_registered(self, user, event):
        """Check if user is registered for the event"""
        return user in event.registered_users
    
    def can_generate_certificate(self, user, event):
        """Check if certificate can be generated for user and event"""
        # Must be registered for the event
        if not self._is_user_registered(user, event):
            return False, "You are not registered for this event"
        
        # Event must be completed
        if not self._is_event_completed(event):
            return False, "Certificate will be available after the event ends"
        
        # Check if certificate already exists
        records = self._load_records()
        cert_key = f"{event.id}_{user.id}"
        existing_cert = None
        for cert_id, data in records.items():
            if data.get('user_id') == user.id and data.get('event_id') == event.id:
                existing_cert = cert_id
                break
        
        if existing_cert:
            return False, "Certificate already generated"
        
        return True, "Certificate can be generated"
    
    def generate_certificate(self, user, event):
        """Generate certificate PDF - with validation"""
        # Validate before generating
        can_generate, message = self.can_generate_certificate(user, event)
        if not can_generate:
            raise ValueError(message)
        
        # Create unique certificate ID
        cert_id = f"CERT-{event.id}-{user.id}-{uuid.uuid4().hex[:8].upper()}"
        
        # PDF filename
        filename = f"{cert_id}.pdf"
        filepath = os.path.join(self.cert_folder, filename)
        
        # Create PDF
        doc = SimpleDocTemplate(filepath, pagesize=landscape(A4))
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CertTitle', parent=styles['Title'], fontSize=36,
            alignment=TA_CENTER, textColor=colors.blue, spaceAfter=30
        )
        name_style = ParagraphStyle(
            'CertName', parent=styles['Normal'], fontSize=28,
            alignment=TA_CENTER, textColor=colors.green, spaceAfter=20
        )
        content_style = ParagraphStyle(
            'CertContent', parent=styles['Normal'], fontSize=16,
            alignment=TA_CENTER, spaceAfter=12
        )
        
        # Certificate content
        story = []
        story.append(Spacer(1, 50))
        story.append(Paragraph("🏆 CERTIFICATE OF PARTICIPATION", title_style))
        story.append(Paragraph("EVENTIFY UNIVERSITY", content_style))
        story.append(Spacer(1, 30))
        story.append(Paragraph("This is to certify that", content_style))
        story.append(Paragraph(f"<u>{user.username}</u>", name_style))
        story.append(Paragraph("has successfully participated in", content_style))
        story.append(Paragraph(f'<b>"{event.title}"</b>', name_style))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Event Date: {event.start_date.strftime('%B %d, %Y')}", content_style))
        story.append(Paragraph(f"Location: {event.location}", content_style))
        story.append(Paragraph(f"Category: {event.category}", content_style))
        story.append(Spacer(1, 40))
        story.append(Paragraph(f"Certificate ID: {cert_id}", content_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", content_style))
        
        # Build PDF
        doc.build(story)
        
        # Save record
        records = self._load_records()
        records[cert_id] = {
            'user_id': user.id,
            'user_name': user.username,
            'user_email': user.email,
            'event_id': event.id,
            'event_title': event.title,
            'event_category': event.category,
            'event_start_date': event.start_date.strftime('%Y-%m-%d'),
            'event_end_date': event.end_date.strftime('%Y-%m-%d') if hasattr(event, 'end_date') else event.start_date.strftime('%Y-%m-%d'),
            'event_location': event.location,
            'generated_at': datetime.now().isoformat(),
            'download_count': 0,
            'filename': filename,
            'is_valid': True
        }
        self._save_records(records)
        
        return cert_id, filename
    
    def get_user_certificates(self, user_id):
        """Get all certificates for a user"""
        records = self._load_records()
        user_certs = []
        for cert_id, data in records.items():
            if data['user_id'] == user_id and data.get('is_valid', True):
                user_certs.append({
                    'id': cert_id,
                    'event_id': data['event_id'],
                    'event_title': data['event_title'],
                    #'event_category': data['event_category'],
                    #'event_date': data['event_start_date'],
                    'generated_at': data['generated_at'],
                    'download_count': data.get('download_count', 0),
                    'filename': data['filename']
                })
        return sorted(user_certs, key=lambda x: x['generated_at'], reverse=True)
    
    def get_user_eligible_events(self, user):
        """Get events for which user can generate certificates"""
        eligible_events = []
        completed_cert_event_ids = []
        
        # Get already generated certificate event IDs
        user_certs = self.get_user_certificates(user.id)
        completed_cert_event_ids = [cert['event_id'] for cert in user_certs]
        
        # Check registered events
        for event in user.registered_events:
            if event.id not in completed_cert_event_ids and self._is_event_completed(event):
                eligible_events.append({
                    'event': event,
                    'can_generate': True,
                    'reason': 'Ready to generate certificate'
                })
        
        return eligible_events
    
    def get_user_pending_events(self, user):
        """Get events that are registered but not yet completed"""
        pending_events = []
        
        for event in user.registered_events:
            if not self._is_event_completed(event):
                pending_events.append({
                    'event': event,
                    'can_generate': False,
                    'reason': f'Event will end on {event.end_date if hasattr(event, "end_date") else event.start_date}'
                })
        
        return pending_events
    
    def record_download(self, cert_id):
        """Record certificate download"""
        records = self._load_records()
        if cert_id in records:
            records[cert_id]['download_count'] = records[cert_id].get('download_count', 0) + 1
            records[cert_id]['last_downloaded'] = datetime.now().isoformat()
            self._save_records(records)
    
    def verify_certificate(self, cert_id):
        """Verify certificate"""
        records = self._load_records()
        if cert_id in records and records[cert_id].get('is_valid', True):
            return {
                'valid': True,
                'data': records[cert_id]
            }
        return {'valid': False}