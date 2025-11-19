"""
Script to fix users table ID column if it's not auto-incrementing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import inspect, text

def fix_users_table():
    """Fix users table ID column to ensure auto-increment"""
    app = create_app()
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            
            # Check if users table exists
            if 'users' not in inspector.get_table_names():
                print("Table 'users' does not exist!")
                return False
            
            # Get database URI to determine database type
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            db_type = 'sqlite'
            if 'mysql' in db_uri or 'mariadb' in db_uri:
                db_type = 'mysql'
            
            print(f"Database type: {db_type}")
            
            # Get current columns
            columns = inspector.get_columns('users')
            id_column = next((c for c in columns if c['name'] == 'id'), None)
            
            if not id_column:
                print("ID column not found in users table!")
                return False
            
            print(f"Current ID column: {id_column}")
            
            # Check if autoincrement is set
            autoincrement = id_column.get('autoincrement', False)
            print(f"Autoincrement: {autoincrement}")
            
            if db_type == 'sqlite':
                # SQLite always auto-increments INTEGER PRIMARY KEY
                # But we can check if there are users without IDs
                result = db.session.execute(text("SELECT COUNT(*) FROM users WHERE id IS NULL OR id = ''"))
                count = result.scalar()
                if count > 0:
                    print(f"Found {count} users without IDs. This shouldn't happen with SQLite.")
                    # Try to fix by recreating the table
                    print("Attempting to fix by ensuring table structure is correct...")
                    db.create_all()
                    db.session.commit()
                    print("Table structure recreated.")
            elif db_type == 'mysql':
                # For MySQL/MariaDB, check if AUTO_INCREMENT is set
                result = db.session.execute(text("SHOW CREATE TABLE users"))
                create_table = result.fetchone()[1]
                print(f"Table structure: {create_table}")
                
                if 'AUTO_INCREMENT' not in create_table:
                    print("AUTO_INCREMENT not found! Attempting to add it...")
                    # Get max ID
                    result = db.session.execute(text("SELECT COALESCE(MAX(id), 0) FROM users"))
                    max_id = result.scalar()
                    next_id = max_id + 1
                    
                    # Alter table to add AUTO_INCREMENT
                    db.session.execute(text(f"ALTER TABLE users MODIFY COLUMN id INT AUTO_INCREMENT"))
                    db.session.execute(text(f"ALTER TABLE users AUTO_INCREMENT = {next_id}"))
                    db.session.commit()
                    print(f"AUTO_INCREMENT added. Next ID will be {next_id}")
                else:
                    print("AUTO_INCREMENT is already set.")
            
            # Verify fix
            result = db.session.execute(text("SELECT COUNT(*) FROM users WHERE id IS NULL OR id = ''"))
            count = result.scalar()
            if count > 0:
                print(f"WARNING: Still found {count} users without IDs!")
            else:
                print("✓ All users have valid IDs.")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            import traceback
            print(f"Error fixing users table: {str(e)}")
            print(traceback.format_exc())
            return False

if __name__ == '__main__':
    fix_users_table()

