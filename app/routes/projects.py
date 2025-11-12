from flask import Blueprint, request, jsonify, session
from datetime import datetime
from app.models.project import Project
from app.models.database_connection import DatabaseConnection
from app.models.user import User
from app import db
from app.utils.security import token_required, get_users_with_execute_permission
from app.services.table_mapper import TableMapper
from app.services.database import DatabaseService
from pathlib import Path
from sqlalchemy import or_

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('', methods=['GET'])
@projects_bp.route('/', methods=['GET'])
@token_required
def get_projects(user):
    """Get all projects - users see projects created by users with execute permission"""
    if user.is_admin:
        # Admins see all projects
        projects = Project.query.filter_by(is_active=True).all()
    else:
        # Get user IDs that have execute permission for projects
        authorized_user_ids = get_users_with_execute_permission('projects')
        if not authorized_user_ids:
            # No users have permission (shouldn't happen if user got here)
            projects = []
        else:
            # Show projects created by any user with execute permission
            projects = Project.query.filter(
                Project.user_id.in_(authorized_user_ids),
                Project.is_active == True
            ).all()
    
    return jsonify({
        'projects': [project.to_dict() for project in projects]
    }), 200


@projects_bp.route('/<int:project_id>', methods=['GET'])
@token_required
def get_project(user, project_id):
    """Get a specific project - users can see projects created by users with execute permission"""
    if user.is_admin:
        project = Project.query.filter_by(id=project_id).first()
    else:
        # Get user IDs that have execute permission for projects
        authorized_user_ids = get_users_with_execute_permission('projects')
        if not authorized_user_ids:
            project = None
        else:
            project = Project.query.filter(
                Project.id == project_id,
                Project.user_id.in_(authorized_user_ids)
            ).first()
    
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    
    return jsonify({'project': project.to_dict()}), 200


