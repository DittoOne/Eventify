from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from viewmodels.student_viewmodel import StudentViewModel

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.before_request
@login_required
def require_student():
    if not current_user.is_student():
        flash('Access denied. Students only.', 'error')
        return redirect(url_for('admin.dashboard'))

@student_bp.route('/dashboard')
def dashboard():
    registered_events = StudentViewModel.get_user_registered_events(current_user)
    upcoming_events = StudentViewModel.get_upcoming_events()[:5]  # Show 5 latest
    return render_template('student/dashboard.html', 
                         registered_events=registered_events,
                         upcoming_events=upcoming_events)

@student_bp.route('/events')
def events():
    upcoming_events = StudentViewModel.get_upcoming_events()
    return render_template('student/events.html', events=upcoming_events)

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