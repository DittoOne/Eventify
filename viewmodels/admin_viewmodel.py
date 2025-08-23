from models.event import Event
from models import db
from datetime import datetime, date

class AdminViewModel:
    @staticmethod
    def create_event(title, description, event_date, event_time, location, category, max_capacity, creator):
        """Create a new event"""
        try:
            event = Event(
                title=title,
                description=description,
                date=event_date,
                time=event_time,
                location=location,
                category=category,
                max_capacity=max_capacity,
                creator=creator
            )
            
            db.session.add(event)
            db.session.commit()
            
            return True, "Event created successfully"
        except Exception as e:
            db.session.rollback()
            return False, f"Event creation failed: {str(e)}"
    
    @staticmethod
    def get_admin_events(admin_user):
        """Get events created by admin"""
        return Event.query.filter_by(creator=admin_user).order_by(Event.date.desc()).all()
    
    @staticmethod
    def update_event(event_id, title, description, event_date, event_time, location, category, max_capacity):
        """Update an existing event"""
        try:
            event = Event.query.get_or_404(event_id)
            
            event.title = title
            event.description = description
            event.date = event_date
            event.time = event_time
            event.location = location
            event.category = category
            event.max_capacity = max_capacity
            event.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return True, "Event updated successfully"
        except Exception as e:
            db.session.rollback()
            return False, f"Event update failed: {str(e)}"
    
    @staticmethod
    def delete_event(event_id):
        """Delete an event"""
        try:
            event = Event.query.get_or_404(event_id)
            db.session.delete(event)
            db.session.commit()
            
            return True, "Event deleted successfully"
        except Exception as e:
            db.session.rollback()
            return False, f"Event deletion failed: {str(e)}"
    
    @staticmethod
    def get_event_attendees(event_id):
        """Get list of attendees for an event"""
        event = Event.query.get_or_404(event_id)
        return event.registered_users
    
    @staticmethod
    def get_admin_stats(admin_user):
        """Get admin dashboard statistics"""
        events = Event.query.filter_by(creator=admin_user).all()
        total_events = len(events)
        
        upcoming_events = [e for e in events if e.date >= date.today()]
        total_upcoming = len(upcoming_events)
        
        total_attendees = sum(e.registration_count for e in events)
        
        return {
            'total_events': total_events,
            'upcoming_events': total_upcoming,
            'total_attendees': total_attendees
        }