from models.event import Event
from models.user import User
from models import db
from datetime import datetime, date

class StudentViewModel:
    @staticmethod
    def get_upcoming_events():
        """Get all upcoming events"""
        today = date.today()
        return Event.query.filter(Event.date >= today).order_by(Event.date, Event.time).all()
    
    @staticmethod
    def get_event_by_id(event_id):
        """Get event by ID"""
        return Event.query.get_or_404(event_id)
    
    @staticmethod
    def register_for_event(user, event_id):
        """Register user for an event"""
        try:
            event = Event.query.get_or_404(event_id)
            
            # Check if already registered
            if user in event.registered_users:
                return False, "Already registered for this event"
            
            # Check if event is full
            if event.is_full:
                return False, "Event is full"
            
            # Check if event is in the past
            if event.is_past:
                return False, "Cannot register for past events"
            
            # Register user
            event.registered_users.append(user)
            db.session.commit()
            
            return True, "Successfully registered for the event"
        except Exception as e:
            db.session.rollback()
            return False, f"Registration failed: {str(e)}"
    
    @staticmethod
    def unregister_from_event(user, event_id):
        """Unregister user from an event"""
        try:
            event = Event.query.get_or_404(event_id)
            
            if user in event.registered_users:
                event.registered_users.remove(user)
                db.session.commit()
                return True, "Successfully unregistered from the event"
            else:
                return False, "Not registered for this event"
        except Exception as e:
            db.session.rollback()
            return False, f"Unregistration failed: {str(e)}"
    
    @staticmethod
    def get_user_registered_events(user):
        """Get events user is registered for"""
        return user.registered_events