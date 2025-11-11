from functools import wraps
from flask import request, jsonify
from app.models.user import User


def permission_required(permission):
    """Decorator for routes that require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Get user from request (set by token_required)
            user_id = request.headers.get('X-User-Id')
            if not user_id:
                return jsonify({'message': 'User ID is missing'}), 401
            
            try:
                user = User.query.get(int(user_id))
                if not user or not user.is_active:
                    return jsonify({'message': 'Invalid user'}), 401
                
                # Check permission
                if not user.has_permission(permission):
                    return jsonify({
                        'message': f'Permission denied. Required permission: {permission}'
                    }), 403
                
                return f(user, *args, **kwargs)
            except (ValueError, TypeError):
                return jsonify({'message': 'Invalid user ID'}), 401
        
        return decorated
    return decorator

