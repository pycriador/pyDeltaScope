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
    
    # Permissions - Create and Execute for each functionality
    # Connections
    can_create_connections = db.Column(db.Boolean, default=False)
    can_execute_connections = db.Column(db.Boolean, default=False)
    
    # Projects
    can_create_projects = db.Column(db.Boolean, default=False)
    can_execute_projects = db.Column(db.Boolean, default=False)
    
    # Tables
    can_create_tables = db.Column(db.Boolean, default=False)
    can_execute_tables = db.Column(db.Boolean, default=False)
    
    # Users
    can_create_users = db.Column(db.Boolean, default=False)
    can_execute_users = db.Column(db.Boolean, default=False)
    
    # Groups
    can_create_groups = db.Column(db.Boolean, default=False)
    can_execute_groups = db.Column(db.Boolean, default=False)
    
    # Comparison Reports
    can_create_comparison_reports = db.Column(db.Boolean, default=False)
    can_execute_comparison_reports = db.Column(db.Boolean, default=False)
    
    # Consistency Reports
    can_create_consistency_reports = db.Column(db.Boolean, default=False)
    can_execute_consistency_reports = db.Column(db.Boolean, default=False)
    
    # Dashboard
    can_create_dashboard = db.Column(db.Boolean, default=False)
    can_execute_dashboard = db.Column(db.Boolean, default=False)
    
    # Comparison
    can_create_comparison = db.Column(db.Boolean, default=False)
    can_execute_comparison = db.Column(db.Boolean, default=False)
    
    # Scheduled Tasks
    can_create_scheduled_tasks = db.Column(db.Boolean, default=False)
    can_execute_scheduled_tasks = db.Column(db.Boolean, default=False)
    
    # Webhooks/HTTP Client
    can_create_webhooks = db.Column(db.Boolean, default=False)
    can_execute_webhooks = db.Column(db.Boolean, default=False)
    
    # Data Consistency
    can_create_data_consistency = db.Column(db.Boolean, default=False)
    can_execute_data_consistency = db.Column(db.Boolean, default=False)
    
    # Legacy permissions (kept for backward compatibility, will be deprecated)
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
            # Connections
            'can_create_connections': self.can_create_connections,
            'can_execute_connections': self.can_execute_connections,
            # Projects
            'can_create_projects': self.can_create_projects,
            'can_execute_projects': self.can_execute_projects,
            # Tables
            'can_create_tables': self.can_create_tables,
            'can_execute_tables': self.can_execute_tables,
            # Users
            'can_create_users': self.can_create_users,
            'can_execute_users': self.can_execute_users,
            # Groups
            'can_create_groups': self.can_create_groups,
            'can_execute_groups': self.can_execute_groups,
            # Comparison Reports
            'can_create_comparison_reports': self.can_create_comparison_reports,
            'can_execute_comparison_reports': self.can_execute_comparison_reports,
            # Consistency Reports
            'can_create_consistency_reports': self.can_create_consistency_reports,
            'can_execute_consistency_reports': self.can_execute_consistency_reports,
            # Dashboard
            'can_create_dashboard': self.can_create_dashboard,
            'can_execute_dashboard': self.can_execute_dashboard,
            # Comparison
            'can_create_comparison': self.can_create_comparison,
            'can_execute_comparison': self.can_execute_comparison,
            # Scheduled Tasks
            'can_create_scheduled_tasks': self.can_create_scheduled_tasks,
            'can_execute_scheduled_tasks': self.can_execute_scheduled_tasks,
            # Webhooks
            'can_create_webhooks': self.can_create_webhooks,
            'can_execute_webhooks': self.can_execute_webhooks,
            # Data Consistency
            'can_create_data_consistency': self.can_create_data_consistency,
            'can_execute_data_consistency': self.can_execute_data_consistency,
            # Legacy (backward compatibility)
            'can_view_dashboards': self.can_view_dashboards,
            'can_edit_tables': self.can_edit_tables,
            'can_view_tables': self.can_view_tables,
            'can_view_reports': self.can_view_reports,
            'can_download_reports': self.can_download_reports,
            'user_count': self.users.count()
        }
    
    def __repr__(self):
        return f'<Group {self.name}>'

