from datetime import datetime
from app import db
import json

class WebhookConfig(db.Model):
    """Model to store webhook configurations"""
    __tablename__ = 'webhook_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(500), nullable=False)
    method = db.Column(db.String(10), nullable=False, default='POST')  # GET, POST, PUT, PATCH, DELETE
    headers = db.Column(db.JSON)  # JSON object for custom headers
    auth_type = db.Column(db.String(50))  # 'none', 'bearer', 'basic', 'api_key'
    auth_config = db.Column(db.JSON)  # JSON object for auth configuration (passwords encrypted)
    default_payload = db.Column(db.Text)  # Default JSON payload template
    is_active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='webhook_configs')
    
    def to_dict(self):
        """Convert to dictionary, hiding sensitive auth data"""
        auth_config = self.auth_config.copy() if self.auth_config else {}
        
        # Hide passwords/tokens in API response
        if self.auth_type == 'bearer' and 'token' in auth_config:
            auth_config['token'] = '***' if auth_config['token'] else ''
        elif self.auth_type == 'basic':
            if 'username' in auth_config:
                auth_config['username'] = auth_config['username'] if auth_config['username'] else ''
            if 'password' in auth_config:
                auth_config['password'] = '***' if auth_config['password'] else ''
        elif self.auth_type == 'api_key' and 'key_value' in auth_config:
            auth_config['key_value'] = '***' if auth_config['key_value'] else ''
        
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'method': self.method,
            'headers': self.headers or {},
            'auth_type': self.auth_type or 'none',
            'auth_config': auth_config,
            'default_payload': self.default_payload or '',
            'is_active': self.is_active,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_dict_with_credentials(self):
        """Convert to dictionary with decrypted credentials (for owner only)"""
        auth_config = self.get_decrypted_auth_config()
        
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'method': self.method,
            'headers': self.headers or {},
            'auth_type': self.auth_type or 'none',
            'auth_config': auth_config,
            'default_payload': self.default_payload or '',
            'is_active': self.is_active,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_decrypted_auth_config(self):
        """Get decrypted authentication configuration"""
        from app.utils.encryption import PasswordEncryption
        
        if not self.auth_config:
            return {}
        
        auth_config = self.auth_config.copy()
        
        # Decrypt passwords based on auth type
        if self.auth_type == 'bearer' and 'token' in auth_config:
            token = auth_config.get('token', '')
            if token and token != '***':
                # Try to decrypt if encrypted
                if isinstance(token, str) and token.startswith('gAAAAAB'):
                    try:
                        auth_config['token'] = PasswordEncryption.decrypt_password(token)
                    except:
                        pass  # Keep original if decryption fails
        elif self.auth_type == 'basic':
            password = auth_config.get('password', '')
            if password and password != '***':
                # Try to decrypt if encrypted
                if isinstance(password, str) and password.startswith('gAAAAAB'):
                    try:
                        auth_config['password'] = PasswordEncryption.decrypt_password(password)
                    except:
                        pass  # Keep original if decryption fails
        elif self.auth_type == 'api_key':
            key_value = auth_config.get('key_value', '')
            if key_value and key_value != '***':
                # Try to decrypt if encrypted
                if isinstance(key_value, str) and key_value.startswith('gAAAAAB'):
                    try:
                        auth_config['key_value'] = PasswordEncryption.decrypt_password(key_value)
                    except:
                        pass  # Keep original if decryption fails
        
        return auth_config
    
    def __repr__(self):
        return f'<WebhookConfig {self.name} ({self.method} {self.url})>'


class WebhookPayload(db.Model):
    """Model to store webhook payload templates"""
    __tablename__ = 'webhook_payloads'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    payload_template = db.Column(db.Text, nullable=False)  # JSON template with placeholders
    payload_example = db.Column(db.Text)  # Example JSON filled with sample data
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='webhook_payloads')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'payload_template': self.payload_template,
            'payload_example': self.payload_example,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<WebhookPayload {self.name}>'


class WebhookParams(db.Model):
    """Model to store webhook query parameters templates"""
    __tablename__ = 'webhook_params'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    params_template = db.Column(db.Text, nullable=False)  # JSON template with placeholders (key-value pairs)
    params_example = db.Column(db.Text)  # Example JSON filled with sample data
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='webhook_params')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'params_template': self.params_template,
            'params_example': self.params_example,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<WebhookParams {self.name}>'

