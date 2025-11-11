from datetime import datetime
from app import db


class DatabaseConnection(db.Model):
    """Database connection model"""
    __tablename__ = 'database_connections'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    db_type = db.Column(db.String(50), nullable=False)  # sqlite, mariadb, mysql
    db_config = db.Column(db.JSON, nullable=False)  # Encrypted database configuration
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='database_connections')
    
    def to_dict(self):
        """Convert connection to dictionary"""
        config = self.db_config.copy() if self.db_config else {}
        # Don't expose password in API response
        if 'password' in config:
            config['password'] = '***' if config['password'] else ''
        
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'db_type': self.db_type,
            'db_config': config,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }
    
    def get_decrypted_config(self):
        """Get decrypted database configuration"""
        from app.utils.encryption import decrypt_db_config
        decrypted = decrypt_db_config(self.db_config)
        
        # Debug: Log password status
        if self.db_type.lower() in ['mariadb', 'mysql']:
            original_pwd = self.db_config.get('password', '') if isinstance(self.db_config, dict) else ''
            decrypted_pwd = decrypted.get('password', '') if isinstance(decrypted, dict) else ''
            
            if original_pwd:
                is_encrypted = isinstance(original_pwd, str) and original_pwd.startswith('gAAAAAB')
                pwd_length = len(str(decrypted_pwd)) if decrypted_pwd else 0
                print(f"DEBUG Connection {self.id} ({self.name}):")
                print(f"  - Original encrypted: {is_encrypted}")
                print(f"  - Original length: {len(str(original_pwd))}")
                print(f"  - Decrypted length: {pwd_length}")
                print(f"  - Decrypted empty: {not decrypted_pwd}")
                if not decrypted_pwd and original_pwd:
                    print(f"  - WARNING: Password was lost during decryption!")
                    print(f"  - Original (first 20 chars): {str(original_pwd)[:20]}...")
        
        return decrypted
    
    def __repr__(self):
        return f'<DatabaseConnection {self.name}>'

