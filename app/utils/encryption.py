"""
Encryption utilities for database passwords
Uses Fernet symmetric encryption from cryptography library
"""
from cryptography.fernet import Fernet
import base64
import os
from flask import current_app


class PasswordEncryption:
    """Handle encryption and decryption of database passwords"""
    
    @staticmethod
    def get_encryption_key():
        """Get or generate encryption key from environment or config"""
        # Try to get from environment variable first
        key = os.environ.get('ENCRYPTION_KEY')
        key_source = 'ENV'
        
        if not key:
            # Try to get from Flask config
            try:
                key = current_app.config.get('ENCRYPTION_KEY')
                key_source = 'FLASK_CONFIG'
            except RuntimeError:
                # Not in app context, use default from env
                pass
        
        if not key:
            # Generate a new key (should be set in .env for production)
            # This is a fallback - in production, always set ENCRYPTION_KEY
            generated_key = Fernet.generate_key()
            print("=" * 60)
            print("WARNING: Generated new encryption key!")
            print("Set ENCRYPTION_KEY in .env for production!")
            print(f"Generated key: {generated_key.decode()}")
            print("=" * 60)
            return generated_key
        
        # Ensure key is bytes
        if isinstance(key, str):
            # Fernet keys are base64-encoded strings
            # Try to decode as base64 first (most common case)
            try:
                decoded = base64.urlsafe_b64decode(key.encode())
                if len(decoded) == 32:
                    print(f"DEBUG: Using ENCRYPTION_KEY from {key_source} (base64 decoded)")
                    return decoded
            except Exception as e:
                print(f"DEBUG: Key is not valid base64, trying as raw string: {e}")
            
            # If not valid base64, use as raw string and pad/truncate to 32 bytes
            key_bytes = key.encode('utf-8')
            if len(key_bytes) < 32:
                key_bytes = key_bytes.ljust(32, b'0')
            elif len(key_bytes) > 32:
                key_bytes = key_bytes[:32]
            print(f"DEBUG: Using ENCRYPTION_KEY from {key_source} (raw string, padded/truncated)")
            return key_bytes
        
        # If already bytes, ensure correct length
        if isinstance(key, bytes):
            if len(key) < 32:
                return key.ljust(32, b'0')
            elif len(key) > 32:
                return key[:32]
            return key
        
        return key
    
    @staticmethod
    def encrypt_password(password: str) -> str:
        """Encrypt a password"""
        if not password:
            return ""
        
        try:
            key = PasswordEncryption.get_encryption_key()
            # Fernet requires base64-encoded 32-byte key
            # Ensure key is bytes and exactly 32 bytes
            if isinstance(key, bytes):
                if len(key) != 32:
                    key = key[:32].ljust(32, b'0')
            else:
                key = key[:32].ljust(32, b'0')
            
            fernet_key = base64.urlsafe_b64encode(key)
            fernet = Fernet(fernet_key)
            encrypted = fernet.encrypt(password.encode())
            return encrypted.decode()
        except Exception as e:
            print(f"ERROR encrypting password: {e}")
            # Return empty string if encryption fails
            return ""
    
    @staticmethod
    def decrypt_password(encrypted_password: str) -> str:
        """Decrypt a password"""
        if not encrypted_password:
            return ""
        
        try:
            key = PasswordEncryption.get_encryption_key()
            # Fernet requires base64-encoded 32-byte key
            # Ensure key is exactly 32 bytes
            if isinstance(key, bytes):
                if len(key) != 32:
                    key = key[:32].ljust(32, b'0')
            else:
                key = key[:32].ljust(32, b'0')
            
            fernet_key = base64.urlsafe_b64encode(key)
            fernet = Fernet(fernet_key)
            decrypted = fernet.decrypt(encrypted_password.encode())
            return decrypted.decode()
        except Exception as e:
            # If decryption fails, return empty string
            # This might mean the password is already plain text
            print(f"Warning: Could not decrypt password (might be plain text): {e}")
            return ""


def encrypt_db_config(db_config: dict) -> dict:
    """Encrypt password in database configuration"""
    if not db_config:
        return db_config
    
    config = db_config.copy()
    if 'password' in config and config['password']:
        config['password'] = PasswordEncryption.encrypt_password(config['password'])
    
    return config


def decrypt_db_config(db_config: dict) -> dict:
    """Decrypt password in database configuration"""
    if not db_config:
        return db_config
    
    config = db_config.copy()
    if 'password' in config:
        password = config['password']
        
        # If password is None or empty, keep it as is
        if not password:
            return config
        
        # Try to decrypt - if it fails, assume it's already plain text
        # Fernet encrypted strings are base64 and start with specific pattern
        if isinstance(password, str) and password.startswith('gAAAAAB'):
            # Looks like encrypted password, try to decrypt
            try:
                decrypted = PasswordEncryption.decrypt_password(password)
                if decrypted and len(decrypted) > 0:
                    config['password'] = decrypted
                    print(f"DEBUG: Successfully decrypted password (length: {len(decrypted)})")
                else:
                    # Decryption returned empty, but password exists
                    # This might mean wrong key - try to use original as fallback
                    # But first, let's try to see if it's actually encrypted with a different key
                    print(f"WARNING: Decryption returned empty string for encrypted password.")
                    print(f"  This usually means the ENCRYPTION_KEY is different from when password was encrypted.")
                    print(f"  Attempting to use original password as fallback...")
                    # Don't use encrypted password - it won't work
                    # Return empty to force user to re-enter password
                    config['password'] = ''
            except Exception as e:
                print(f"ERROR decrypting password: {e}")
                print(f"  Password appears encrypted but decryption failed.")
                print(f"  Check if ENCRYPTION_KEY matches the key used when password was encrypted.")
                # Return empty password - encrypted password won't work
                config['password'] = ''
        else:
            # Password doesn't look encrypted, use as plain text
            print(f"DEBUG: Password doesn't look encrypted, using as plain text (length: {len(str(password))})")
            config['password'] = password
    
    return config

