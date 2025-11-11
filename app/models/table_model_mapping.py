from datetime import datetime
from app import db


class TableModelMapping(db.Model):
    """Model to store mapping between database tables and SQLAlchemy model files"""
    __tablename__ = 'table_model_mappings'
    
    id = db.Column(db.Integer, primary_key=True)
    connection_id = db.Column(db.Integer, db.ForeignKey('database_connections.id'), nullable=False)
    table_name = db.Column(db.String(200), nullable=False)
    model_file_path = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    connection = db.relationship('DatabaseConnection', backref='table_mappings')
    
    # Unique constraint: one model file per table per connection
    __table_args__ = (db.UniqueConstraint('connection_id', 'table_name', name='_connection_table_uc'),)
    
    def to_dict(self):
        """Convert mapping to dictionary"""
        return {
            'id': self.id,
            'connection_id': self.connection_id,
            'table_name': self.table_name,
            'model_file_path': self.model_file_path,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<TableModelMapping {self.table_name} -> {self.model_file_path}>'

