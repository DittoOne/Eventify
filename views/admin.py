from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from viewmodels.admin_viewmodel import AdminViewModel
from datetime import datetime
import os
from models import db

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
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        
        # Parse end date and time
        
        time = datetime.strptime(request.form['time'], '%H:%M').time()
        
        location = request.form['location']
        category = request.form['category']
        max_capacity = int(request.form['max_capacity'])
        
        success, message = AdminViewModel.create_event(
            title, description, date, time, 
            location, category, max_capacity, current_user
        )
        
        flash(message, 'success' if success else 'error')
        
        if success:
            return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/create_event.html')

@admin_bp.route('/edit-event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    from models.event import Event
    event = Event.query.get_or_404(event_id)
    
    # Check if current admin owns this event
    if event.creator != current_user:
        flash('Access denied. You can only edit your own events.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        
        # Parse start date and time
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        time = datetime.strptime(request.form['time'], '%H:%M').time()
        
        location = request.form['location']
        category = request.form['category']
        max_capacity = int(request.form['max_capacity'])
        
        success, message = AdminViewModel.update_event(
            event_id, title, description, date, time, 
            location, category, max_capacity
        )
        
        flash(message, 'success' if success else 'error')
        
        if success:
            return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/edit_event.html', event=event)

@admin_bp.route('/delete-event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    from models.event import Event
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
    from models.event import Event
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
@admin_bp.route('/events/search')
@login_required
def search_events():
    search_query = request.args.get('q', '')
    category = request.args.get('category', 'all')
    date = request.args.get('date')
    
    # Convert date strings to date objects if provided
    if date:
        date = datetime.strptime(date, '%Y-%m-%d').date()
    
        
    events = AdminViewModel.search_events(
        search_query=search_query,
        category=category,
        date=date,
    )
    
    return render_template('search_events.html',
                      search_query=search_query,
                      events=events,
                      selected_category=category,
                      date=date,
                     #search_events='search_events',  # Add this
                     #event_detail_route='student.event_detail'
                     )