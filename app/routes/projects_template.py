from flask import Blueprint, render_template, request, redirect, url_for, session
from app.models.project import Project
from app.models.database_connection import DatabaseConnection
from app.utils.security import login_required_template

projects_template_bp = Blueprint('projects_template', __name__)


@projects_template_bp.route('/projetos')
@login_required_template
def projects_page(current_user):
    """Render projects management page"""
    projects = Project.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    connections = DatabaseConnection.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    return render_template('projects.html', projects=projects, connections=connections, current_user=current_user)


@projects_template_bp.route('/projetos/<int:project_id>/editar', methods=['GET', 'POST'])
@login_required_template
def edit_project_page(current_user, project_id):
    """Render edit project page and handle project update"""
    print(f"[PROJECTS] Loading edit project page for project {project_id}")
    try:
        # Get project and verify ownership
        project = Project.query.filter_by(
            id=project_id,
            user_id=current_user.id,
            is_active=True
        ).first()
        
        if not project:
            return render_template('error.html', message='Projeto não encontrado'), 404
        
        # Get all user connections
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
            
            # Verify connections belong to user
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

