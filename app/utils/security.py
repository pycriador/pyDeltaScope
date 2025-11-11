from functools import wraps
from typing import Optional
from flask import request, jsonify, current_app, session, redirect, url_for, render_template
from werkzeug.security import generate_password_hash
import secrets
from datetime import datetime, timedelta
from app.models.user import User
from app import db


def generate_token(user: User) -> str:
    """Generate authentication token for user"""
    # Simple token generation - in production, use JWT or similar
    token = secrets.token_urlsafe(32)
    # Store token hash in user model (simplified - in production use separate token table)
    return token


def verify_token(token: str) -> Optional[User]:
    """Verify authentication token"""
    # Simplified token verification - in production, use proper JWT verification
    # For now, we'll use session-based auth with Werkzeug
    return None


def token_required(f):
    """Decorator for routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer TOKEN
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        # In a real implementation, verify token here
        # For now, we'll use session-based authentication
        user_id = request.headers.get('X-User-Id')
        if not user_id:
            return jsonify({'message': 'User ID is missing'}), 401
        
        try:
            user = User.query.get(int(user_id))
            if not user or not user.is_active:
                return jsonify({'message': 'Invalid user'}), 401
        except (ValueError, TypeError):
            return jsonify({'message': 'Invalid user ID'}), 401
        
        return f(user, *args, **kwargs)
    
    return decorated


def admin_required(f):
    """Decorator for routes that require admin privileges"""
    @wraps(f)
    @token_required
    def decorated(user, *args, **kwargs):
        if not user.is_admin:
            return jsonify({'message': 'Admin privileges required'}), 403
        return f(user, *args, **kwargs)
    
    return decorated


def login_required_template(f):
    """Decorator for template routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get('user_id')
        print(f"[AUTH] login_required_template - user_id from session: {user_id}")
        
        if not user_id:
            print("[AUTH] No user_id in session, redirecting to /")
            return redirect('/')
        
        try:
            user = User.query.get(int(user_id))
            print(f"[AUTH] User found: {user.username if user else 'None'}, Active: {user.is_active if user else 'N/A'}")
            if not user or not user.is_active:
                print("[AUTH] User not found or inactive, clearing session")
                session.clear()
                return redirect('/')
        except (ValueError, TypeError) as e:
            print(f"[AUTH] Error getting user: {e}")
            session.clear()
            return redirect('/')
        
        print(f"[AUTH] Authentication successful for {user.username}")
        return f(user, *args, **kwargs)
    
    return decorated


def admin_required_template(f):
    """Decorator for template routes that require admin privileges"""
    @wraps(f)
    @login_required_template
    def decorated(user, *args, **kwargs):
        if not user or not user.is_admin:
            return render_template('error.html', message='Acesso negado. Apenas administradores podem acessar esta página.'), 403
        try:
            return f(user, *args, **kwargs)
        except Exception as e:
            import traceback
            print(f"Error in {f.__name__}: {str(e)}")
            print(traceback.format_exc())
            return render_template('error.html', message=f'Erro ao carregar página: {str(e)}'), 500
    
    return decorated

