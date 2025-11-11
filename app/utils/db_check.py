"""
Utility functions for database checks and initialization
"""
from sqlalchemy import inspect
from app import db
from app.models import User, Project, Comparison, ComparisonResult, ChangeLog, DatabaseConnection, TableModelMapping, Group
from app.models.group import user_groups


def check_tables_exist():
    """Check if all required tables exist in the database"""
    try:
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        required_tables = [
            'users',
            'projects',
            'comparisons',
            'comparison_results',
            'change_logs',
            'database_connections',
            'table_model_mappings',
            'groups',
            'user_groups'
        ]
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        return {
            'all_exist': len(missing_tables) == 0,
            'missing_tables': missing_tables,
            'existing_tables': existing_tables
        }
    except Exception as e:
        # If inspection fails, assume tables don't exist
        return {
            'all_exist': False,
            'missing_tables': ['all'],
            'existing_tables': [],
            'error': str(e)
        }


def ensure_tables_exist():
    """Ensure all required tables exist, create them if missing"""
    check_result = check_tables_exist()
    
    if not check_result['all_exist']:
        print(f"Creating missing tables: {check_result['missing_tables']}")
        try:
            db.create_all()
            db.session.commit()
            # Also create default groups if they don't exist
            from app.models.group import Group
            default_groups = [
                {
                    'name': 'Administradores',
                    'description': 'Acesso total ao sistema',
                    'can_create_connections': True,
                    'can_create_projects': True,
                    'can_view_dashboards': True,
                    'can_edit_tables': True,
                    'can_view_tables': True,
                    'can_view_reports': True,
                    'can_download_reports': True
                },
                {
                    'name': 'Criadores de Conexões',
                    'description': 'Podem criar e gerenciar conexões de banco de dados',
                    'can_create_connections': True,
                    'can_create_projects': False,
                    'can_view_dashboards': True,
                    'can_edit_tables': False,
                    'can_view_tables': True,
                    'can_view_reports': True,
                    'can_download_reports': True
                },
                {
                    'name': 'Criadores de Projetos',
                    'description': 'Podem criar e gerenciar projetos de comparação',
                    'can_create_connections': False,
                    'can_create_projects': True,
                    'can_view_dashboards': True,
                    'can_edit_tables': False,
                    'can_view_tables': True,
                    'can_view_reports': True,
                    'can_download_reports': True
                },
                {
                    'name': 'Visualizadores de Dashboard',
                    'description': 'Apenas visualização de dashboards',
                    'can_create_connections': False,
                    'can_create_projects': False,
                    'can_view_dashboards': True,
                    'can_edit_tables': False,
                    'can_view_tables': False,
                    'can_view_reports': False,
                    'can_download_reports': False
                },
                {
                    'name': 'Editores de Tabelas',
                    'description': 'Podem visualizar e editar tabelas',
                    'can_create_connections': False,
                    'can_create_projects': False,
                    'can_view_dashboards': True,
                    'can_edit_tables': True,
                    'can_view_tables': True,
                    'can_view_reports': True,
                    'can_download_reports': True
                },
                {
                    'name': 'Visualizadores de Tabelas',
                    'description': 'Apenas visualização de tabelas',
                    'can_create_connections': False,
                    'can_create_projects': False,
                    'can_view_dashboards': True,
                    'can_edit_tables': False,
                    'can_view_tables': True,
                    'can_view_reports': True,
                    'can_download_reports': False
                },
                {
                    'name': 'Visualizadores de Relatórios',
                    'description': 'Podem visualizar e baixar relatórios',
                    'can_create_connections': False,
                    'can_create_projects': False,
                    'can_view_dashboards': True,
                    'can_edit_tables': False,
                    'can_view_tables': False,
                    'can_view_reports': True,
                    'can_download_reports': True
                }
            ]
            
            for group_data in default_groups:
                group = Group.query.filter_by(name=group_data['name']).first()
                if not group:
                    group = Group(**group_data)
                    db.session.add(group)
            
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error creating tables: {str(e)}")
            db.session.rollback()
            return False
    
    return False


def is_first_run():
    """Check if this is the first run (no admin users exist)"""
    try:
        # First check if users table exists
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        table_names = inspector.get_table_names()
        
        print(f"[FIRST RUN CHECK] Tables found: {table_names}")
        
        if 'users' not in table_names:
            print("[FIRST RUN CHECK] Users table does not exist - first run")
            return True
        
        # Check if any admin users exist
        admin_users = User.query.filter_by(is_admin=True).all()
        admin_count = len(admin_users)
        result = admin_count == 0
        
        print(f"[FIRST RUN CHECK] Admin users found: {admin_count}, First run: {result}")
        
        return result
    except Exception as e:
        # If query fails, assume first run
        import traceback
        print(f"[FIRST RUN CHECK ERROR] {str(e)}")
        print(traceback.format_exc())
        return True
