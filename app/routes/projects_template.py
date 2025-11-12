from flask import Blueprint, render_template, request, redirect, url_for, session
from app.models.project import Project
from app.models.database_connection import DatabaseConnection
from app.models.data_consistency import DataConsistencyConfig
from app.utils.security import login_required_template, has_any_permission, get_users_with_execute_permission
from sqlalchemy import or_

projects_template_bp = Blueprint('projects_template', __name__)


@projects_template_bp.route('/projetos')
@login_required_template
def projects_page(current_user):
    """Render projects management page - requires execute permission"""
    from app.utils.security import generate_token
    
    # Check if user can execute projects (view/list)
    if not has_any_permission(current_user, 'projects'):
        from flask import render_template as rt
        return rt('unauthorized.html', message='Você não tem permissão para visualizar projetos. Entre em contato com um administrador para solicitar esta permissão.', current_user=current_user), 403
    
    # Admins see all projects, regular users see projects created by users with execute permission
    if current_user.is_admin:
        comparison_projects = Project.query.filter_by(is_active=True).all()
        consistency_projects = DataConsistencyConfig.query.filter_by(is_active=True).all()
        connections = DatabaseConnection.query.filter_by(is_active=True).all()
    else:
        # Get user IDs that have execute permission for projects
        authorized_user_ids = get_users_with_execute_permission('projects')
        if not authorized_user_ids:
            comparison_projects = []
        else:
            comparison_projects = Project.query.filter(
                Project.user_id.in_(authorized_user_ids),
                Project.is_active == True
            ).all()
        
        # For consistency projects, use same logic
        consistency_authorized_user_ids = get_users_with_execute_permission('data_consistency')
        if not consistency_authorized_user_ids:
            consistency_projects = []
        else:
            consistency_projects = DataConsistencyConfig.query.filter(
                DataConsistencyConfig.user_id.in_(consistency_authorized_user_ids),
                DataConsistencyConfig.is_active == True
            ).all()
        
        # Connections: users see connections created by users with execute permission
        connection_authorized_user_ids = get_users_with_execute_permission('connections')
        if not connection_authorized_user_ids:
            connections = []
        else:
            connections = DatabaseConnection.query.filter(
                DatabaseConnection.user_id.in_(connection_authorized_user_ids),
                DatabaseConnection.is_active == True
            ).all()
    
    # Generate token for API calls
    token = session.get('token') or generate_token(current_user)
    
    # Check if we should open the create modal (from /projetos/novo redirect)
    open_create_modal = request.args.get('novo') == 'true'
    
    return render_template('projects.html', 
                         comparison_projects=comparison_projects,
                         consistency_projects=consistency_projects,
                         connections=connections, 
                         current_user=current_user,
                         auth_token=token,
                         open_create_modal=open_create_modal)


@projects_template_bp.route('/projetos/novo')
@login_required_template
def new_project_page(current_user):
    """Redirect to projects page with modal open"""
    return redirect('/projetos?novo=true')


@projects_template_bp.route('/projetos/<int:project_id>/editar', methods=['GET', 'POST'])
@login_required_template
def edit_project_page(current_user, project_id):
    """Render edit project page and handle project update"""
    print(f"[PROJECTS] Loading edit project page for project {project_id}")
    try:
        # Get project - users can see projects created by users with execute permission
        if current_user.is_admin:
            project = Project.query.filter_by(id=project_id, is_active=True).first()
        else:
            # Get user IDs that have execute permission for projects
            authorized_user_ids = get_users_with_execute_permission('projects')
            if not authorized_user_ids:
                project = None
            else:
                project = Project.query.filter(
                    Project.id == project_id,
                    Project.user_id.in_(authorized_user_ids),
                    Project.is_active == True
                ).first()
        
        if not project:
            return render_template('error.html', message='Projeto não encontrado', current_user=current_user), 404
        
        # Get connections - admins see all, regular users only their own
        if current_user.is_admin:
            connections = DatabaseConnection.query.filter_by(is_active=True).all()
        else:
            connections = DatabaseConnection.query.filter_by(
                user_id=current_user.id,
                is_active=True
            ).all()
        
        if request.method == 'POST':
            # Handle form submission via API
            # This will be handled by JavaScript, but we can also handle it server-side
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            source_connection_id = request.form.get('source_connection_id')
            target_connection_id = request.form.get('target_connection_id')
            source_table = request.form.get('source_table', '').strip()
            target_table = request.form.get('target_table', '').strip()
            
            # Validation
            if not name:
                return render_template('edit_project.html', 
                                     project=project, 
                                     connections=connections,
                                     current_user=current_user,
                                     error='Nome do projeto é obrigatório')
            
            if not source_connection_id or not target_connection_id:
                return render_template('edit_project.html', 
                                     project=project, 
                                     connections=connections,
                                     current_user=current_user,
                                     error='Selecione ambas as conexões')
            
            if not source_table or not target_table:
                return render_template('edit_project.html', 
                                     project=project, 
                                     connections=connections,
                                     current_user=current_user,
                                     error='Selecione ambas as tabelas')
            
            # Verify connections - admins can use any, regular users only their own
            if current_user.is_admin:
                source_conn = DatabaseConnection.query.filter_by(id=source_connection_id).first()
                target_conn = DatabaseConnection.query.filter_by(id=target_connection_id).first()
            else:
                source_conn = DatabaseConnection.query.filter_by(
                    id=source_connection_id,
                    user_id=current_user.id
                ).first()
                target_conn = DatabaseConnection.query.filter_by(
                    id=target_connection_id,
                    user_id=current_user.id
                ).first()
            
            if not source_conn or not target_conn:
                return render_template('edit_project.html', 
                                     project=project, 
                                     connections=connections,
                                     current_user=current_user,
                                     error='Conexão não encontrada')
            
            # Update project (will be handled by API, but we can redirect)
            # For now, redirect to projects page - JavaScript will handle the API call
            return redirect('/projetos')
        
        # GET request - show edit form
        return render_template('edit_project.html', 
                             project=project, 
                             connections=connections,
                             current_user=current_user)
    except Exception as e:
        import traceback
        print(f"[PROJECTS] Error loading edit project page: {str(e)}")
        print(traceback.format_exc())
        return render_template('error.html', message=f'Erro ao carregar página de edição: {str(e)}'), 500

