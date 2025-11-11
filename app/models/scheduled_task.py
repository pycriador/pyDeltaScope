from datetime import datetime
from app import db


class ScheduledTask(db.Model):
    """Scheduled task model for CRON-like scheduling"""
    __tablename__ = 'scheduled_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Scheduling options
    schedule_type = db.Column(db.String(50), nullable=False)  # 'interval', 'cron', 'preset'
    # For interval: minutes between executions
    # For cron: cron expression (e.g., "0 0 * * *" for daily at midnight)
    # For preset: '15min', '1hour', '6hours', '12hours', 'daily'
    schedule_value = db.Column(db.String(200), nullable=False)
    
    # Key mappings for comparison (JSON)
    key_mappings = db.Column(db.JSON)  # {"source_col": "target_col", ...}
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_run_at = db.Column(db.DateTime)
    next_run_at = db.Column(db.DateTime)
    last_run_status = db.Column(db.String(50))  # 'success', 'failed', 'running'
    last_run_message = db.Column(db.Text)
    
    # Execution count
    total_runs = db.Column(db.Integer, default=0)
    successful_runs = db.Column(db.Integer, default=0)
    failed_runs = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', backref='scheduled_tasks')
    user = db.relationship('User', backref='scheduled_tasks')
    
    def to_dict(self):
        """Convert scheduled task to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'user_id': self.user_id,
            'schedule_type': self.schedule_type,
            'schedule_value': self.schedule_value,
            'key_mappings': self.key_mappings or {},
            'is_active': self.is_active,
            'last_run_at': self.last_run_at.isoformat() if self.last_run_at else None,
            'next_run_at': self.next_run_at.isoformat() if self.next_run_at else None,
            'last_run_status': self.last_run_status,
            'last_run_message': self.last_run_message,
            'total_runs': self.total_runs,
            'successful_runs': self.successful_runs,
            'failed_runs': self.failed_runs,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<ScheduledTask {self.name} - Project {self.project_id}>'

