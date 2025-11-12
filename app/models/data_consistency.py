from datetime import datetime
from app import db


class DataConsistencyConfig(db.Model):
    """Model to store data consistency check configurations"""
    __tablename__ = 'data_consistency_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Source table configuration
    source_connection_id = db.Column(db.Integer, db.ForeignKey('database_connections.id'), nullable=False)
    source_table = db.Column(db.String(200), nullable=False)
    
    # Target table configuration
    target_connection_id = db.Column(db.Integer, db.ForeignKey('database_connections.id'), nullable=False)
    target_table = db.Column(db.String(200), nullable=False)
    
    # Field mappings (JSON): {"source_field": "target_field"} for join keys
    # Example: {"id": "user_id", "email": "email_address"}
    join_mappings = db.Column(db.JSON, nullable=False)
    
    # Fields to compare (JSON): [{"source_field": "nome", "target_field": "name"}, ...]
    # These are the fields that will be compared for consistency
    comparison_fields = db.Column(db.JSON, nullable=False)
    
    # User who created this config
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    source_connection = db.relationship('DatabaseConnection', foreign_keys=[source_connection_id], backref='source_consistency_configs')
    target_connection = db.relationship('DatabaseConnection', foreign_keys=[target_connection_id], backref='target_consistency_configs')
    user = db.relationship('User', backref='consistency_configs')
    consistency_checks = db.relationship('DataConsistencyCheck', backref='config', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert config to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'source_connection_id': self.source_connection_id,
            'source_table': self.source_table,
            'target_connection_id': self.target_connection_id,
            'target_table': self.target_table,
            'join_mappings': self.join_mappings or {},
            'comparison_fields': self.comparison_fields or [],
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<DataConsistencyConfig {self.name}>'


class DataConsistencyCheck(db.Model):
    """Model to store data consistency check executions"""
    __tablename__ = 'data_consistency_checks'
    
    id = db.Column(db.Integer, primary_key=True)
    config_id = db.Column(db.Integer, db.ForeignKey('data_consistency_configs.id'), nullable=False)
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='pending')  # pending, running, completed, failed
    total_inconsistencies = db.Column(db.Integer, default=0)
    check_metadata = db.Column(db.JSON)  # Additional metadata
    
    # Relationships
    results = db.relationship('DataConsistencyResult', backref='check', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert check to dictionary"""
        return {
            'id': self.id,
            'config_id': self.config_id,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'status': self.status,
            'total_inconsistencies': self.total_inconsistencies,
            'metadata': self.check_metadata
        }
    
    def __repr__(self):
        return f'<DataConsistencyCheck {self.id} - Config {self.config_id}>'


class DataConsistencyResult(db.Model):
    """Model to store individual data consistency check results"""
    __tablename__ = 'data_consistency_results'
    
    id = db.Column(db.Integer, primary_key=True)
    check_id = db.Column(db.Integer, db.ForeignKey('data_consistency_checks.id'), nullable=False)
    
    # Join key values used to match records (JSON)
    # Example: {"id": "123", "email": "user@example.com"}
    join_key_values = db.Column(db.JSON, nullable=False)
    
    # Field that has inconsistency
    field_name = db.Column(db.String(200), nullable=False)
    
    # Values found
    source_value = db.Column(db.Text)  # Value in source table
    target_value = db.Column(db.Text)  # Value in target table (can be None if record not found)
    
    # Type of inconsistency
    # "value_mismatch" - values don't match
    # "missing_in_target" - record exists in source but not in target
    # "missing_in_source" - record exists in target but not in source
    inconsistency_type = db.Column(db.String(50), nullable=False)
    
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert result to dictionary"""
        return {
            'id': self.id,
            'check_id': self.check_id,
            'join_key_values': self.join_key_values or {},
            'field_name': self.field_name,
            'source_value': self.source_value,
            'target_value': self.target_value,
            'inconsistency_type': self.inconsistency_type,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None
        }
    
    def __repr__(self):
        return f'<DataConsistencyResult {self.id} - Field {self.field_name}>'

