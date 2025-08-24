# Run this script in your Flask shell or create a route to run it
# flask shell
# >>> exec(open('create_test_events.py').read())

from models.event import Event
from models.user import User
from models import db
from datetime import date, time, timedelta

def create_test_events():
    """Create test events for recommendation testing"""
    
    # Get the first admin/creator user
    creator = User.query.filter_by(role='admin').first()
    if not creator:
        print("No admin user found! Please create an admin user first.")
        return
    
    # Create events in different categories
    test_events = [
        # Technical events (similar to user's preference)
        {
            'title': 'Advanced Machine Learning Workshop',
            'description': 'Learn advanced ML techniques and neural networks',
            'category': 'Technical',
            'location': 'Tech Lab 1'
        },
        {
            'title': 'Blockchain Development Bootcamp',
            'description': 'Build your first blockchain application',
            'category': 'Technical',
            'location': 'Computer Lab'
        },
        {
            'title': 'Cloud Computing with AWS',
            'description': 'Master AWS services and cloud deployment',
            'category': 'Technical',
            'location': 'Cloud Lab'
        },
        
        # Different categories to diversify recommendations
        {
            'title': 'Photography Exhibition',
            'description': 'Annual student photography showcase',
            'category': 'Cultural',
            'location': 'Art Gallery'
        },
        {
            'title': 'Entrepreneurship Seminar',
            'description': 'Learn from successful startup founders',
            'category': 'Academic',
            'location': 'Auditorium A'
        },
        {
            'title': 'Inter-University Football Tournament',
            'description': 'Competitive football matches between universities',
            'category': 'Sports',
            'location': 'Stadium'
        },
        {
            'title': 'Career Fair 2025',
            'description': 'Meet top employers and explore career opportunities',
            'category': 'Academic',
            'location': 'Main Hall'
        },
        {
            'title': 'Music Festival',
            'description': 'Live performances by local and international artists',
            'category': 'Cultural',
            'location': 'Open Theatre'
        }
    ]
    
    created_events = []
    base_date = date.today() + timedelta(days=1)  # Start from tomorrow
    
    for i, event_data in enumerate(test_events):
        event = Event(
            title=event_data['title'],
            description=event_data['description'],
            date=base_date + timedelta(days=i*2),  # Events every 2 days
            time=time(14, 0),  # 2:00 PM
            location=event_data['location'],
            category=event_data['category'],
            max_capacity=50,
            creator_id=creator.id
        )
        
        db.session.add(event)
        created_events.append(event)
    
    try:
        db.session.commit()
        print(f"Successfully created {len(created_events)} test events!")
        
        for event in created_events:
            print(f"- {event.title} ({event.category}) on {event.date}")
            
    except Exception as e:
        db.session.rollback()
        print(f"Error creating events: {e}")

# Call the function
if __name__ == "__main__":
    create_test_events()