@projects_bp.route('', methods=['POST'])
@projects_bp.route('/', methods=['POST'])
@token_required
def create_project(user):
    """Create a new project"""
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('source_table') or not data.get('target_table'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Get connection IDs
    source_connection_id = data.get('source_connection_id')
    target_connection_id = data.get('target_connection_id')
    
    if not source_connection_id or not target_connection_id:
        return jsonify({'message': 'Source and target connection IDs required'}), 400
    
    # Get connections - admins can use any, regular users only their own
    if user.is_admin:
        source_connection = DatabaseConnection.query.filter_by(id=source_connection_id).first()
        target_connection = DatabaseConnection.query.filter_by(id=target_connection_id).first()
    else:
        source_connection = DatabaseConnection.query.filter_by(
            id=source_connection_id, 
            user_id=user.id
        ).first()
        target_connection = DatabaseConnection.query.filter_by(
            id=target_connection_id, 
            user_id=user.id
        ).first()
    
    if not source_connection or not target_connection:
        return jsonify({'message': 'Connection not found'}), 404
    
    try:
        # Get decrypted configs for connection
        source_config = source_connection.get_decrypted_config()
        source_config['type'] = source_connection.db_type
        
        target_config = target_connection.get_decrypted_config()
        target_config['type'] = target_connection.db_type
        
        # Map tables and generate models (already decrypted)
        source_engine = DatabaseService.get_engine(source_config, already_decrypted=True)
        target_engine = DatabaseService.get_engine(target_config, already_decrypted=True)
        
        source_columns = DatabaseService.get_table_columns(source_engine, data['source_table'])
        target_columns = DatabaseService.get_table_columns(target_engine, data['target_table'])
        
        # Generate model code
        base_path = Path(__file__).parent.parent.parent
        source_model_code = TableMapper.generate_model_code(
            data['source_table'], source_columns, source_config
        )
        target_model_code = TableMapper.generate_model_code(
            data['target_table'], target_columns, target_config
        )
        
        # Save model files
        source_model_path = TableMapper.save_model_file(
            data['name'], data['source_table'], source_model_code, base_path
        )
        target_model_path = TableMapper.save_model_file(
            data['name'], data['target_table'], target_model_code, base_path
        )
        
        # Create project
        project = Project(
            name=data['name'],
            description=data.get('description', ''),
            source_table=data['source_table'],
            target_table=data['target_table'],
            source_connection_id=source_connection_id,
            target_connection_id=target_connection_id,
            model_file_path=str(source_model_path),  # Store primary model path
            user_id=user.id
        )
        
        db.session.add(project)
        db.session.flush()
        
        # Create or update table model mappings
        from app.models.table_model_mapping import TableModelMapping
        
        # Check if source mapping already exists
        source_mapping = TableModelMapping.query.filter_by(
            connection_id=source_connection_id,
            table_name=data['source_table'],
            user_id=user.id
        ).first()
        
        if source_mapping:
            # Update existing mapping
            source_mapping.model_file_path = str(source_model_path)
            source_mapping.updated_at = datetime.utcnow()
        else:
            # Create new mapping
            source_mapping = TableModelMapping(
                connection_id=source_connection_id,
                table_name=data['source_table'],
                model_file_path=str(source_model_path),
                user_id=user.id
            )
            db.session.add(source_mapping)
        
        # Check if target mapping already exists
        target_mapping = TableModelMapping.query.filter_by(
            connection_id=target_connection_id,
            table_name=data['target_table'],
            user_id=user.id
        ).first()
        
        if target_mapping:
            # Update existing mapping
            target_mapping.model_file_path = str(target_model_path)
            target_mapping.updated_at = datetime.utcnow()
        else:
            # Create new mapping
            target_mapping = TableModelMapping(
                connection_id=target_connection_id,
                table_name=data['target_table'],
                model_file_path=str(target_model_path),
                user_id=user.id
            )
            db.session.add(target_mapping)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Project created successfully',
            'project': project.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating project: {str(e)}'}), 500


@projects_bp.route('/<int:project_id>', methods=['PUT'])
@token_required
def update_project(user, project_id):
    """Update a project - users can update projects created by users with execute permission"""
    if user.is_admin:
        project = Project.query.filter_by(id=project_id).first()
    else:
        # Get user IDs that have execute permission for projects
        authorized_user_ids = get_users_with_execute_permission('projects')
        if not authorized_user_ids:
            project = None
        else:
            project = Project.query.filter(
                Project.id == project_id,
                Project.user_id.in_(authorized_user_ids)
            ).first()
    
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    
    data = request.get_json()
    
    # Track if tables or connections changed (need to regenerate models)
    tables_changed = False
    connections_changed = False
    
    # Store old values for comparison
    old_source_table = project.source_table
    old_target_table = project.target_table
    old_source_connection_id = project.source_connection_id
    old_target_connection_id = project.target_connection_id
    
    if 'name' in data:
        project.name = data['name']
    if 'description' in data:
        project.description = data['description']
    if 'source_table' in data:
        project.source_table = data['source_table']
        if project.source_table != old_source_table:
            tables_changed = True
    if 'target_table' in data:
        project.target_table = data['target_table']
        if project.target_table != old_target_table:
            tables_changed = True
    if 'source_connection_id' in data:
        # Verify connection belongs to user
        source_connection = DatabaseConnection.query.filter_by(
            id=data['source_connection_id'], 
            user_id=user.id
        ).first()
        if source_connection:
            if project.source_connection_id != data['source_connection_id']:
                connections_changed = True
            project.source_connection_id = data['source_connection_id']
        else:
            return jsonify({'message': 'Source connection not found'}), 404
    if 'target_connection_id' in data:
        # Verify connection belongs to user
        target_connection = DatabaseConnection.query.filter_by(
            id=data['target_connection_id'], 
            user_id=user.id
        ).first()
        if target_connection:
            if project.target_connection_id != data['target_connection_id']:
                connections_changed = True
            project.target_connection_id = data['target_connection_id']
        else:
            return jsonify({'message': 'Target connection not found'}), 404
    
    # If tables or connections changed, regenerate models
    if tables_changed or connections_changed:
        try:
            # Get connections (already verified above)
            source_connection = DatabaseConnection.query.filter_by(
                id=project.source_connection_id,
                user_id=user.id
            ).first()
            target_connection = DatabaseConnection.query.filter_by(
                id=project.target_connection_id,
                user_id=user.id
            ).first()
            
            # Get decrypted configs
            source_config = source_connection.get_decrypted_config()
            source_config['type'] = source_connection.db_type
            target_config = target_connection.get_decrypted_config()
            target_config['type'] = target_connection.db_type
            
            # Generate models
            source_engine = DatabaseService.get_engine(source_config, already_decrypted=True)
            target_engine = DatabaseService.get_engine(target_config, already_decrypted=True)
            
            source_columns = DatabaseService.get_table_columns(source_engine, project.source_table)
            target_columns = DatabaseService.get_table_columns(target_engine, project.target_table)
            
            # Generate model code
            base_path = Path(__file__).parent.parent.parent
            source_model_code = TableMapper.generate_model_code(
                project.source_table, source_columns, source_config
            )
            target_model_code = TableMapper.generate_model_code(
                project.target_table, target_columns, target_config
            )
            
            # Save model files
            source_model_path = TableMapper.save_model_file(
                project.name, project.source_table, source_model_code, base_path
            )
            target_model_path = TableMapper.save_model_file(
                project.name, project.target_table, target_model_code, base_path
            )
            
            # Update project model file path
            project.model_file_path = str(source_model_path)
            
            # Update or create table model mappings
            from app.models.table_model_mapping import TableModelMapping
            
            # Source mapping
            source_mapping = TableModelMapping.query.filter_by(
                connection_id=project.source_connection_id,
                table_name=project.source_table,
                user_id=user.id
            ).first()
            
            if source_mapping:
                source_mapping.model_file_path = str(source_model_path)
                source_mapping.updated_at = datetime.utcnow()
            else:
                source_mapping = TableModelMapping(
                    connection_id=project.source_connection_id,
                    table_name=project.source_table,
                    model_file_path=str(source_model_path),
                    user_id=user.id
                )
                db.session.add(source_mapping)
            
            # Target mapping
            target_mapping = TableModelMapping.query.filter_by(
                connection_id=project.target_connection_id,
                table_name=project.target_table,
                user_id=user.id
            ).first()
            
            if target_mapping:
                target_mapping.model_file_path = str(target_model_path)
                target_mapping.updated_at = datetime.utcnow()
            else:
                target_mapping = TableModelMapping(
                    connection_id=project.target_connection_id,
                    table_name=project.target_table,
                    model_file_path=str(target_model_path),
                    user_id=user.id
                )
                db.session.add(target_mapping)
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error regenerating models: {str(e)}'}), 500
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Project updated successfully',
            'project': project.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating project: {str(e)}'}), 500


@projects_bp.route('/<int:project_id>', methods=['DELETE'])
@token_required
def delete_project(user, project_id):
    """Delete a project (soft delete) - users can delete projects created by users with execute permission"""
    if user.is_admin:
        project = Project.query.filter_by(id=project_id).first()
    else:
        # Get user IDs that have execute permission for projects
        authorized_user_ids = get_users_with_execute_permission('projects')
        if not authorized_user_ids:
            project = None
        else:
            project = Project.query.filter(
                Project.id == project_id,
                Project.user_id.in_(authorized_user_ids)
            ).first()
    
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    
    project.is_active = False
    
    try:
        db.session.commit()
        return jsonify({'message': 'Project deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error deleting project: {str(e)}'}), 500


