from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationships
    projects = db.relationship('Project', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    
    def has_permission(self, permission):
        """Check if user has a specific permission through their groups or admin status"""
        # Admin has all permissions
        if self.is_admin:
            return True
        
        # Check if any of user's groups have the permission
        # Handle both dynamic query and list
        groups = self.groups.all() if hasattr(self.groups, 'all') else self.groups
        for group in groups:
            if hasattr(group, permission) and getattr(group, permission):
                return True
        
        return False
    
    def get_all_permissions(self):
        """Get all permissions for the user"""
        permissions = {
            'can_create_connections': False,
            'can_create_projects': False,
            'can_view_dashboards': False,
            'can_edit_tables': False,
            'can_view_tables': False,
            'can_view_reports': False,
            'can_download_reports': False
        }
        
        # Admin has all permissions
        if self.is_admin:
            return {k: True for k in permissions.keys()}
        
        # Check groups
        # Handle both dynamic query and list
        groups = self.groups.all() if hasattr(self.groups, 'all') else self.groups
        for group in groups:
            for perm in permissions.keys():
                if hasattr(group, perm) and getattr(group, perm):
                    permissions[perm] = True
        
        return permissions
    
    def set_password(self, password):
        """Set password hash"""
        if not password:
            raise ValueError("Password cannot be empty")
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        if not self.password_hash:
            return False
        if not password:
            return False
        try:
            return check_password_hash(self.password_hash, password)
        except Exception as e:
            print(f"[PASSWORD CHECK ERROR] {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'is_admin': self.is_admin
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


