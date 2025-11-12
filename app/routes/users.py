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
    
    # Check if user already exists (with trimmed values)
    username = data['username'].strip()
    email = data['email'].strip()
    
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': f'Username "{username}" already exists'}), 400
    
    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        return jsonify({'message': f'Email "{email}" already exists'}), 400
    
    # Get password
    password = data['password']
    
    # Validate inputs
    if not username or len(username) < 1:
        return jsonify({'message': 'Username cannot be empty'}), 400
    
    if not email or len(email) < 1:
        return jsonify({'message': 'Email cannot be empty'}), 400
    
    if not password or len(password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters'}), 400
    
    user = User(
        username=username,
        email=email,
        is_admin=data.get('is_admin', False),
        is_active=data.get('is_active', True)
    )
    user.set_password(password)
    
    try:
        print(f"[CREATE USER] Starting creation - username: {username}, email: {email}")
        
        db.session.add(user)
        print(f"[CREATE USER] User added to session")
        
        try:
            db.session.flush()  # Flush to get user ID from database
            print(f"[CREATE USER] Flush successful")
        except Exception as flush_error:
            db.session.rollback()
            import traceback
            print(f"[CREATE USER] Flush failed: {flush_error}")
            print(traceback.format_exc())
            return jsonify({'message': f'Error flushing user to database: {str(flush_error)}'}), 500
        
        # Verify ID was generated
        if not user.id:
            db.session.rollback()
            print(f"[CREATE USER] ERROR: User ID was not generated after flush")
            return jsonify({'message': 'Error: User ID was not generated. Check database table structure.'}), 500
        
        # Store user data before commit
        user_id = user.id
        username = user.username
        email = user.email
        is_admin = user.is_admin
        is_active = user.is_active
        created_at = user.created_at
        updated_at = user.updated_at
        
        print(f"[CREATE USER] After flush - user: {username}, email: {email}, id: {user_id}")
        
        # Commit the transaction
        try:
            db.session.commit()
            print(f"[CREATE USER] Commit successful - user: {username}, email: {email}, id: {user_id}")
        except Exception as commit_error:
            db.session.rollback()
            import traceback
            error_msg = str(commit_error)
            traceback_msg = traceback.format_exc()
            print(f"[CREATE USER] Commit failed: {error_msg}")
            print(f"[CREATE USER] Traceback:\n{traceback_msg}")
            
            # Check for common errors
            if 'UNIQUE constraint' in error_msg or 'Duplicate entry' in error_msg:
                if 'username' in error_msg.lower():
                    return jsonify({'message': f'Username "{username}" already exists'}), 400
                elif 'email' in error_msg.lower():
                    return jsonify({'message': f'Email "{email}" already exists'}), 400
            
            return jsonify({'message': f'Error committing user to database: {error_msg}'}), 500
        
        # Verify user was saved (optional check - commit was successful)
        # Note: If commit succeeded, the user is saved. Verification is just for logging.
        try:
            # Use a direct SQL query to avoid session issues
            from sqlalchemy import text
            result = db.session.execute(text("SELECT id, username, email FROM users WHERE id = :user_id"), {"user_id": user_id})
            row = result.fetchone()
            if row:
                print(f"[CREATE USER] Verified: User saved successfully - id={row[0]}, username={row[1]}")
            else:
                print(f"[CREATE USER] WARNING: User not found immediately after commit (id={user_id}). This might be a session caching issue.")
                # Don't fail - commit was successful, so user should be saved
        except Exception as verify_error:
            import traceback
            print(f"[CREATE USER] Warning: Could not verify user after commit: {verify_error}")
            print(traceback.format_exc())
            # Continue anyway - commit was successful, so user should be saved
        
        # Return user dict using stored values
        user_dict = {
            'id': user_id,
            'username': username,
            'email': email,
            'is_admin': is_admin,
            'is_active': is_active,
            'created_at': created_at.isoformat() if created_at else None,
            'updated_at': updated_at.isoformat() if updated_at else None
        }
        
        print(f"[CREATE USER] User created successfully: {user_dict}")
        
        return jsonify({
            'message': 'User created successfully',
            'user': user_dict
        }), 201
    except Exception as e:
        db.session.rollback()
        import traceback
        error_msg = str(e)
        traceback_msg = traceback.format_exc()
        print(f"[CREATE USER ERROR] {error_msg}")
        print(f"[CREATE USER TRACEBACK] {traceback_msg}")
        return jsonify({'message': f'Error creating user: {error_msg}'}), 500


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


@users_bp.route('/<int:user_id>/toggle-admin', methods=['PUT'])
@admin_required
def toggle_user_admin(current_user, user_id):
    """Toggle user admin status (Admin only)"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Prevent admin from removing their own admin status
    if current_user.id == user_id:
        return jsonify({'message': 'Cannot remove your own admin privileges'}), 400
    
    try:
        user.is_admin = not user.is_admin
        db.session.commit()
        
        status = 'tornado admin' if user.is_admin else 'removido como admin'
        return jsonify({
            'message': f'Usuário {status} com sucesso',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao alterar status de admin: {str(e)}'}), 500

