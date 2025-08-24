from models.event import Event
from models import db
from datetime import datetime, date

class AdminViewModel:
    @staticmethod
    def create_event(title, description, start_date, start_time, end_date, end_time, location, category, max_capacity, creator,images,documents):
        """Create a new event"""
        
        try:
            # Convert strings to proper Python objects
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date() if isinstance(start_date, str) else start_date
            end_date   = datetime.strptime(end_date, "%Y-%m-%d").date() if isinstance(end_date, str) else end_date
            start_time = datetime.strptime(start_time, "%H:%M").time() if isinstance(start_time, str) else start_time
            end_time   = datetime.strptime(end_time, "%H:%M").time() if isinstance(end_time, str) else end_time


            event = Event(
                title=title,
                description=description,
                start_date=start_date,
                start_time=start_time,
                end_date=end_date,
                end_time=end_time,
                location=location,
                category=category,
                max_capacity=max_capacity,
                creator=creator,
                images=images,
                documents=documents
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
        return Event.query.filter_by(creator=admin_user).order_by(Event.start_date.desc()).all()
    
    @staticmethod
    def update_event(event_id, title, description, start_date, start_time, end_date, end_time, location, category, max_capacity,images,documents):
        """Update an existing event"""
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date() if isinstance(start_date, str) else start_date
            end_date   = datetime.strptime(end_date, "%Y-%m-%d").date() if isinstance(end_date, str) else end_date
            start_time = datetime.strptime(start_time, "%H:%M").time() if isinstance(start_time, str) else start_time
            end_time   = datetime.strptime(end_time, "%H:%M").time() if isinstance(end_time, str) else end_time

            event = Event.query.get_or_404(event_id)
            
            event.title = title
            event.description = description
            event.start_date = start_date
            event.start_time = start_time
            event.end_date = end_date
            event.end_time = end_time
            event.location = location
            event.category = category
            event.max_capacity = max_capacity
            event.updated_at = datetime.utcnow()
            event.images = images
            event.documents = documents
            
            
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
        
        upcoming_events = [e for e in events if e.start_date >= date.today()]
        total_upcoming = len(upcoming_events)
        
        total_attendees = sum(e.registration_count for e in events)
        
        return {
            'total_events': total_events,
            'upcoming_events': total_upcoming,
            'total_attendees': total_attendees
        }