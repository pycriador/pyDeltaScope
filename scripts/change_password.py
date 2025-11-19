#!/usr/bin/env python3
"""
CLI script to change user password or create admin user
Usage: 
    python change_password.py <username> <new_password> [--create-admin]
    
Examples:
    # Change password for existing user
    python change_password.py admin newpassword123
    
    # Create new admin user (non-interactive)
    python change_password.py admin newpassword123 --create-admin
    
Note: For interactive admin creation, use: python create_admin.py
"""
import sys
import os
from app import create_app, db
from app.models.user import User

def change_password(username, new_password, create_admin=False):
    """Change password for a user or create admin user"""
    app = create_app(os.getenv('FLASK_ENV', 'default'))
    
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if create_admin:
            if user:
                print(f"Error: User '{username}' already exists.")
                sys.exit(1)
            
            # Create new admin user
            try:
                user = User(
                    username=username,
                    email=f"{username}@deltascope.local",
                    is_admin=True,
                    is_active=True
                )
                user.set_password(new_password)
                db.session.add(user)
                db.session.commit()
                print(f"Admin user '{username}' created successfully!")
                print(f"  Username: {username}")
                print(f"  Email: {user.email}")
                print(f"  Is Admin: True")
            except Exception as e:
                db.session.rollback()
                print(f"Error creating admin user: {str(e)}")
                sys.exit(1)
        else:
            if not user:
                print(f"Error: User '{username}' not found.")
                print("Use --create-admin flag to create a new admin user.")
                sys.exit(1)
            
            try:
                user.set_password(new_password)
                db.session.commit()
                print(f"Password changed successfully for user '{username}'")
            except Exception as e:
                db.session.rollback()
                print(f"Error changing password: {str(e)}")
                sys.exit(1)

if __name__ == '__main__':
    create_admin = '--create-admin' in sys.argv
    
    if create_admin:
        sys.argv.remove('--create-admin')
    
    if len(sys.argv) != 3:
        print("Usage: python change_password.py <username> <new_password> [--create-admin]")
        print("\nExamples:")
        print("  # Change password for existing user")
        print("  python change_password.py admin newpassword123")
        print("\n  # Create new admin user")
        print("  python change_password.py admin newpassword123 --create-admin")
        sys.exit(1)
    
    username = sys.argv[1]
    new_password = sys.argv[2]
    
    if len(new_password) < 6:
        print("Error: Password must be at least 6 characters long.")
        sys.exit(1)
    
    change_password(username, new_password, create_admin)
