from datetime import datetime
from app import db


class Comparison(db.Model):
    """Comparison execution model"""
    __tablename__ = 'comparisons'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='pending')  # pending, running, completed, failed
    total_differences = db.Column(db.Integer, default=0)
    comparison_metadata = db.Column(db.JSON)  # Additional comparison metadata
    
    # Relationships
    results = db.relationship('ComparisonResult', backref='comparison', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert comparison to dictionary"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'status': self.status,
            'total_differences': self.total_differences,
            'metadata': self.comparison_metadata  # Keep 'metadata' key for API compatibility
        }
    
    def __repr__(self):
        return f'<Comparison {self.id} - Project {self.project_id}>'


class ComparisonResult(db.Model):
    """Individual comparison result model"""
    __tablename__ = 'comparison_results'
    
    id = db.Column(db.Integer, primary_key=True)
    comparison_id = db.Column(db.Integer, db.ForeignKey('comparisons.id'), nullable=False)
    record_id = db.Column(db.String(200))  # Primary key or identifier of the record
    field_name = db.Column(db.String(200), nullable=False)
    source_value = db.Column(db.Text)
    target_value = db.Column(db.Text)
    change_type = db.Column(db.String(50))  # added, deleted, modified
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert result to dictionary"""
        return {
            'id': self.id,
            'comparison_id': self.comparison_id,
            'record_id': self.record_id,
            'field_name': self.field_name,
            'source_value': self.source_value,
            'target_value': self.target_value,
            'change_type': self.change_type,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None
        }
    
    def __repr__(self):
        return f'<ComparisonResult {self.id} - Field {self.field_name}>'


