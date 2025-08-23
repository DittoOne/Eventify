from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from viewmodels.auth_viewmodel import AuthViewModel

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard' if current_user.is_student() else 'admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = bool(request.form.get('remember'))
        
        success, user = AuthViewModel.login_user_by_credentials(username, password, remember)
        
        if success:
            if user.is_student():
                return redirect(url_for('student.dashboard'))
            else:
                return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard' if current_user.is_student() else 'admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        success, message = AuthViewModel.register_user(username, email, password, role)
        
        if success:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    AuthViewModel.logout_current_user()
    return redirect(url_for('auth.login'))