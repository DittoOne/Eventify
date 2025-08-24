from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from viewmodels.student_viewmodel import StudentViewModel
from datetime import date, datetime
from werkzeug.utils import secure_filename
import os
from models import db

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.before_request
@login_required
def require_student():
    if not current_user.is_student():
        flash('Access denied. Students only.', 'error')
        return redirect(url_for('admin.dashboard'))

@student_bp.route('/dashboard')
@login_required
def dashboard():
    registered_events = StudentViewModel.get_user_upcoming_registered_events(current_user)
    upcoming_events = StudentViewModel.get_upcoming_events()[:6]  # Show 6 latest
    ongoing_events = StudentViewModel.get_ongoing_events()
    today_events = StudentViewModel.get_today_events()
    stats = StudentViewModel.get_dashboard_stats(current_user)
    
    return render_template('student/dashboard.html', 
                         registered_events=registered_events,
                         upcoming_events=upcoming_events,
                         ongoing_events=ongoing_events,
                         today_events=today_events,
                         stats=stats)

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
            if file.filename != '':
                filename = secure_filename(file.filename)
                upload_folder = os.path.join(current_app.root_path, 'static/uploads')
                os.makedirs(upload_folder, exist_ok=True)
                file.save(os.path.join(upload_folder, filename))
                current_user.profile_image = f'/static/uploads/{filename}'

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
    location = request.args.get('location', '')  # নতুন
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
                          location=location,      # নতুন
                          time=time,             # নতুন
                          user_type='student')