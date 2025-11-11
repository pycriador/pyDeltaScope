"""
Script to initialize the database
Run this script to create all tables in the database
"""
from app import create_app, db
from app.models import User, Project, Comparison, ComparisonResult, ChangeLog, DatabaseConnection, TableModelMapping, Group, WebhookConfig, WebhookPayload
import os

app = create_app(os.getenv('FLASK_ENV', 'default'))

with app.app_context():
    print("Creating database tables...")
    db.create_all()
    print("Database tables created successfully!")
    
    # Create default groups
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
        },
        {
            'name': 'Usuários Básicos',
            'description': 'Usuários com acesso limitado - apenas visualização da tela inicial',
            'can_create_connections': False,
            'can_create_projects': False,
            'can_view_dashboards': False,
            'can_edit_tables': False,
            'can_view_tables': False,
            'can_view_reports': False,
            'can_download_reports': False
        },
        {
            'name': 'Gerenciadores de Webhooks',
            'description': 'Podem gerenciar webhooks e enviar requisições HTTP para servidores externos',
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
            print(f"Created group: {group_data['name']}")
        else:
            print(f"Group already exists: {group_data['name']}")
    
    db.session.commit()
    print("\nDefault groups created successfully!")
    
    # Check if any admin exists
    admin_users = User.query.filter_by(is_admin=True).all()
    if len(admin_users) == 0:
        print("\n" + "="*60)
        print("ATENÇÃO: Nenhum usuário administrador encontrado!")
        print("="*60)
        print("Execute o sistema e crie o primeiro administrador através da interface web.")
        print("Ou use o script change_password.py para criar um usuário admin:")
        print("  python change_password.py <username> <password> --create-admin")
        print("="*60)
    else:
        print(f"\n{len(admin_users)} usuário(s) administrador(es) encontrado(s).")


