from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from viewmodels.admin_viewmodel import AdminViewModel
from datetime import datetime
import os
from models import db
from models.event import Event

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def require_admin():
    if not current_user.is_admin():
        flash('Access denied. Admins only.', 'error')
        return redirect(url_for('student.dashboard'))

@admin_bp.route('/dashboard')
def dashboard():
    events = AdminViewModel.get_admin_events(current_user)
    stats = AdminViewModel.get_admin_stats(current_user)
    return render_template('admin/dashboard.html', events=events, stats=stats)

@admin_bp.route('/create-event', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        
        # Parse start date and time
        start_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        start_time = datetime.strptime(request.form['time'], '%H:%M').time()
        
        # Parse end date and time
        end_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        end_time = datetime.strptime(request.form['time'], '%H:%M').time()
        
        location = request.form['location']
        category = request.form['category']
        max_capacity = int(request.form['max_capacity'])
        
        success, message = AdminViewModel.create_event(
            title, description, start_date, start_time,
            location, category, max_capacity, current_user
        )
        
        flash(message, 'success' if success else 'error')
        
        if success:
            return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/create_event.html')

@admin_bp.route('/edit-event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if current admin owns this event
    if event.creator != current_user:
        flash('Access denied. You can only edit your own events.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        
        # Parse start date and time
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        start_time = datetime.strptime(request.form['start_time'], '%H:%M').time()
        
        # Parse end date and time
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        end_time = datetime.strptime(request.form['end_time'], '%H:%M').time()
        
        location = request.form['location']
        category = request.form['category']
        max_capacity = int(request.form['max_capacity'])
        
        success, message = AdminViewModel.update_event(
            event_id, title, description, start_date, start_time, 
            location, category, max_capacity
        )
        
        flash(message, 'success' if success else 'error')
        
        if success:
            return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/edit_event.html', event=event)

@admin_bp.route('/delete-event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if current admin owns this event
    if event.creator != current_user:
        flash('Access denied. You can only delete your own events.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    success, message = AdminViewModel.delete_event(event_id)
    flash(message, 'success' if success else 'error')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/event-attendees/<int:event_id>')
def event_attendees(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if current admin owns this event
    if event.creator != current_user:
        flash('Access denied. You can only view attendees for your own events.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    attendees = AdminViewModel.get_event_attendees(event_id)
    return render_template('admin/event_attendees.html', event=event, attendees=attendees)

@admin_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Handle profile updates
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
        return redirect(url_for('admin.profile'))

    return render_template('admin/profile.html', user=current_user)

@admin_bp.route('/search')
def search_events():
    search_query = request.args.get('q', '')
    selected_category = request.args.get('category', 'all')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    location = request.args.get('location')
    time = request.args.get('time')

    # Start with base query
    query = Event.query

    # Apply filters
    if search_query:
        query = query.filter(Event.title.ilike(f'%{search_query}%'))
    if selected_category != 'all':
        query = query.filter(Event.category == selected_category)
    if start_date:
        query = query.filter(Event.date >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Event.date <= datetime.strptime(end_date, '%Y-%m-%d'))
    if location:
        query = query.filter(Event.location.ilike(f'%{location}%'))
    if time:
        query = query.filter(Event.time.ilike(f'%{time}%'))

    events = query.order_by(Event.date.desc()).all()

    return render_template('search_events.html',
                         events=events,
                         search_query=search_query,
                         selected_category=selected_category,
                         start_date=start_date,
                         end_date=end_date,
                         location=location,
                         time=time,
                         user_type='admin')

@admin_bp.route('/event/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('admin/event_detail.html', event=event)