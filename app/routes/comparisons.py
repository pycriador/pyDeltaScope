from flask import Blueprint, request, jsonify
from app.models.comparison import Comparison, ComparisonResult, ComparisonProfile
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
    """Run comparison for a project - admins can run any project"""
    if user.is_admin:
        project = Project.query.filter_by(id=project_id, is_active=True).first()
    else:
        project = Project.query.filter_by(id=project_id, user_id=user.id, is_active=True).first()
    
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    
    try:
        # Get primary keys and table names from request or use project defaults
        data = request.get_json() or {}
        primary_keys = data.get('primary_keys', [])
        key_mappings = data.get('key_mappings', {})  # Mapping from source to target column names
        ignored_columns = data.get('ignored_columns', [])  # Columns to ignore during comparison
        source_table = data.get('source_table', project.source_table)
        target_table = data.get('target_table', project.target_table)
        
        print(f"[MANUAL_COMPARISON] ========== MANUAL COMPARISON START ==========", flush=True)
        print(f"[MANUAL_COMPARISON] Starting manual comparison for project {project_id}", flush=True)
        print(f"[MANUAL_COMPARISON] Source table: {source_table}, Target table: {target_table}", flush=True)
        print(f"[MANUAL_COMPARISON] Key mappings from request: {key_mappings}", flush=True)
        print(f"[MANUAL_COMPARISON] Key mappings type: {type(key_mappings)}, empty: {not key_mappings}, length: {len(key_mappings) if isinstance(key_mappings, dict) else 0}", flush=True)
        if key_mappings:
            print(f"[MANUAL_COMPARISON] Key mappings content: {list(key_mappings.items())}", flush=True)
        else:
            print(f"[MANUAL_COMPARISON] WARNING: Key mappings are EMPTY!", flush=True)
        
        # Get connection configs
        source_config = project.source_connection.get_decrypted_config()
        source_config['type'] = project.source_connection.db_type
        
        target_config = project.target_connection.get_decrypted_config()
        target_config['type'] = project.target_connection.db_type
        
        # If not provided, try to get from source table (already decrypted)
        if not primary_keys:
            source_engine = DatabaseService.get_engine(source_config, already_decrypted=True)
            primary_keys = DatabaseService.get_primary_keys(source_engine, source_table)
        
        print(f"[MANUAL_COMPARISON] Primary keys: {primary_keys}", flush=True)
        print(f"[MANUAL_COMPARISON] Starting comparison with key_mappings={key_mappings}...", flush=True)
        
        # Run comparison with key mappings and ignored columns
        differences_df, differences = ComparisonService.compare_tables(
            source_config,
            target_config,
            source_table,
            target_table,
            primary_keys,
            key_mappings,
            ignored_columns
        )
        
        print(f"[MANUAL_COMPARISON] Comparison completed. Differences found: {len(differences)}", flush=True)
        print(f"[MANUAL_COMPARISON] DataFrame shape: {differences_df.shape if not differences_df.empty else 'empty'}", flush=True)
        
        # Save results
        comparison = ComparisonService.save_comparison_results(
            project_id,
            differences,
            metadata={
                'primary_keys': primary_keys,
                'key_mappings': key_mappings,
                'ignored_columns': ignored_columns,
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


@comparisons_bp.route('/project/<int:project_id>', methods=['DELETE'])
@token_required
def delete_all_comparisons(user, project_id):
    """Delete all comparisons for a project"""
    project = Project.query.filter_by(id=project_id, user_id=user.id).first()
    
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    
    try:
        # Get all comparisons ONLY for this specific project
        comparisons = Comparison.query.filter_by(project_id=project_id).all()
        comparison_ids = [comp.id for comp in comparisons]
        
        if not comparison_ids:
            return jsonify({
                'message': 'No comparisons found for this project',
                'deleted_count': 0
            }), 200
        
        print(f"[DELETE_ALL_COMPARISONS] Deleting {len(comparison_ids)} comparisons for project {project_id} only", flush=True)
        
        # Delete related change logs first (only for this project's comparisons)
        deleted_change_logs = 0
        for comparison_id in comparison_ids:
            change_logs = ChangeLog.query.filter_by(comparison_id=comparison_id).all()
            for change_log in change_logs:
                db.session.delete(change_log)
                deleted_change_logs += 1
        
        # Delete all comparisons for this project only (cascade will delete results)
        for comparison in comparisons:
            db.session.delete(comparison)
        
        db.session.commit()
        
        print(f"[DELETE_ALL_COMPARISONS] Successfully deleted {len(comparison_ids)} comparisons and {deleted_change_logs} change logs for project {project_id}", flush=True)
        
        return jsonify({
            'message': f'All comparisons for project "{project.name}" deleted successfully',
            'deleted_count': len(comparison_ids),
            'project_id': project_id,
            'project_name': project.name
        }), 200
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"[DELETE_ALL_COMPARISONS] Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'message': f'Error deleting comparisons: {str(e)}'}), 500


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


@comparisons_bp.route('/<int:comparison_id>', methods=['DELETE'])
@token_required
def delete_comparison(user, comparison_id):
    """Delete a comparison and its results"""
    comparison = Comparison.query.get(comparison_id)
    
    if not comparison:
        return jsonify({'message': 'Comparison not found'}), 404
    
    # Verify project ownership
    project = Project.query.get(comparison.project_id)
    if not project or project.user_id != user.id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    try:
        # Delete related change logs first (if any)
        change_logs = ChangeLog.query.filter_by(comparison_id=comparison_id).all()
        for change_log in change_logs:
            db.session.delete(change_log)
        
        # Delete comparison (cascade will delete results)
        db.session.delete(comparison)
        db.session.commit()
        
        return jsonify({
            'message': 'Comparison deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"[DELETE_COMPARISON] Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'message': f'Error deleting comparison: {str(e)}'}), 500


# ============================================================================
# COMPARISON PROFILES API
# ============================================================================

@comparisons_bp.route('/profiles/project/<int:project_id>', methods=['GET'])
@token_required
def get_comparison_profiles(user, project_id):
    """Get all comparison profiles for a project - admins can see all"""
    if user.is_admin:
        project = Project.query.filter_by(id=project_id, is_active=True).first()
    else:
        project = Project.query.filter_by(id=project_id, user_id=user.id, is_active=True).first()
    
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    
    profiles = ComparisonProfile.query.filter_by(
        project_id=project_id,
        is_active=True
    ).order_by(ComparisonProfile.created_at.desc()).all()
    
    return jsonify({
        'profiles': [profile.to_dict() for profile in profiles]
    }), 200


@comparisons_bp.route('/profiles/<int:profile_id>', methods=['GET'])
@token_required
def get_comparison_profile(user, profile_id):
    """Get a specific comparison profile"""
    profile = ComparisonProfile.query.get(profile_id)
    
    if not profile:
        return jsonify({'message': 'Profile not found'}), 404
    
    # Verify project ownership - admins can access any project
    project = Project.query.get(profile.project_id)
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    if not user.is_admin and project.user_id != user.id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    return jsonify({
        'profile': profile.to_dict()
    }), 200


@comparisons_bp.route('/profiles', methods=['POST'])
@token_required
def create_comparison_profile(user):
    """Create a new comparison profile"""
    data = request.get_json() or {}
    
    project_id = data.get('project_id')
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    primary_keys = data.get('primary_keys', [])
    key_mappings = data.get('key_mappings', {})
    ignored_columns = data.get('ignored_columns', [])
    
    if not project_id:
        return jsonify({'message': 'project_id is required'}), 400
    
    if not name:
        return jsonify({'message': 'name is required'}), 400
    
    if not primary_keys:
        return jsonify({'message': 'primary_keys is required'}), 400
    
    # Verify project ownership - admins can access any project
    if user.is_admin:
        project = Project.query.filter_by(id=project_id, is_active=True).first()
    else:
        project = Project.query.filter_by(id=project_id, user_id=user.id, is_active=True).first()
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    
    # Check if profile with same name already exists
    existing = ComparisonProfile.query.filter_by(
        project_id=project_id,
        name=name,
        is_active=True
    ).first()
    
    if existing:
        return jsonify({'message': 'Profile with this name already exists'}), 400
    
    try:
        profile = ComparisonProfile(
            project_id=project_id,
            name=name,
            description=description,
            primary_keys=primary_keys,
            key_mappings=key_mappings,
            ignored_columns=ignored_columns,
            created_by=user.id
        )
        
        db.session.add(profile)
        db.session.commit()
        
        return jsonify({
            'message': 'Profile created successfully',
            'profile': profile.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error creating profile: {str(e)}'}), 500


@comparisons_bp.route('/profiles/<int:profile_id>', methods=['PUT'])
@token_required
def update_comparison_profile(user, profile_id):
    """Update a comparison profile"""
    profile = ComparisonProfile.query.get(profile_id)
    
    if not profile:
        return jsonify({'message': 'Profile not found'}), 404
    
    # Verify project ownership - admins can access any project
    project = Project.query.get(profile.project_id)
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    if not user.is_admin and project.user_id != user.id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json() or {}
    
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    primary_keys = data.get('primary_keys')
    key_mappings = data.get('key_mappings')
    ignored_columns = data.get('ignored_columns')
    
    try:
        if name and name != profile.name:
            # Check if another profile with same name exists
            existing = ComparisonProfile.query.filter_by(
                project_id=profile.project_id,
                name=name,
                is_active=True
            ).filter(ComparisonProfile.id != profile_id).first()
            
            if existing:
                return jsonify({'message': 'Profile with this name already exists'}), 400
            
            profile.name = name
        
        if description is not None:
            profile.description = description
        
        if primary_keys is not None:
            profile.primary_keys = primary_keys
        
        if key_mappings is not None:
            profile.key_mappings = key_mappings
        
        if ignored_columns is not None:
            profile.ignored_columns = ignored_columns
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'profile': profile.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating profile: {str(e)}'}), 500


@comparisons_bp.route('/profiles/<int:profile_id>', methods=['DELETE'])
@token_required
def delete_comparison_profile(user, profile_id):
    """Delete (deactivate) a comparison profile"""
    profile = ComparisonProfile.query.get(profile_id)
    
    if not profile:
        return jsonify({'message': 'Profile not found'}), 404
    
    # Verify project ownership - admins can access any project
    project = Project.query.get(profile.project_id)
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    if not user.is_admin and project.user_id != user.id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    try:
        profile.is_active = False
        db.session.commit()
        
        return jsonify({
            'message': 'Profile deleted successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error deleting profile: {str(e)}'}), 500

