from flask import Blueprint, request, jsonify, session
from app.models.user import User
from app import db
from app.utils.security import generate_token

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        
        token = generate_token(user)
        session['user_id'] = user.id
        session['token'] = token
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict(),
            'token': token
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating user: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username and password required'}), 400
    
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    print(f"[LOGIN] Attempting login for username: '{username}'")
    print(f"[LOGIN] Password length: {len(password)}")
    
    if not username or not password:
        print(f"[LOGIN] Missing username or password")
        return jsonify({'message': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user:
        print(f"[LOGIN] User '{username}' not found")
        # List all usernames for debugging
        all_users = User.query.all()
        print(f"[LOGIN] Available users: {[u.username for u in all_users]}")
        return jsonify({'message': 'Invalid credentials'}), 401
    
    print(f"[LOGIN] User found: {user.username}, ID: {user.id}, Active: {user.is_active}, Admin: {user.is_admin}")
    print(f"[LOGIN] Password hash exists: {bool(user.password_hash)}")
    print(f"[LOGIN] Password hash length: {len(user.password_hash) if user.password_hash else 0}")
    print(f"[LOGIN] Password hash starts with: {user.password_hash[:20] if user.password_hash else 'None'}")
    
    # Try password check
    try:
        password_check = user.check_password(password)
        print(f"[LOGIN] Password check result: {password_check}")
        
        # If password check fails, try with stripped password
        if not password_check:
            password_stripped = password.strip()
            if password_stripped != password:
                print(f"[LOGIN] Trying with stripped password...")
                password_check = user.check_password(password_stripped)
                print(f"[LOGIN] Password check with stripped password: {password_check}")
    except Exception as e:
        print(f"[LOGIN] Error during password check: {str(e)}")
        import traceback
        print(traceback.format_exc())
        password_check = False
    
    if not password_check:
        print(f"[LOGIN] Password verification failed for user '{username}'")
        return jsonify({'message': 'Invalid credentials'}), 401
    
    if not user.is_active:
        print(f"[LOGIN] User '{username}' is inactive")
        return jsonify({'message': 'User account is inactive'}), 403
    
    token = generate_token(user)
    session['user_id'] = user.id
    session['token'] = token
    
    print(f"[LOGIN] Login successful for user '{username}'")
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'token': token
    }), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current authenticated user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'Not authenticated'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200


