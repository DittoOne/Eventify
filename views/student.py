from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from viewmodels.student_viewmodel import StudentViewModel
from utils.certificate_generator import CertificateGenerator
from flask import send_file, flash, redirect, url_for, render_template
import os
from utils.certificate_generator import CertificateGenerator
from datetime import date, datetime
from werkzeug.utils import secure_filename
import os
from models import db
from models.event import Event
from sqlalchemy import not_
from flask import send_file

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.before_request
@login_required
def require_student():
    if not current_user.is_student():
        flash('Access denied. Students only.', 'error')
        return redirect(url_for('admin.dashboard'))

# Single dashboard route with recommendation features
@student_bp.route('/dashboard')
@login_required
def dashboard():
    registered_events = StudentViewModel.get_user_upcoming_registered_events(current_user)
    upcoming_events = StudentViewModel.get_upcoming_events()[:6]
    ongoing_events = StudentViewModel.get_ongoing_events()
    today_events = StudentViewModel.get_today_events()
    stats = StudentViewModel.get_dashboard_stats(current_user)
    
    # Add recommendations
    recommendations = StudentViewModel.get_user_recommendations(current_user, 5)
    trending_events = StudentViewModel.get_trending_events(5)
    
    return render_template('student/dashboard.html', 
                         registered_events=registered_events,
                         upcoming_events=upcoming_events,
                         ongoing_events=ongoing_events,
                         today_events=today_events,
                         stats=stats,
                         recommendations=recommendations,
                         trending_events=trending_events)

@student_bp.route('/events')
def events():
    # Get filter parameters
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    
    if search:
        upcoming_events = StudentViewModel.search_events(search)
    elif category:
        upcoming_events = StudentViewModel.get_events_by_category(category)
    elif status == 'ongoing':
        upcoming_events = StudentViewModel.get_ongoing_events()
    elif status == 'today':
        upcoming_events = StudentViewModel.get_today_events()
    else:
        upcoming_events = StudentViewModel.get_upcoming_events()
    
    return render_template('student/events.html', 
                         events=upcoming_events,
                         today=date.today())

@student_bp.route('/event/<int:event_id>')
def event_detail(event_id):
    event = StudentViewModel.get_event_by_id(event_id)
    is_registered = current_user in event.registered_users
    return render_template('student/event_detail.html', 
                         event=event, 
                         is_registered=is_registered)

@student_bp.route('/register/<int:event_id>', methods=['POST'])
def register_event(event_id):
    success, message = StudentViewModel.register_for_event(current_user, event_id)
    
    if request.headers.get('Content-Type') == 'application/json':
        return jsonify({'success': success, 'message': message})
    
    flash(message, 'success' if success else 'error')
    return redirect(url_for('student.event_detail', event_id=event_id))

@student_bp.route('/unregister/<int:event_id>', methods=['POST'])
def unregister_event(event_id):
    success, message = StudentViewModel.unregister_from_event(current_user, event_id)
    
    if request.headers.get('Content-Type') == 'application/json':
        return jsonify({'success': success, 'message': message})
    
    flash(message, 'success' if success else 'error')
    return redirect(url_for('student.event_detail', event_id=event_id))

@student_bp.route('/my-events')
def my_events():
    upcoming_events = StudentViewModel.get_user_upcoming_registered_events(current_user)
    past_events = StudentViewModel.get_user_past_registered_events(current_user)
    
    return render_template('student/my_events.html',
                         upcoming_events=upcoming_events,
                         past_events=past_events)

@student_bp.route('/ongoing-events')
def ongoing_events():
    ongoing_events = StudentViewModel.get_ongoing_events()
    return render_template('student/ongoing_events.html',
                         events=ongoing_events)

