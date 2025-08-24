from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from viewmodels.admin_viewmodel import AdminViewModel
from datetime import datetime
import os
from models import db
from models.event import Event
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import json

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
        image_files = request.files.getlist('images')
        doc_files = request.files.getlist('documents')

        image_paths = save_files(image_files, 'images')
        document_paths = save_files(doc_files, 'docs')
        
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
            end_date, end_time, location, category, max_capacity, current_user,
            image_paths,document_paths
        )

        flash(message, 'success' if success else 'error')

        if success:
            return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/create_event.html',event={})

@admin_bp.route('/edit-event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if current admin owns this event
    if event.creator != current_user:
        flash('Access denied. You can only edit your own events.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        # Basic event info
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
            return render_template('admin/edit_event.html', event=event)

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()
        max_capacity = int(max_capacity)

        # Handle files to remove
        delete_images = request.form.getlist('remove_images')
        delete_docs = request.form.getlist('remove_docs')

        new_images_add=request.form.getlist('new_images')
        

        for img in delete_images:
            img_path = os.path.join(current_app.root_path, 'static', 'uploads', 'events', img)
            if os.path.exists(img_path):
                os.remove(img_path)
            if img in event.images:
                event.images.remove(img)

        for doc in delete_docs:
            doc_path = os.path.join(current_app.root_path, 'static', 'uploads', 'events', doc)
            if os.path.exists(doc_path):
                os.remove(doc_path)
            if doc in event.documents:
                event.documents.remove(doc)

        for img in event.images:
            print("Remaining image:", img)
        
        


        # Handle new uploads
        new_images = request.files.getlist('new_images')
        new_docs = request.files.getlist('new_documents')
        new_image_paths = save_files(new_images, 'images')
        new_doc_paths = save_files(new_docs, 'docs')

        # Append new files to existing ones
        if new_image_paths:
            event.images.extend(new_image_paths)
        if new_doc_paths:
            event.documents.extend(new_doc_paths)

        # Update the rest of the event
        success, message = AdminViewModel.update_event(
            event_id=event.id,
            title=title,
            description=description,
            start_date=start_date,
            start_time=start_time,
            end_date=end_date,
            end_time=end_time,
            location=location,
            category=category,
            max_capacity=max_capacity,
            images=event.images,
            documents=event.documents
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
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                file.save(os.path.join(upload_folder, filename))
                # Save only the relative path for use with url_for('static', ...)
                current_user.profile_image = f'uploads/{filename}'

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
        query = query.filter(Event.start_date >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Event.end_date <= datetime.strptime(end_date, '%Y-%m-%d'))
    if location:
        query = query.filter(Event.location.ilike(f'%{location}%'))
    if time:
        query = query.filter(Event.start_time.ilike(f'%{time}%'))

    events = query.order_by(Event.start_date.desc()).all()

    return render_template('search_events.html',
                         events=events,
                         search_query=search_query,
                         selected_category=selected_category,
                         start_date=start_date,
                         end_date=end_date,
                         location=location,
                         start_time=time,
                         user_type='admin')

@admin_bp.route('/event/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('admin/event_detail.html', event=event)

# utils/file_utils.py
def save_files(files, folder):
    saved_paths = []
    upload_folder = os.path.join('static', 'uploads', 'events', folder)
    os.makedirs(upload_folder, exist_ok=True)

    for file in files:
        if file.filename == '':
            continue
        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        # Save relative path with forward slashes
        relative_path = f"{folder}/{filename}".replace("\\", "/")
        saved_paths.append(relative_path)

    return saved_paths
