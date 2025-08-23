from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from viewmodels.admin_viewmodel import AdminViewModel
from datetime import datetime

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
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        start_date_str = request.form.get('start_date', '')
        end_date_str = request.form.get('end_date', '')
        start_time_str = request.form.get('start_time', '')
        end_time_str = request.form.get('end_time', '')
        location = request.form.get('location', '')
        category = request.form.get('category', '')
        max_capacity = request.form.get('max_capacity', '0')
        
        # Validate required fields
        if not (title and description and start_date_str and end_date_str and start_time_str and end_time_str and location and category and max_capacity):
            flash('All fields are required.', 'error')
            return render_template('admin/create_event.html', event=request.form)

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()
        max_capacity = int(max_capacity)

        success, message = AdminViewModel.create_event(
            title, description, start_date, start_time, 
            end_date, end_time, location, category, max_capacity, current_user
        )

        flash(message, 'success' if success else 'error')

        if success:
            return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/create_event.html',event={})

@admin_bp.route('/edit-event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    from models.event import Event
    event = Event.query.get_or_404(event_id)
    
    # Check if current admin owns this event
    if event.creator != current_user:
        flash('Access denied. You can only edit your own events.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        start_date_str = request.form.get('start_date', '')
        end_date_str = request.form.get('end_date', '')
        start_time_str = request.form.get('start_time', '')
        end_time_str = request.form.get('end_time', '')
        location = request.form.get('location', '')
        category = request.form.get('category', '')
        max_capacity = request.form.get('max_capacity', '0')

        # Validate required fields
        if not (title and description and start_date_str and end_date_str and start_time_str and end_time_str and location and category and max_capacity):
            flash('All fields are required.', 'error')
            return render_template('admin/create_event.html', event=request.form)

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()
        max_capacity = int(max_capacity)
        
        success, message = AdminViewModel.update_event(
            title,description, start_date, start_time,end_date,
            end_time, location, category, max_capacity, current_user
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