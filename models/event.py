from datetime import datetime
from . import db

# Association table for many-to-many relationship
event_registrations = db.Table('event_registrations',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('events.id'), primary_key=True),
    db.Column('registered_at', db.DateTime, default=datetime.utcnow)
)

class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    max_capacity = db.Column(db.Integer, default=100)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[creator_id], back_populates='created_events')
    registered_users = db.relationship('User', secondary=event_registrations, back_populates='registered_events')
    
    @property
    def registration_count(self):
        return len(self.registered_users)
    
    @property
    def is_full(self):
        return self.registration_count >= self.max_capacity
    
    @property
    def is_past(self):
        from datetime import datetime, date
        event_datetime = datetime.combine(self.date, self.time)
        return event_datetime < datetime.now()