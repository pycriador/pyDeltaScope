from datetime import datetime
from app import db


class Project(db.Model):
    """Project model"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    source_table = db.Column(db.String(200), nullable=False)
    target_table = db.Column(db.String(200), nullable=False)
    source_connection_id = db.Column(db.Integer, db.ForeignKey('database_connections.id'), nullable=False)
    target_connection_id = db.Column(db.Integer, db.ForeignKey('database_connections.id'), nullable=False)
    model_file_path = db.Column(db.String(500))  # Path to generated model file
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    source_connection = db.relationship('DatabaseConnection', foreign_keys=[source_connection_id], backref='source_projects')
    target_connection = db.relationship('DatabaseConnection', foreign_keys=[target_connection_id], backref='target_projects')
    
    # Relationships
    comparisons = db.relationship('Comparison', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert project to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'source_table': self.source_table,
            'target_table': self.target_table,
            'source_connection_id': self.source_connection_id,
            'target_connection_id': self.target_connection_id,
            'source_connection': self.source_connection.to_dict() if self.source_connection else None,
            'target_connection': self.target_connection.to_dict() if self.target_connection else None,
            'model_file_path': self.model_file_path,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<Project {self.name}>'


