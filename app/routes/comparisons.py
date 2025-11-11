from flask import Blueprint, request, jsonify
from app.models.comparison import Comparison, ComparisonResult
from app.models.project import Project
from app.models.change_log import ChangeLog
from app import db
from app.utils.security import token_required
from app.services.comparison_service import ComparisonService
from app.services.database import DatabaseService

comparisons_bp = Blueprint('comparisons', __name__)


@comparisons_bp.route('/project/<int:project_id>', methods=['POST'])
@token_required
def run_comparison(user, project_id):
    """Run comparison for a project"""
    project = Project.query.filter_by(id=project_id, user_id=user.id).first()
    
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    
    try:
        # Get primary keys and table names from request or use project defaults
        data = request.get_json() or {}
        primary_keys = data.get('primary_keys', [])
        key_mappings = data.get('key_mappings', {})  # Mapping from source to target column names
        source_table = data.get('source_table', project.source_table)
        target_table = data.get('target_table', project.target_table)
        
        # Get connection configs
        source_config = project.source_connection.get_decrypted_config()
        source_config['type'] = project.source_connection.db_type
        
        target_config = project.target_connection.get_decrypted_config()
        target_config['type'] = project.target_connection.db_type
        
        # If not provided, try to get from source table (already decrypted)
        if not primary_keys:
            source_engine = DatabaseService.get_engine(source_config, already_decrypted=True)
            primary_keys = DatabaseService.get_primary_keys(source_engine, source_table)
        
        # Run comparison with key mappings
        differences_df, differences = ComparisonService.compare_tables(
            source_config,
            target_config,
            source_table,
            target_table,
            primary_keys,
            key_mappings
        )
        
        # Save results
        comparison = ComparisonService.save_comparison_results(
            project_id,
            differences,
            metadata={
                'primary_keys': primary_keys,
                'key_mappings': key_mappings,
                'total_source_rows': len(differences_df) if not differences_df.empty else 0
            }
        )
        
        return jsonify({
            'message': 'Comparison completed',
            'comparison': comparison.to_dict(),
            'total_differences': len(differences)
        }), 200
    
    except Exception as e:
        return jsonify({'message': f'Error running comparison: {str(e)}'}), 500


@comparisons_bp.route('/project/<int:project_id>', methods=['GET'])
@token_required
def get_comparisons(user, project_id):
    """Get all comparisons for a project"""
    project = Project.query.filter_by(id=project_id, user_id=user.id).first()
    
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    
    comparisons = Comparison.query.filter_by(project_id=project_id).order_by(Comparison.executed_at.desc()).all()
    
    return jsonify({
        'comparisons': [comp.to_dict() for comp in comparisons]
    }), 200


@comparisons_bp.route('', methods=['GET'])
@token_required
def get_all_comparisons(user):
    """Get all comparisons for all user projects"""
    # Get all user projects
    user_projects = Project.query.filter_by(user_id=user.id, is_active=True).all()
    project_ids = [p.id for p in user_projects]
    
    if not project_ids:
        return jsonify({'comparisons': []}), 200
    
    # Get all comparisons for user projects
    comparisons = Comparison.query.filter(
        Comparison.project_id.in_(project_ids)
    ).order_by(Comparison.executed_at.desc()).all()
    
    # Include project info in response
    comparisons_data = []
    for comp in comparisons:
        comp_dict = comp.to_dict()
        project = next((p for p in user_projects if p.id == comp.project_id), None)
        if project:
            comp_dict['project_name'] = project.name
            comp_dict['project_source_table'] = project.source_table
            comp_dict['project_target_table'] = project.target_table
        comparisons_data.append(comp_dict)
    
    return jsonify({
        'comparisons': comparisons_data
    }), 200


@comparisons_bp.route('/<int:comparison_id>/results', methods=['GET'])
@token_required
def get_comparison_results(user, comparison_id):
    """Get results for a specific comparison"""
    comparison = Comparison.query.get(comparison_id)
    
    if not comparison:
        return jsonify({'message': 'Comparison not found'}), 404
    
    # Verify project ownership
    project = Project.query.get(comparison.project_id)
    if project.user_id != user.id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    results = ComparisonResult.query.filter_by(comparison_id=comparison_id).all()
    
    return jsonify({
        'comparison': comparison.to_dict(),
        'results': [result.to_dict() for result in results]
    }), 200


@comparisons_bp.route('/project/<int:project_id>/send-changes', methods=['POST'])
@token_required
def send_changes_to_api(user, project_id):
    """Send pending changes to external API"""
    project = Project.query.filter_by(id=project_id, user_id=user.id).first()
    
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    
    # Get unsent change logs
    change_logs = ChangeLog.query.filter_by(
        project_id=project_id,
        sent_to_api=False
    ).all()
    
    if not change_logs:
        return jsonify({'message': 'No pending changes to send'}), 200
    
    # Send to API
    results = ComparisonService.send_changes_to_api(change_logs)
    
    return jsonify({
        'message': 'Changes sent to API',
        'results': results
    }), 200

