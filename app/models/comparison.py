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
    target_record_json = db.Column(db.JSON)  # Complete target record data as JSON for webhook namespace
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
            'target_record_json': self.target_record_json,
            'change_type': self.change_type,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None
        }
    
    def __repr__(self):
        return f'<ComparisonResult {self.id} - Field {self.field_name}>'


class ComparisonProfile(db.Model):
    """Comparison execution profile model"""
    __tablename__ = 'comparison_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Execution configuration
    primary_keys = db.Column(db.JSON, nullable=False)  # List of primary key column names
    key_mappings = db.Column(db.JSON, default={})  # Mapping from source to target column names
    ignored_columns = db.Column(db.JSON, default=[])  # List of columns to ignore during comparison
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    project = db.relationship('Project', backref='comparison_profiles')
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def to_dict(self):
        """Convert profile to dictionary"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'primary_keys': self.primary_keys or [],
            'key_mappings': self.key_mappings or {},
            'ignored_columns': self.ignored_columns or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<ComparisonProfile {self.id} - {self.name} (Project {self.project_id})>'


