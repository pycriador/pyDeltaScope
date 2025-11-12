from flask import Blueprint, request, jsonify
from app.models.data_consistency import DataConsistencyConfig, DataConsistencyCheck, DataConsistencyResult
from app.models.database_connection import DatabaseConnection
from app import db
from app.utils.security import token_required
from app.services.database import DatabaseService
from app.services.consistency_service import ConsistencyService
from datetime import datetime

consistency_bp = Blueprint('consistency', __name__)


@consistency_bp.route('/configs', methods=['GET'])
@token_required
def list_consistency_configs(user):
    """List all consistency configurations - admins see all, regular users see only their own"""
    try:
        if user.is_admin:
            configs = DataConsistencyConfig.query.filter_by(is_active=True).order_by(DataConsistencyConfig.created_at.desc()).all()
        else:
            configs = DataConsistencyConfig.query.filter_by(user_id=user.id, is_active=True).order_by(DataConsistencyConfig.created_at.desc()).all()
        return jsonify({
            'configs': [config.to_dict() for config in configs]
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error listing consistency configs: {str(e)}'}), 500


@consistency_bp.route('/configs/<int:config_id>', methods=['GET'])
@token_required
def get_consistency_config(user, config_id):
    """Get a specific consistency configuration - admins can see any, regular users only their own"""
    if user.is_admin:
        config = DataConsistencyConfig.query.filter_by(id=config_id).first()
    else:
        config = DataConsistencyConfig.query.filter_by(id=config_id, user_id=user.id).first()
    
    if not config:
        return jsonify({'message': 'Consistency config not found'}), 404
    
    return jsonify(config.to_dict()), 200


@consistency_bp.route('/configs', methods=['POST'])
@token_required
def create_consistency_config(user):
    """Create a new consistency configuration"""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    required_fields = ['name', 'source_connection_id', 'source_table', 'target_connection_id', 'target_table', 'join_mappings', 'comparison_fields']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400
    
    # Validate connections - admins can use any, regular users only their own
    if user.is_admin:
        source_connection = DatabaseConnection.query.filter_by(id=data['source_connection_id']).first()
        target_connection = DatabaseConnection.query.filter_by(id=data['target_connection_id']).first()
    else:
        source_connection = DatabaseConnection.query.filter_by(
            id=data['source_connection_id'],
            user_id=user.id
        ).first()
        target_connection = DatabaseConnection.query.filter_by(
            id=data['target_connection_id'],
            user_id=user.id
        ).first()
    
    if not source_connection or not target_connection:
        return jsonify({'message': 'Connection not found'}), 404
    
    # Validate join_mappings and comparison_fields are lists/dicts
    if not isinstance(data['join_mappings'], dict):
        return jsonify({'message': 'join_mappings must be a dictionary'}), 400
    
    if not isinstance(data['comparison_fields'], list):
        return jsonify({'message': 'comparison_fields must be a list'}), 400
    
    if len(data['join_mappings']) == 0:
        return jsonify({'message': 'At least one join mapping is required'}), 400
    
    if len(data['comparison_fields']) == 0:
        return jsonify({'message': 'At least one comparison field is required'}), 400
    
    try:
        config = DataConsistencyConfig(
            name=data['name'],
            description=data.get('description', ''),
            source_connection_id=data['source_connection_id'],
            source_table=data['source_table'],
            target_connection_id=data['target_connection_id'],
            target_table=data['target_table'],
            join_mappings=data['join_mappings'],
            comparison_fields=data['comparison_fields'],
            user_id=user.id
        )
        
        db.session.add(config)
        db.session.commit()
        
        return jsonify({
            'message': 'Consistency config created successfully',
            'config': config.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating consistency config: {str(e)}'}), 500


@consistency_bp.route('/configs/<int:config_id>', methods=['PUT'])
@token_required
def update_consistency_config(user, config_id):
    """Update a consistency configuration - admins can update any, regular users only their own"""
    if user.is_admin:
        config = DataConsistencyConfig.query.filter_by(id=config_id).first()
    else:
        config = DataConsistencyConfig.query.filter_by(id=config_id, user_id=user.id).first()
    
    if not config:
        return jsonify({'message': 'Consistency config not found'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    
    try:
        if 'name' in data:
            config.name = data['name']
        if 'description' in data:
            config.description = data['description']
        if 'source_connection_id' in data:
            # Verify source connection - admins can use any, regular users only their own
            if user.is_admin:
                source_conn = DatabaseConnection.query.filter_by(id=data['source_connection_id']).first()
            else:
                source_conn = DatabaseConnection.query.filter_by(id=data['source_connection_id'], user_id=user.id).first()
            if not source_conn:
                return jsonify({'message': 'Source connection not found'}), 404
            config.source_connection_id = data['source_connection_id']
        if 'source_table' in data:
            config.source_table = data['source_table']
        if 'target_connection_id' in data:
            # Verify target connection - admins can use any, regular users only their own
            if user.is_admin:
                target_conn = DatabaseConnection.query.filter_by(id=data['target_connection_id']).first()
            else:
                target_conn = DatabaseConnection.query.filter_by(id=data['target_connection_id'], user_id=user.id).first()
            if not target_conn:
                return jsonify({'message': 'Target connection not found'}), 404
            config.target_connection_id = data['target_connection_id']
        if 'target_table' in data:
            config.target_table = data['target_table']
        if 'join_mappings' in data:
            if not isinstance(data['join_mappings'], dict) or len(data['join_mappings']) == 0:
                return jsonify({'message': 'join_mappings must be a non-empty dictionary'}), 400
            config.join_mappings = data['join_mappings']
        if 'comparison_fields' in data:
            if not isinstance(data['comparison_fields'], list) or len(data['comparison_fields']) == 0:
                return jsonify({'message': 'comparison_fields must be a non-empty list'}), 400
            config.comparison_fields = data['comparison_fields']
        if 'is_active' in data:
            config.is_active = data['is_active']
        
        config.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Consistency config updated successfully',
            'config': config.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating consistency config: {str(e)}'}), 500


@consistency_bp.route('/configs/<int:config_id>', methods=['DELETE'])
@token_required
def delete_consistency_config(user, config_id):
    """Delete a consistency configuration - admins can delete any, regular users only their own"""
    if user.is_admin:
        config = DataConsistencyConfig.query.filter_by(id=config_id).first()
    else:
        config = DataConsistencyConfig.query.filter_by(id=config_id, user_id=user.id).first()
    
    if not config:
        return jsonify({'message': 'Consistency config not found'}), 404
    
    try:
        db.session.delete(config)
        db.session.commit()
        
        return jsonify({'message': 'Consistency config deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error deleting consistency config: {str(e)}'}), 500


@consistency_bp.route('/configs/<int:config_id>/run', methods=['POST'])
@token_required
def run_consistency_check(user, config_id):
    """Run a consistency check - admins can run any, regular users only their own"""
    if user.is_admin:
        config = DataConsistencyConfig.query.filter_by(id=config_id).first()
    else:
        config = DataConsistencyConfig.query.filter_by(id=config_id, user_id=user.id).first()
    
    if not config:
        return jsonify({'message': 'Consistency config not found'}), 404
    
    if not config.is_active:
        return jsonify({'message': 'Consistency config is not active'}), 400
    
    try:
        check, inconsistencies = ConsistencyService.check_consistency(config)
        
        return jsonify({
            'message': 'Consistency check completed successfully',
            'check': check.to_dict(),
            'total_inconsistencies': len(inconsistencies)
        }), 200
    except Exception as e:
        import traceback
        print(f"[CONSISTENCY] Error running check: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'message': f'Error running consistency check: {str(e)}'}), 500


@consistency_bp.route('/configs/<int:config_id>/checks', methods=['GET'])
@token_required
def list_config_checks(user, config_id):
    """List all checks for a consistency configuration"""
    config = DataConsistencyConfig.query.filter_by(id=config_id, user_id=user.id).first()
    
    if not config:
        return jsonify({'message': 'Consistency config not found'}), 404
    
    try:
        checks = DataConsistencyCheck.query.filter_by(config_id=config_id).order_by(DataConsistencyCheck.executed_at.desc()).all()
        
        return jsonify({
            'checks': [check.to_dict() for check in checks]
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error listing checks: {str(e)}'}), 500


@consistency_bp.route('/checks/<int:check_id>', methods=['DELETE'])
@token_required
def delete_consistency_check(user, check_id):
    """Delete a consistency check"""
    check = DataConsistencyCheck.query.get(check_id)
    
    if not check:
        return jsonify({'message': 'Consistency check not found'}), 404
    
    # Verify user owns the config
    if check.config.user_id != user.id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    try:
        db.session.delete(check)
        db.session.commit()
        
        return jsonify({'message': 'Consistency check deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error deleting consistency check: {str(e)}'}), 500


@consistency_bp.route('/checks/<int:check_id>/results', methods=['GET'])
@token_required
def get_consistency_results(user, check_id):
    """Get results from a consistency check"""
    check = DataConsistencyCheck.query.get(check_id)
    
    if not check:
        return jsonify({'message': 'Consistency check not found'}), 404
    
    # Verify user owns the config
    if check.config.user_id != user.id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    try:
        results = DataConsistencyResult.query.filter_by(check_id=check_id).order_by(DataConsistencyResult.detected_at.desc()).all()
        
        return jsonify({
            'check': check.to_dict(),
            'results': [result.to_dict() for result in results]
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error getting consistency results: {str(e)}'}), 500


@consistency_bp.route('/connections/<int:connection_id>/tables/<table_name>/columns', methods=['GET'])
@token_required
def get_table_columns_for_consistency(user, connection_id, table_name):
    """Get columns from a table for consistency configuration - admins can access any, regular users only their own"""
    if user.is_admin:
        connection = DatabaseConnection.query.filter_by(id=connection_id).first()
    else:
        connection = DatabaseConnection.query.filter_by(id=connection_id, user_id=user.id).first()
    
    if not connection:
        return jsonify({'message': 'Connection not found'}), 404
    
    try:
        decrypted_config = connection.get_decrypted_config()
        decrypted_config['type'] = connection.db_type
        
        engine = DatabaseService.get_engine(decrypted_config, already_decrypted=True)
        columns = DatabaseService.get_table_columns(engine, table_name)
        primary_keys = DatabaseService.get_primary_keys(engine, table_name)
        
        return jsonify({
            'columns': [col['name'] for col in columns],
            'primary_keys': primary_keys,
            'table_name': table_name
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error getting table columns: {str(e)}'}), 500

