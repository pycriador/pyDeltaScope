from flask import Blueprint, request, jsonify
from app.models.scheduled_task import ScheduledTask
from app.models.project import Project
from app import db
from app.utils.security import token_required
from datetime import datetime, timedelta
from croniter import croniter
from app.services.database import DatabaseService
import json

scheduled_tasks_bp = Blueprint('scheduled_tasks', __name__)


def calculate_next_run(schedule_type, schedule_value, last_run=None):
    """Calculate next run time based on schedule type and value"""
    now = datetime.utcnow()
    
    if schedule_type == 'preset':
        if schedule_value == '15min':
            return now + timedelta(minutes=15)
        elif schedule_value == '1hour':
            return now + timedelta(hours=1)
        elif schedule_value == '6hours':
            return now + timedelta(hours=6)
        elif schedule_value == '12hours':
            return now + timedelta(hours=12)
        elif schedule_value == 'daily':
            # Next day at midnight UTC
            next_day = now + timedelta(days=1)
            return next_day.replace(hour=0, minute=0, second=0, microsecond=0)
    
    elif schedule_type == 'interval':
        # schedule_value is minutes
        minutes = int(schedule_value)
        return now + timedelta(minutes=minutes)
    
    elif schedule_type == 'cron':
        # schedule_value is cron expression
        try:
            cron = croniter(schedule_value, now)
            return cron.get_next(datetime)
        except Exception as e:
            raise ValueError(f"Invalid cron expression: {str(e)}")
    
    return now