@student_bp.route('/api/event-status/<int:event_id>')
def event_status_api(event_id):
    """API endpoint to get real-time event status"""
    try:
        event = StudentViewModel.get_event_by_id(event_id)
        return jsonify({
            'success': True,
            'status': {
                'is_ongoing': event.is_ongoing,
                'is_past': event.is_past,
                'registration_count': event.registration_count,
                'is_full': event.is_full
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404

@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                upload_folder = os.path.join('static', 'uploads', 'profiles')
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                # Save relative path for use in template
                current_user.profile_image = f'uploads/profiles/{filename}'

        current_user.username = request.form['username']
        current_user.email = request.form['email']
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student.profile'))

    return render_template('student/profile.html', user=current_user)

@student_bp.route('/events/search')
@login_required
def search_events():
    search_query = request.args.get('q', '')
    category = request.args.get('category', 'all')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    location = request.args.get('location', '')
    time = request.args.get('time', '') 
    
    # Convert date strings to date objects if provided
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
    events = StudentViewModel.search_events(
        search_query=search_query,
        category=category,
        start_date=start_date,
        end_date=end_date
    )
    
    return render_template('search_events.html',
                          search_query=search_query,
                          events=events,
                          selected_category=category,
                          start_date=start_date,
                          end_date=end_date,
                          location=location,      
                          time=time,             
                          user_type='student')

@student_bp.route('/recommendations')
@login_required
def recommendations():
    """Dedicated recommendations page"""
    user_recommendations = StudentViewModel.get_user_recommendations(current_user, 10)
    trending_events = StudentViewModel.get_trending_events(10)
    
    return render_template('student/recommendations.html',
                         recommendations=user_recommendations,
                         trending_events=trending_events)

@student_bp.route('/debug-recommendations')
@login_required
def debug_recommendations():
    """Debug route to check recommendation system"""
    
    # Get some test data
    debug_info = {
        'user_events': current_user.registered_events,
        'upcoming_events_count': len(StudentViewModel.get_upcoming_events()),
        'available_events': [],
        'recommendations': [],
        'trending': []
    }
    
    # Get events user hasn't registered for
    user_event_ids = [e.id for e in current_user.registered_events]
    if user_event_ids:
        available_events = Event.query.filter(
            Event.start_date >= date.today(),
            not_(Event.id.in_(user_event_ids))
        ).limit(10).all()
    else:
        available_events = Event.query.filter(
            Event.start_date >= date.today()
        ).limit(10).all()
    
    debug_info['available_events'] = available_events
    
    try:
        debug_info['recommendations'] = StudentViewModel.get_user_recommendations(current_user, 5)
    except Exception as e:
        debug_info['recommendation_error'] = str(e)
    
    try:
        debug_info['trending'] = StudentViewModel.get_trending_events(5)
    except Exception as e:
        debug_info['trending_error'] = str(e)
    
    return render_template('student/debug_recommendations.html', debug_info=debug_info)
#certificates routes
cert_generator = None

def init_certificate_generator():
    global cert_generator
    from flask import current_app
    cert_generator = CertificateGenerator(current_app)

@student_bp.route('/certificates')
@login_required
def certificates():
    """View user certificates and eligible events"""
    if cert_generator is None:
        init_certificate_generator()
    
    # Get existing certificates
    user_certificates = cert_generator.get_user_certificates(current_user.id)
    
    # Get events eligible for certificate generation
    eligible_events = cert_generator.get_user_eligible_events(current_user)
    
    # Get pending events (not yet completed)
    pending_events = cert_generator.get_user_pending_events(current_user)
    
    return render_template('student/certificates.html', 
                         certificates=user_certificates,
                         eligible_events=eligible_events,
                         pending_events=pending_events)

@student_bp.route('/download-certificate/<cert_id>')
@login_required
def download_certificate_simple(cert_id):
    """Download certificate"""
    if cert_generator is None:
        init_certificate_generator()
        
    cert_data = cert_generator.verify_certificate(cert_id)
    
    if not cert_data['valid'] or cert_data['data']['user_id'] != current_user.id:
        flash('Certificate not found or access denied', 'error')
        return redirect(url_for('student.certificates'))
    
    # Record download
    cert_generator.record_download(cert_id)
    
    # Send file
    filepath = os.path.join(current_app.static_folder, 'certificates', cert_data['data']['filename'])
    if not os.path.exists(filepath):
        flash('Certificate file not found', 'error')
        return redirect(url_for('student.certificates'))
    
    return send_file(filepath, as_attachment=True, 
                    download_name=f"certificate_{cert_data['data']['event_title']}.pdf")

@student_bp.route('/generate-certificate/<int:event_id>')
@login_required
def generate_single_certificate(event_id):
    """Generate certificate for a specific event"""
    if cert_generator is None:
        init_certificate_generator()
    
    from models.event import Event
    event = Event.query.get_or_404(event_id)
    
    try:
        cert_id, filename = cert_generator.generate_certificate(current_user, event)
        flash(f'Certificate generated successfully for "{event.title}"!', 'success')
    except ValueError as e:
        flash(str(e), 'warning')
    except Exception as e:
        flash(f'Error generating certificate: {str(e)}', 'error')
    
    return redirect(url_for('student.certificates'))

@student_bp.route('/generate-all-certificates')
@login_required
def generate_all_certificates():
    """Generate certificates for all eligible events"""
    if cert_generator is None:
        init_certificate_generator()
    
    eligible_events = cert_generator.get_user_eligible_events(current_user)
    generated = 0
    errors = 0
    
    for event_data in eligible_events:
        event = event_data['event']
        try:
            cert_generator.generate_certificate(current_user, event)
            generated += 1
        except Exception as e:
            print(f"Error generating certificate for {event.title}: {e}")
            errors += 1
    
    if generated > 0:
        flash(f'Generated {generated} certificate(s) successfully!', 'success')
    if errors > 0:
        flash(f'{errors} certificate(s) could not be generated', 'warning')
    if generated == 0 and errors == 0:
        flash('No new certificates to generate', 'info')
    
    return redirect(url_for('student.certificates'))