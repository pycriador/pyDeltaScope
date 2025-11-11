from flask import Blueprint, request, jsonify
from app.models.user import User
from app import db
from app.utils.security import admin_required

users_bp = Blueprint('users', __name__)


@users_bp.route('/', methods=['GET'])
@admin_required
def list_users(current_user):
    """List all users (Admin only)"""
    try:
        users = User.query.all()
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error listing users: {str(e)}'}), 500


@users_bp.route('/', methods=['POST'])
@admin_required
def create_user(current_user):
    """Create a new user (Admin only)"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing required fields: username, email, password'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        is_admin=data.get('is_admin', False),
        is_active=data.get('is_active', True)
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating user: {str(e)}'}), 500


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(current_user, user_id):
    """Delete a user (Admin only) - Removes user from all groups before deletion"""
    # Prevent admin from deleting themselves
    if current_user.id == user_id:
        return jsonify({'message': 'Cannot delete your own account'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    try:
        # Remove user from all groups before deletion
        # Use the backref relationship to get all groups
        groups_list = list(user.groups)
        
        # Remove user from each group
        for group in groups_list:
            # Access the relationship collection and remove user
            group.users.remove(user)
        
        # Flush to ensure group removals are processed before deleting user
        db.session.flush()
        
        # Now delete the user
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully and removed from all groups'}), 200
    except Exception as e:
        db.session.rollback()
        import traceback
        error_msg = str(e)
        traceback_msg = traceback.format_exc()
        print(f"Error deleting user: {error_msg}")
        print(f"Traceback: {traceback_msg}")
        return jsonify({'message': f'Error deleting user: {error_msg}'}), 500


@users_bp.route('/<int:user_id>/password', methods=['PUT'])
@admin_required
def change_password(current_user, user_id):
    """Change user password (Admin only)"""
    data = request.get_json()
    
    if not data or not data.get('password'):
        return jsonify({'message': 'Password is required'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    try:
        user.set_password(data['password'])
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error changing password: {str(e)}'}), 500


@users_bp.route('/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(current_user, user_id):
    """Update user (Admin only)"""
    data = request.get_json()
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Prevent admin from removing their own admin status
    if current_user.id == user_id and 'is_admin' in data and not data['is_admin']:
        return jsonify({'message': 'Cannot remove your own admin privileges'}), 400
    
    # Prevent admin from deactivating themselves
    if current_user.id == user_id and 'is_active' in data and not data['is_active']:
        return jsonify({'message': 'Cannot deactivate your own account'}), 400
    
    try:
        if 'username' in data:
            # Check if username already exists (excluding current user)
            existing = User.query.filter_by(username=data['username']).first()
            if existing and existing.id != user_id:
                return jsonify({'message': 'Username already exists'}), 400
            user.username = data['username']
        
        if 'email' in data:
            # Check if email already exists (excluding current user)
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user_id:
                return jsonify({'message': 'Email already exists'}), 400
            user.email = data['email']
        
        if 'is_admin' in data:
            user.is_admin = data['is_admin']
        
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating user: {str(e)}'}), 500


@users_bp.route('/<int:user_id>/toggle-active', methods=['PUT'])
@admin_required
def toggle_user_active(current_user, user_id):
    """Toggle user active status (Admin only)"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Prevent admin from deactivating themselves
    if current_user.id == user_id:
        return jsonify({'message': 'Cannot deactivate your own account'}), 400
    
    try:
        user.is_active = not user.is_active
        db.session.commit()
        
        status = 'activated' if user.is_active else 'deactivated'
        return jsonify({
            'message': f'User {status} successfully',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error toggling user status: {str(e)}'}), 500