@scheduled_tasks_bp.route('', methods=['GET'])
@token_required
def list_scheduled_tasks(user):
    """List all scheduled tasks for the user"""
    try:
        tasks = ScheduledTask.query.filter_by(user_id=user.id).order_by(ScheduledTask.created_at.desc()).all()
        return jsonify({
            'tasks': [task.to_dict() for task in tasks]
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error listing scheduled tasks: {str(e)}'}), 500


@scheduled_tasks_bp.route('/<int:task_id>', methods=['GET'])
@token_required
def get_scheduled_task(user, task_id):
    """Get a specific scheduled task"""
    task = ScheduledTask.query.filter_by(id=task_id, user_id=user.id).first()
    
    if not task:
        return jsonify({'message': 'Scheduled task not found'}), 404
    
    return jsonify(task.to_dict()), 200


@scheduled_tasks_bp.route('', methods=['POST'])
@token_required
def create_scheduled_task(user):
    """Create a new scheduled task"""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    # Validate required fields
    required_fields = ['name', 'project_id', 'schedule_type', 'schedule_value']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400
    
    # Verify project belongs to user
    project = Project.query.filter_by(id=data['project_id'], user_id=user.id).first()
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    
    try:
        # Calculate next run time
        next_run = calculate_next_run(
            data['schedule_type'],
            data['schedule_value']
        )
        
        # Get and validate key_mappings
        key_mappings = data.get('key_mappings', {})
        if not isinstance(key_mappings, dict):
            if isinstance(key_mappings, str):
                import json
                try:
                    key_mappings = json.loads(key_mappings)
                except:
                    key_mappings = {}
            else:
                key_mappings = {}
        
        print(f"[CREATE_TASK] Saving key_mappings: {key_mappings}, type: {type(key_mappings)}", flush=True)
        
        # Create scheduled task
        task = ScheduledTask(
            name=data['name'],
            description=data.get('description', ''),
            project_id=data['project_id'],
            user_id=user.id,
            schedule_type=data['schedule_type'],
            schedule_value=data['schedule_value'],
            key_mappings=key_mappings,
            is_active=data.get('is_active', True),
            next_run_at=next_run
        )
        
        db.session.add(task)
        db.session.flush()  # Flush to get task.id
        
        # Verify key_mappings were saved correctly
        print(f"[CREATE_TASK] Task created with ID {task.id}, key_mappings saved: {task.key_mappings}, type: {type(task.key_mappings)}", flush=True)
        
        db.session.commit()
        
        # Add task to scheduler
        try:
            from app.services.scheduler_service import SchedulerService
            if task.is_active:
                SchedulerService.add_task(task.id)
        except Exception as e:
            print(f"[SCHEDULER] Error adding task to scheduler: {str(e)}")
        
        # Return created task
        return jsonify({
            'message': 'Scheduled task created successfully',
            'task': task.to_dict()
        }), 201
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating scheduled task: {str(e)}'}), 500


@scheduled_tasks_bp.route('/<int:task_id>', methods=['PUT'])
@token_required
def update_scheduled_task(user, task_id):
    """Update a scheduled task"""
    task = ScheduledTask.query.filter_by(id=task_id, user_id=user.id).first()
    
    if not task:
        return jsonify({'message': 'Scheduled task not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    try:
        # Update fields
        if 'name' in data:
            task.name = data['name']
        if 'description' in data:
            task.description = data['description']
        if 'project_id' in data:
            # Verify project belongs to user
            project = Project.query.filter_by(id=data['project_id'], user_id=user.id).first()
            if not project:
                return jsonify({'message': 'Project not found'}), 404
            task.project_id = data['project_id']
        if 'schedule_type' in data:
            task.schedule_type = data['schedule_type']
        if 'schedule_value' in data:
            task.schedule_value = data['schedule_value']
        if 'key_mappings' in data:
            task.key_mappings = data['key_mappings']
        if 'is_active' in data:
            task.is_active = data['is_active']
        
        # Recalculate next run if schedule changed
        if 'schedule_type' in data or 'schedule_value' in data:
            task.next_run_at = calculate_next_run(
                task.schedule_type,
                task.schedule_value,
                task.last_run_at
            )
        
        task.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Update scheduler
        try:
            from app.services.scheduler_service import SchedulerService
            if task.is_active:
                SchedulerService.add_task(task.id)
            else:
                SchedulerService.remove_task(task.id)
        except Exception as e:
            print(f"[SCHEDULER] Error updating task in scheduler: {str(e)}")
        
        return jsonify({
            'message': 'Scheduled task updated successfully',
            'task': task.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating scheduled task: {str(e)}'}), 500


@scheduled_tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@token_required
def delete_scheduled_task(user, task_id):
    """Delete a scheduled task"""
    task = ScheduledTask.query.filter_by(id=task_id, user_id=user.id).first()
    
    if not task:
        return jsonify({'message': 'Scheduled task not found'}), 404
    
    try:
        # Remove from scheduler first
        try:
            from app.services.scheduler_service import SchedulerService
            SchedulerService.remove_task(task_id)
        except Exception as e:
            print(f"[SCHEDULER] Error removing task from scheduler: {str(e)}")
        
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({'message': 'Scheduled task deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error deleting scheduled task: {str(e)}'}), 500


@scheduled_tasks_bp.route('/<int:task_id>/toggle', methods=['PUT'])
@token_required
def toggle_scheduled_task(user, task_id):
    """Toggle active status of a scheduled task"""
    task = ScheduledTask.query.filter_by(id=task_id, user_id=user.id).first()
    
    if not task:
        return jsonify({'message': 'Scheduled task not found'}), 404
    
    try:
        task.is_active = not task.is_active
        
        # If activating, recalculate next run
        if task.is_active:
            task.next_run_at = calculate_next_run(
                task.schedule_type,
                task.schedule_value,
                task.last_run_at
            )
        
        db.session.commit()
        
        # Update scheduler
        try:
            from app.services.scheduler_service import SchedulerService
            if task.is_active:
                SchedulerService.add_task(task.id)
            else:
                SchedulerService.remove_task(task.id)
        except Exception as e:
            print(f"[SCHEDULER] Error updating task status in scheduler: {str(e)}")
        
        return jsonify({
            'message': 'Scheduled task status updated',
            'task': task.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error toggling scheduled task: {str(e)}'}), 500


@scheduled_tasks_bp.route('/<int:task_id>/run-now', methods=['POST'])
@token_required
def run_scheduled_task_now(user, task_id):
    """Manually trigger a scheduled task execution - redirects to comparison execution page"""
    from flask import redirect, url_for
    
    task = ScheduledTask.query.filter_by(id=task_id, user_id=user.id).first()
    
    if not task:
        return jsonify({'message': 'Scheduled task not found'}), 404
    
    # Build URL with key mappings as query parameters
    base_url = f'/comparacao/{task.project_id}/execution'
    
    # Add key mappings as URL parameters
    if task.key_mappings:
        params = []
        for source, target in task.key_mappings.items():
            params.append(f'source_key={source}&target_key={target}')
        if params:
            base_url += '?' + '&'.join(params)
    
    # Return redirect URL instead of executing directly
    return jsonify({
        'message': 'Redirecting to execution page',
        'redirect_url': base_url
    }), 200


@scheduled_tasks_bp.route('/project/<int:project_id>/columns', methods=['GET'])
@token_required
def get_project_columns(user, project_id):
    """Get columns from source and target tables of a project"""
    project = Project.query.filter_by(id=project_id, user_id=user.id).first()
    
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    
    try:
        # Get source table columns
        source_config = project.source_connection.get_decrypted_config()
        source_config['type'] = project.source_connection.db_type
        source_engine = DatabaseService.get_engine(source_config, already_decrypted=True)
        source_columns = DatabaseService.get_table_columns(source_engine, project.source_table)
        source_primary_keys = DatabaseService.get_primary_keys(source_engine, project.source_table)
        
        # Get target table columns
        target_config = project.target_connection.get_decrypted_config()
        target_config['type'] = project.target_connection.db_type
        target_engine = DatabaseService.get_engine(target_config, already_decrypted=True)
        target_columns = DatabaseService.get_table_columns(target_engine, project.target_table)
        target_primary_keys = DatabaseService.get_primary_keys(target_engine, project.target_table)
        
        return jsonify({
            'source_columns': [col['name'] for col in source_columns],
            'target_columns': [col['name'] for col in target_columns],
            'source_primary_keys': source_primary_keys,
            'target_primary_keys': target_primary_keys,
            'source_table': project.source_table,
            'target_table': project.target_table
        }), 200
    except Exception as e:
        import traceback
        print(f"[SCHEDULED_TASKS] Error getting columns: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'message': f'Error getting columns: {str(e)}'}), 500

