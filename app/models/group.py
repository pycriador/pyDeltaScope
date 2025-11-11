from datetime import datetime
from app import db

# Association table for User-Group many-to-many relationship
user_groups = db.Table('user_groups',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)


class Group(db.Model):
    """Group model for permission management"""
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Permissions
    can_create_connections = db.Column(db.Boolean, default=False)
    can_create_projects = db.Column(db.Boolean, default=False)
    can_view_dashboards = db.Column(db.Boolean, default=False)
    can_edit_tables = db.Column(db.Boolean, default=False)
    can_view_tables = db.Column(db.Boolean, default=False)
    can_view_reports = db.Column(db.Boolean, default=False)
    can_download_reports = db.Column(db.Boolean, default=False)
    
    # Relationships
    users = db.relationship('User', secondary=user_groups, backref='groups', lazy='dynamic')
    
    def to_dict(self):
        """Convert group to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'can_create_connections': self.can_create_connections,
            'can_create_projects': self.can_create_projects,
            'can_view_dashboards': self.can_view_dashboards,
            'can_edit_tables': self.can_edit_tables,
            'can_view_tables': self.can_view_tables,
            'can_view_reports': self.can_view_reports,
            'can_download_reports': self.can_download_reports,
            'user_count': self.users.count()
        }
    
    def __repr__(self):
        return f'<Group {self.name}>'

