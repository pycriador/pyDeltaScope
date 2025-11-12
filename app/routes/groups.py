from flask import Blueprint, request, jsonify
from app.models.group import Group
from app.models.user import User
from app import db
from app.utils.security import admin_required
from datetime import datetime

groups_bp = Blueprint('groups', __name__)


@groups_bp.route('/', methods=['GET'])
@admin_required
def list_groups(current_user):
    """List all groups (Admin only)"""
    try:
        groups = Group.query.all()
        return jsonify({
            'groups': [group.to_dict() for group in groups]
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error listing groups: {str(e)}'}), 500


@groups_bp.route('/', methods=['POST'])
@admin_required
def create_group(current_user):
    """Create a new group (Admin only)"""
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'message': 'Group name is required'}), 400
    
    # Check if group already exists
    if Group.query.filter_by(name=data['name']).first():
        return jsonify({'message': 'Group name already exists'}), 400
    
    # Create new group with all permissions
    group = Group(
        name=data['name'],
        description=data.get('description', ''),
        # Connections
        can_create_connections=data.get('can_create_connections', False),
        can_execute_connections=data.get('can_execute_connections', False),
        # Projects
        can_create_projects=data.get('can_create_projects', False),
        can_execute_projects=data.get('can_execute_projects', False),
        # Tables
        can_create_tables=data.get('can_create_tables', False),
        can_execute_tables=data.get('can_execute_tables', False),
        # Users
        can_create_users=data.get('can_create_users', False),
        can_execute_users=data.get('can_execute_users', False),
        # Groups
        can_create_groups=data.get('can_create_groups', False),
        can_execute_groups=data.get('can_execute_groups', False),
        # Comparison Reports
        can_create_comparison_reports=data.get('can_create_comparison_reports', False),
        can_execute_comparison_reports=data.get('can_execute_comparison_reports', False),
        # Consistency Reports
        can_create_consistency_reports=data.get('can_create_consistency_reports', False),
        can_execute_consistency_reports=data.get('can_execute_consistency_reports', False),
        # Dashboard
        can_create_dashboard=data.get('can_create_dashboard', False),
        can_execute_dashboard=data.get('can_execute_dashboard', False),
        # Comparison
        can_create_comparison=data.get('can_create_comparison', False),
        can_execute_comparison=data.get('can_execute_comparison', False),
        # Scheduled Tasks
        can_create_scheduled_tasks=data.get('can_create_scheduled_tasks', False),
        can_execute_scheduled_tasks=data.get('can_execute_scheduled_tasks', False),
        # Webhooks
        can_create_webhooks=data.get('can_create_webhooks', False),
        can_execute_webhooks=data.get('can_execute_webhooks', False),
        # Data Consistency
        can_create_data_consistency=data.get('can_create_data_consistency', False),
        can_execute_data_consistency=data.get('can_execute_data_consistency', False),
        # Legacy permissions (backward compatibility)
        can_view_dashboards=data.get('can_view_dashboards', False),
        can_edit_tables=data.get('can_edit_tables', False),
        can_view_tables=data.get('can_view_tables', False),
        can_view_reports=data.get('can_view_reports', False),
        can_download_reports=data.get('can_download_reports', False)
    )
    
    try:
        db.session.add(group)
        db.session.commit()
        
        return jsonify({
            'message': 'Group created successfully',
            'group': group.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating group: {str(e)}'}), 500


@groups_bp.route('/<int:group_id>', methods=['GET'])
@admin_required
def get_group(current_user, group_id):
    """Get group details (Admin only)"""
    group = Group.query.get(group_id)
    if not group:
        return jsonify({'message': 'Group not found'}), 404
    
    return jsonify({'group': group.to_dict()}), 200


@groups_bp.route('/<int:group_id>', methods=['PUT'])
@admin_required
def update_group(current_user, group_id):
    """Update a group (Admin only)"""
    data = request.get_json()
    
    group = Group.query.get(group_id)
    if not group:
        return jsonify({'message': 'Group not found'}), 404
    
    try:
        if 'name' in data:
            # Check if name already exists (excluding current group)
            existing = Group.query.filter_by(name=data['name']).first()
            if existing and existing.id != group_id:
                return jsonify({'message': 'Group name already exists'}), 400
            group.name = data['name']
        
        if 'description' in data:
            group.description = data['description']
        
        # Update permissions - all new granular permissions
        permission_fields = [
            # Connections
            'can_create_connections', 'can_execute_connections',
            # Projects
            'can_create_projects', 'can_execute_projects',
            # Tables
            'can_create_tables', 'can_execute_tables',
            # Users
            'can_create_users', 'can_execute_users',
            # Groups
            'can_create_groups', 'can_execute_groups',
            # Comparison Reports
            'can_create_comparison_reports', 'can_execute_comparison_reports',
            # Consistency Reports
            'can_create_consistency_reports', 'can_execute_consistency_reports',
            # Dashboard
            'can_create_dashboard', 'can_execute_dashboard',
            # Comparison
            'can_create_comparison', 'can_execute_comparison',
            # Scheduled Tasks
            'can_create_scheduled_tasks', 'can_execute_scheduled_tasks',
            # Webhooks
            'can_create_webhooks', 'can_execute_webhooks',
            # Data Consistency
            'can_create_data_consistency', 'can_execute_data_consistency',
            # Legacy permissions (backward compatibility)
            'can_view_dashboards', 'can_edit_tables', 'can_view_tables',
            'can_view_reports', 'can_download_reports'
        ]
        
        for field in permission_fields:
            if field in data:
                setattr(group, field, data[field])
        
        group.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Group updated successfully',
            'group': group.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating group: {str(e)}'}), 500


@groups_bp.route('/<int:group_id>', methods=['DELETE'])
@admin_required
def delete_group(current_user, group_id):
    """Delete a group (Admin only)"""
    group = Group.query.get(group_id)
    if not group:
        return jsonify({'message': 'Group not found'}), 404
    
    try:
        # Remove all user associations
        group.users = []
        db.session.commit()
        
        # Delete group
        db.session.delete(group)
        db.session.commit()
        
        return jsonify({'message': 'Group deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error deleting group: {str(e)}'}), 500


@groups_bp.route('/<int:group_id>/users', methods=['GET'])
@admin_required
def get_group_users(current_user, group_id):
    """Get users in a group (Admin only)"""
    group = Group.query.get(group_id)
    if not group:
        return jsonify({'message': 'Group not found'}), 404
    
    return jsonify({
        'users': [user.to_dict() for user in group.users]
    }), 200


@groups_bp.route('/<int:group_id>/users/<int:user_id>', methods=['POST'])
@admin_required
def add_user_to_group(current_user, group_id, user_id):
    """Add user to group (Admin only)"""
    group = Group.query.get(group_id)
    if not group:
        return jsonify({'message': 'Group not found'}), 404
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    try:
        if user in group.users.all():
            return jsonify({'message': 'User is already in this group'}), 400
        
        group.users.append(user)
        db.session.commit()
        
        return jsonify({'message': 'User added to group successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error adding user to group: {str(e)}'}), 500


@groups_bp.route('/<int:group_id>/users/<int:user_id>', methods=['DELETE'])
@admin_required
def remove_user_from_group(current_user, group_id, user_id):
    """Remove user from group (Admin only)"""
    group = Group.query.get(group_id)
    if not group:
        return jsonify({'message': 'Group not found'}), 404
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    try:
        if user not in group.users.all():
            return jsonify({'message': 'User is not in this group'}), 400
        
        group.users.remove(user)
        db.session.commit()
        
        return jsonify({'message': 'User removed from group successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error removing user from group: {str(e)}'}), 500


@groups_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user_groups(current_user, user_id):
    """Get groups for a user (Admin only)"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({
        'groups': [group.to_dict() for group in user.groups]
    }), 200

