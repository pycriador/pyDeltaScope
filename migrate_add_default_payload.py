"""
Migration script to add default_payload column to webhook_configs table

Execute this script when your Flask app is running or import it in a Python shell:
    python3 -c "from migrate_add_default_payload import migrate; from app import create_app; app = create_app(); app.app_context().push(); migrate()"
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import inspect, text

def migrate(db, app_config):
    """Add default_payload column to webhook_configs if it doesn't exist"""
    inspector = inspect(db.engine)
    
    # Check if webhook_configs table exists
    if 'webhook_configs' not in inspector.get_table_names():
        print("Table 'webhook_configs' does not exist. Run init_db.py first.")
        return False
    
    # Check if default_payload column exists
    columns = [col['name'] for col in inspector.get_columns('webhook_configs')]
    
    if 'default_payload' in columns:
        print("Column 'default_payload' already exists in 'webhook_configs' table.")
        return True
    
    # Get database type
    db_uri = app_config.get('SQLALCHEMY_DATABASE_URI', '')
    db_type = 'sqlite'
    if '://' in db_uri:
        db_type = db_uri.split('://')[0]
    
    try:
        print(f"Adding 'default_payload' column to 'webhook_configs' table ({db_type})...")
        db.session.execute(text("ALTER TABLE webhook_configs ADD COLUMN default_payload TEXT"))
        db.session.commit()
        print("✓ Successfully added 'default_payload' column to 'webhook_configs' table.")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error adding column: {str(e)}")
        print("Note: If you're using SQLite and the table already has data, you may need to recreate it.")
        print("For development, you can delete the database and run: python3 init_db.py")
        return False

if __name__ == '__main__':
    try:
        from app import create_app, db
        app = create_app()
        with app.app_context():
            migrate(db, app.config)
    except ImportError as e:
        print(f"Error importing Flask app: {e}")
        print("\nTo run this migration:")
        print("1. Start your Flask app")
        print("2. In another terminal, run:")
        print("   python3 -c \"from migrate_add_default_payload import migrate; from app import create_app, db; app = create_app(); app.app_context().push(); migrate(db, app.config)\"")
        print("\nOr simply restart your Flask app - the column will be added automatically on next table creation.")

