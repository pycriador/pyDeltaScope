"""
Migration script to add target_record_json column to comparison_results table

Execute this script when your Flask app is running or import it in a Python shell:
    python3 -c "from scripts.migrate_add_target_record_json import migrate; from app import create_app, db; app = create_app(); app.app_context().push(); migrate(db, app.config)"
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect, text

def migrate(db, app_config):
    """Add target_record_json column to comparison_results if it doesn't exist"""
    inspector = inspect(db.engine)
    
    # Check if comparison_results table exists
    if 'comparison_results' not in inspector.get_table_names():
        print("Table 'comparison_results' does not exist. Run init_db.py first.")
        return False
    
    # Check if target_record_json column exists
    columns = [col['name'] for col in inspector.get_columns('comparison_results')]
    
    if 'target_record_json' in columns:
        print("Column 'target_record_json' already exists in 'comparison_results' table.")
        return True
    
    # Get database type
    db_uri = app_config.get('SQLALCHEMY_DATABASE_URI', '')
    db_type = 'sqlite'
    if '://' in db_uri:
        db_type = db_uri.split('://')[0].split('+')[0]  # Handle sqlite+pysqlite://
    
    try:
        print(f"Adding 'target_record_json' column to 'comparison_results' table ({db_type})...")
        
        # Use JSON type for MySQL/PostgreSQL, TEXT for SQLite
        if db_type in ('mysql', 'mariadb', 'postgresql', 'postgres'):
            if db_type in ('mysql', 'mariadb'):
                db.session.execute(text("ALTER TABLE comparison_results ADD COLUMN target_record_json JSON"))
            else:  # PostgreSQL
                db.session.execute(text("ALTER TABLE comparison_results ADD COLUMN target_record_json JSONB"))
        else:  # SQLite
            db.session.execute(text("ALTER TABLE comparison_results ADD COLUMN target_record_json TEXT"))
        
        db.session.commit()
        print("✓ Successfully added 'target_record_json' column to 'comparison_results' table.")
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
        print("   python3 -c \"from scripts.migrate_add_target_record_json import migrate; from app import create_app, db; app = create_app(); app.app_context().push(); migrate(db, app.config)\"")
        print("\nOr simply restart your Flask app - the column will be added automatically on next table creation.")

