"""
Routes for initial setup (first admin user creation)
"""
from flask import Blueprint, request, jsonify
from app.models.user import User
from app.models.group import Group
from app import db
from app.utils.db_check import is_first_run

setup_bp = Blueprint('setup', __name__)


@setup_bp.route('/check', methods=['GET'])
def check_setup():
    """Check if setup is needed (first run)"""
    try:
        needs_setup = is_first_run()
        print(f"[SETUP CHECK] needs_setup = {needs_setup}")
        
        # Log additional info for debugging
        from app.models.user import User
        try:
            total_users = User.query.count()
            admin_count = User.query.filter_by(is_admin=True).count()
            print(f"[SETUP CHECK] Total users: {total_users}, Admin users: {admin_count}")
        except:
            pass
        
        return jsonify({
            'needs_setup': bool(needs_setup)  # Ensure boolean
        }), 200
    except Exception as e:
        # If there's an error checking, assume setup is needed
        import traceback
        error_msg = str(e)
        traceback_msg = traceback.format_exc()
        print(f"[SETUP CHECK ERROR] {error_msg}")
        print(f"Traceback: {traceback_msg}")
        return jsonify({
            'needs_setup': True,
            'error': error_msg
        }), 200


@setup_bp.route('/create-admin', methods=['POST'])
def create_first_admin():
    """Create the first admin user (only works if no admin exists)"""
    if not is_first_run():
        return jsonify({'message': 'Setup already completed. Admin users exist.'}), 400
    
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing required fields: username, email, password'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    try:
        # Create admin user
        admin = User(
            username=data['username'],
            email=data['email'],
            is_admin=True,
            is_active=True
        )
        admin.set_password(data['password'])
        
        db.session.add(admin)
        db.session.commit()
        
        # Add admin to Administradores group if it exists
        admin_group = Group.query.filter_by(name='Administradores').first()
        if admin_group:
            admin_group.users.append(admin)
            db.session.commit()
        
        return jsonify({
            'message': 'Admin user created successfully',
            'user': admin.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating admin user: {str(e)}'}), 500

