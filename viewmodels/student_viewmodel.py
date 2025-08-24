from models.event import Event
from models.user import User
from models import db
from datetime import datetime, date
from sqlalchemy import or_, and_
# Fix the import - use the correct module name
from models import reccomendation_engine

class StudentViewModel:
    @staticmethod
    def get_upcoming_events():
        """Get all upcoming events"""
        today = date.today()
        return Event.query.filter(Event.start_date >= today).order_by(Event.start_date, Event.start_time).all()
    
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
    
    @staticmethod
    def get_user_upcoming_registered_events(user):
        """Get all upcoming events that the user has registered for"""
        now = datetime.now()
        return [event for event in StudentViewModel.get_user_registered_events(user)
                if datetime.combine(event.start_date, event.start_time) > now]
    
    @staticmethod
    def get_user_past_registered_events(user):
        """Get all past events that the user was registered for"""
        now = datetime.now()
        return [event for event in StudentViewModel.get_user_registered_events(user)
                if datetime.combine(event.date, event.time) <= now]
    
    @staticmethod
    def get_ongoing_events():
        """Get all events that are currently happening"""
        now = datetime.now()
        return Event.query.filter(
            Event.start_date == now.date(),
            Event.start_time <= now.time()
        ).all()
    
    @staticmethod
    def get_today_events():
        """Get all events scheduled for today"""
        today = datetime.now().date()
        return Event.query.filter(
            Event.start_date == today
        ).order_by(Event.start_time).all()
    
    @staticmethod
    def get_dashboard_stats(user):
        """Get statistics for student dashboard"""
        registered_events = StudentViewModel.get_user_registered_events(user)
        today = datetime.now().date()
        
        stats = {
            'total_registered': len(registered_events),
            'upcoming_events': sum(1 for e in registered_events if e.start_date >= today),
            'events_this_month': sum(1 for e in registered_events if e.start_date.month == today.month),
            'categories': {}
        }
        
        # Count events by category
        for event in registered_events:
            if event.category in stats['categories']:
                stats['categories'][event.category] += 1
            else:
                stats['categories'][event.category] = 1
                
        return stats
    
    @staticmethod
    def get_events_by_category(category):
        """Get events filtered by category"""
        today = date.today()
        return Event.query.filter(
            Event.date >= today,
            Event.category == category
        ).order_by(Event.date, Event.time).all()
    
    @staticmethod
    def search_events(search_query=None, category=None, start_date=None, end_date=None):
        """Search and filter events"""
        query = Event.query
        
        # Search by title or description
        if search_query:
            search = f"%{search_query}%"
            query = query.filter(
                or_(
                    Event.title.ilike(search),
                    Event.description.ilike(search),
                    Event.location.ilike(search)
                )
            )
        
        # Filter by category
        if category and category != 'all':
            query = query.filter(Event.category == category)
            
        # Filter by date range
        if start_date:
            query = query.filter(Event.start_date >= start_date)
        if end_date:
            query = query.filter(Event.start_date <= end_date)
            
        # Order by date and time
        return query.order_by(Event.start_date, Event.start_time).all()
        return query.order_by(Event.date, Event.time).all()
    
    # Enhanced recommendation methods with debugging
    @staticmethod
    def get_user_recommendations(user, limit=5):
        """Get personalized recommendations for user with debugging"""
        try:
            print(f"Getting recommendations for user: {user.username}")
            print(f"User registered events: {[e.title for e in user.registered_events]}")
            
            recommendations = reccomendation_engine.get_user_recommendations(user, limit)
            
            print(f"Generated {len(recommendations)} recommendations:")
            for i, rec in enumerate(recommendations):
                print(f"{i+1}. {rec['event'].title} - Score: {rec['score']:.3f} - {rec['reason']}")
            
            return recommendations
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            # Fallback: return some upcoming events
            return StudentViewModel._get_fallback_recommendations(user, limit)
    
    @staticmethod
    def get_trending_events(limit=10):
        """Get trending events with debugging"""
        try:
            trending = reccomendation_engine.get_trending_events(limit)
            print(f"Generated {len(trending)} trending events")
            return trending
        except Exception as e:
            print(f"Error getting trending events: {e}")
            # Fallback: return recent events
            upcoming_events = Event.query.filter(
                Event.date >= date.today()
            ).order_by(Event.date).limit(limit).all()
            
            return [{'event': event, 'registration_count': len(event.registered_users)} 
                   for event in upcoming_events]
    
    @staticmethod
    def _get_fallback_recommendations(user, limit):
        """Fallback recommendations when main system fails"""
        # Get events user hasn't registered for
        user_event_ids = [e.id for e in user.registered_events]
        
        from sqlalchemy import not_
        
        upcoming_events = Event.query.filter(
            Event.date >= date.today(),
            not_(Event.id.in_(user_event_ids)) if user_event_ids else True
        ).order_by(Event.date).limit(limit).all()
        
        return [{
            'event': event,
            'score': 0.5,
            'reason': 'Upcoming event you might like'
        } for event in upcoming_events]