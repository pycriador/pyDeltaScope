from datetime import datetime
from app import db


class ChangeLog(db.Model):
    """Change log for incremental tracking"""
    __tablename__ = 'change_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    comparison_id = db.Column(db.Integer, db.ForeignKey('comparisons.id'), nullable=True)
    record_id = db.Column(db.String(200), nullable=False)
    field_name = db.Column(db.String(200), nullable=False)
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    change_type = db.Column(db.String(50), nullable=False)  # added, deleted, modified
    detected_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    sent_to_api = db.Column(db.Boolean, default=False)
    api_response = db.Column(db.JSON)
    sent_at = db.Column(db.DateTime)
    
    # Relationship
    project = db.relationship('Project', backref='change_logs')
    
    def to_dict(self):
        """Convert change log to dictionary"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'comparison_id': self.comparison_id,
            'record_id': self.record_id,
            'field_name': self.field_name,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'change_type': self.change_type,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None,
            'sent_to_api': self.sent_to_api,
            'api_response': self.api_response,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None
        }
    
    def __repr__(self):
        return f'<ChangeLog {self.id} - {self.field_name}>'


