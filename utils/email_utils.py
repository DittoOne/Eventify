from flask_mail import Message
from extensions import mail

def send_event_registration_email(to_email, event):
    """
    Send registration confirmation email with event details
    """
    subject = f"Registration Confirmed: {event.title}"
    body = f"""
    Hi,

    You have successfully registered for the event: {event.title}

    Event Details:
    Start Date: {event.start_date.strftime('%B %d, %Y')}, {event.start_time.strftime('%I:%M %p')}
    End Date: {event.end_date.strftime('%B %d, %Y')}, {event.end_time.strftime('%I:%M %p')}
    Location: {event.location}
    Category: {event.category}
    Description: {event.description}

    Thank you for registering!
    """

    msg = Message(subject=subject, recipients=[to_email], body=body)
    mail.send(msg)
