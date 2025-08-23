from models.user import User
from models import db
from flask_login import login_user, logout_user

class AuthViewModel:
    @staticmethod
    def register_user(username, email, password, role='student'):
        """Register a new user"""
        try:
            # Check if user already exists
            if User.query.filter_by(username=username).first():
                return False, "Username already exists"
            
            if User.query.filter_by(email=email).first():
                return False, "Email already exists"
            
            # Create new user
            user = User(username=username, email=email, role=role)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            return True, "User registered successfully"
        except Exception as e:
            db.session.rollback()
            return False, f"Registration failed: {str(e)}"
    
    @staticmethod
    def login_user_by_credentials(username, password, remember=False):
        """Login user with credentials"""
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            return True, user
        
        return False, None
    
    @staticmethod
    def logout_current_user():
        """Logout current user"""
        logout_user()