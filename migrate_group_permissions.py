"""
Migration script to add new granular permissions to groups table
Run this script to add the new permission columns to existing databases
"""
import sys
import os
from sqlalchemy import text, inspect
from app import create_app, db
from app.models import Group

def migrate_group_permissions():
    """Add new permission columns to groups table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Get database inspector
            inspector = inspect(db.engine)
            columns = {col['name']: col for col in inspector.get_columns('groups')}
            
            # List of new permission columns to add
            new_permissions = [
                # Connections
                ('can_execute_connections', 'BOOLEAN', 'DEFAULT 0'),
                # Projects
                ('can_execute_projects', 'BOOLEAN', 'DEFAULT 0'),
                # Tables
                ('can_create_tables', 'BOOLEAN', 'DEFAULT 0'),
                ('can_execute_tables', 'BOOLEAN', 'DEFAULT 0'),
                # Users
                ('can_create_users', 'BOOLEAN', 'DEFAULT 0'),
                ('can_execute_users', 'BOOLEAN', 'DEFAULT 0'),
                # Groups
                ('can_create_groups', 'BOOLEAN', 'DEFAULT 0'),
                ('can_execute_groups', 'BOOLEAN', 'DEFAULT 0'),
                # Comparison Reports
                ('can_create_comparison_reports', 'BOOLEAN', 'DEFAULT 0'),
                ('can_execute_comparison_reports', 'BOOLEAN', 'DEFAULT 0'),
                # Consistency Reports
                ('can_create_consistency_reports', 'BOOLEAN', 'DEFAULT 0'),
                ('can_execute_consistency_reports', 'BOOLEAN', 'DEFAULT 0'),
                # Dashboard
                ('can_create_dashboard', 'BOOLEAN', 'DEFAULT 0'),
                ('can_execute_dashboard', 'BOOLEAN', 'DEFAULT 0'),
                # Comparison
                ('can_create_comparison', 'BOOLEAN', 'DEFAULT 0'),
                ('can_execute_comparison', 'BOOLEAN', 'DEFAULT 0'),
                # Scheduled Tasks
                ('can_create_scheduled_tasks', 'BOOLEAN', 'DEFAULT 0'),
                ('can_execute_scheduled_tasks', 'BOOLEAN', 'DEFAULT 0'),
                # Webhooks
                ('can_create_webhooks', 'BOOLEAN', 'DEFAULT 0'),
                ('can_execute_webhooks', 'BOOLEAN', 'DEFAULT 0'),
                # Data Consistency
                ('can_create_data_consistency', 'BOOLEAN', 'DEFAULT 0'),
                ('can_execute_data_consistency', 'BOOLEAN', 'DEFAULT 0'),
            ]
            
            # Get database type
            db_url = str(db.engine.url)
            db_type = db_url.split(':')[0] if ':' in db_url else 'sqlite'
            
            print(f"Database type: {db_type}")
            print(f"Checking groups table structure...")
            
            # Add missing columns
            with db.engine.connect() as connection:
                for col_name, col_type, default in new_permissions:
                    if col_name not in columns:
                        print(f"Adding column: {col_name}")
                        try:
                            if db_type == 'sqlite':
                                # SQLite doesn't support ALTER TABLE ADD COLUMN with DEFAULT directly
                                # We'll add it without default and update existing rows
                                alter_sql = text(f"ALTER TABLE groups ADD COLUMN {col_name} INTEGER DEFAULT 0")
                                connection.execute(alter_sql)
                                connection.commit()
                            elif db_type.startswith('mysql') or db_type.startswith('mariadb'):
                                alter_sql = text(f"ALTER TABLE groups ADD COLUMN {col_name} BOOLEAN DEFAULT 0")
                                connection.execute(alter_sql)
                                connection.commit()
                            else:
                                alter_sql = text(f"ALTER TABLE groups ADD COLUMN {col_name} {col_type} {default}")
                                connection.execute(alter_sql)
                                connection.commit()
                            print(f"  ✓ Added {col_name}")
                        except Exception as e:
                            print(f"  ✗ Error adding {col_name}: {e}")
                            connection.rollback()
                    else:
                        print(f"  Column {col_name} already exists, skipping")
            
            # Migrate existing permissions to new structure
            print("\nMigrating existing permissions...")
            groups = Group.query.all()
            for group in groups:
                updated = False
                
                # If can_create_connections exists, also grant execute
                if hasattr(group, 'can_create_connections') and group.can_create_connections:
                    if not hasattr(group, 'can_execute_connections') or not group.can_execute_connections:
                        group.can_execute_connections = True
                        updated = True
                
                # If can_create_projects exists, also grant execute
                if hasattr(group, 'can_create_projects') and group.can_create_projects:
                    if not hasattr(group, 'can_execute_projects') or not group.can_execute_projects:
                        group.can_execute_projects = True
                        updated = True
                
                # Legacy permissions migration
                if hasattr(group, 'can_view_dashboards') and group.can_view_dashboards:
                    if not hasattr(group, 'can_execute_dashboard') or not group.can_execute_dashboard:
                        group.can_execute_dashboard = True
                        updated = True
                
                if hasattr(group, 'can_view_reports') and group.can_view_reports:
                    if not hasattr(group, 'can_execute_comparison_reports') or not group.can_execute_comparison_reports:
                        group.can_execute_comparison_reports = True
                        updated = True
                
                if updated:
                    print(f"  Updated group: {group.name}")
            
            db.session.commit()
            print("\n✓ Migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            import traceback
            print(f"\n✗ Migration failed: {e}")
            print(traceback.format_exc())
            sys.exit(1)

if __name__ == '__main__':
    migrate_group_permissions()

