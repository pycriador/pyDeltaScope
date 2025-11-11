from flask import Blueprint, request, jsonify
from app.models.comparison import Comparison, ComparisonResult
from app.models.change_log import ChangeLog
from app.models.project import Project
from app import db
from app.utils.security import token_required
from sqlalchemy import func, and_
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/project/<int:project_id>/stats', methods=['GET'])
@token_required
def get_project_stats(user, project_id):
    """Get statistics for a project"""
    project = Project.query.filter_by(id=project_id, user_id=user.id).first()
    
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    
    # Get date filters
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    # Build date filter - default to today if no dates provided
    date_filter = None
    if start_date_str:
        try:
            # Handle both 'T' and space separators, and with/without timezone
            start_date_str_clean = start_date_str.replace('T', ' ').split('.')[0]
            start_date = datetime.strptime(start_date_str_clean, '%Y-%m-%d %H:%M:%S')
            date_filter = ChangeLog.detected_at >= start_date
        except Exception as e:
            print(f"Error parsing start_date: {e}")
            pass
    
    if end_date_str:
        try:
            # Handle both 'T' and space separators, and with/without timezone
            end_date_str_clean = end_date_str.replace('T', ' ').split('.')[0]
            end_date = datetime.strptime(end_date_str_clean, '%Y-%m-%d %H:%M:%S')
            if date_filter is not None:
                date_filter = and_(date_filter, ChangeLog.detected_at <= end_date)
            else:
                date_filter = ChangeLog.detected_at <= end_date
        except Exception as e:
            print(f"Error parsing end_date: {e}")
            pass
    
    # If no dates provided, default to today
    if date_filter is None:
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
        date_filter = and_(
            ChangeLog.detected_at >= today_start,
            ChangeLog.detected_at <= today_end
        )
    
    # Get comparison statistics
    total_comparisons = Comparison.query.filter_by(project_id=project_id).count()
    completed_comparisons = Comparison.query.filter_by(
        project_id=project_id,
        status='completed'
    ).count()
    
    # Get total differences
    total_differences = db.session.query(func.sum(Comparison.total_differences)).filter_by(
        project_id=project_id
    ).scalar() or 0
    
    # Get change log statistics with date filter
    query = ChangeLog.query.filter_by(project_id=project_id)
    if date_filter is not None:
        query = query.filter(date_filter)
    
    total_changes = query.count()
    unsent_changes = query.filter_by(sent_to_api=False).count()
    
    # Get unique modified fields count
    modified_fields_query = db.session.query(func.count(func.distinct(ChangeLog.field_name))).filter_by(
        project_id=project_id
    )
    if date_filter is not None:
        modified_fields_query = modified_fields_query.filter(date_filter)
    modified_fields_count = modified_fields_query.scalar() or 0
    
    # Get changes by type
    changes_by_type_query = db.session.query(
        ChangeLog.change_type,
        func.count(ChangeLog.id)
    ).filter_by(project_id=project_id)
    if date_filter is not None:
        changes_by_type_query = changes_by_type_query.filter(date_filter)
    changes_by_type = changes_by_type_query.group_by(ChangeLog.change_type).all()
    
    changes_by_type_dict = {change_type: count for change_type, count in changes_by_type}
    
    # Get recent comparisons
    recent_comparisons = Comparison.query.filter_by(
        project_id=project_id
    ).order_by(Comparison.executed_at.desc()).limit(5).all()
    
    return jsonify({
        'project_id': project_id,
        'total_comparisons': total_comparisons,
        'completed_comparisons': completed_comparisons,
        'total_differences': total_differences,
        'total_changes': total_changes,
        'unsent_changes': unsent_changes,
        'modified_fields_count': modified_fields_count,
        'changes_by_type': changes_by_type_dict,
        'recent_comparisons': [comp.to_dict() for comp in recent_comparisons]
    }), 200


@dashboard_bp.route('/project/<int:project_id>/changes-over-time', methods=['GET'])
@token_required
def get_changes_over_time(user, project_id):
    """Get changes over time for charting"""
    project = Project.query.filter_by(id=project_id, user_id=user.id).first()
    
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    
    # Get date range from query params
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    # Build date filter - default to today if no dates provided
    if start_date_str:
        try:
            # Handle both 'T' and space separators, and with/without timezone
            start_date_str_clean = start_date_str.replace('T', ' ').split('.')[0]
            start_date = datetime.strptime(start_date_str_clean, '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            print(f"Error parsing start_date: {e}")
            # Default to today start
            start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        # Default to today start
        start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    if end_date_str:
        try:
            # Handle both 'T' and space separators, and with/without timezone
            end_date_str_clean = end_date_str.replace('T', ' ').split('.')[0]
            end_date = datetime.strptime(end_date_str_clean, '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            print(f"Error parsing end_date: {e}")
            # Default to today end
            end_date = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
    else:
        # Default to today end
        end_date = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
    
    query_filter = and_(
        ChangeLog.project_id == project_id,
        ChangeLog.detected_at >= start_date,
        ChangeLog.detected_at <= end_date
    )
    
    # Query changes grouped by date
    changes_by_date = db.session.query(
        func.date(ChangeLog.detected_at).label('date'),
        func.count(ChangeLog.id).label('count'),
        ChangeLog.change_type
    ).filter(query_filter).group_by(
        func.date(ChangeLog.detected_at),
        ChangeLog.change_type
    ).order_by('date').all()
    
    # Format data for chart
    chart_data = {}
    for date, count, change_type in changes_by_date:
        # Handle date object or string
        if isinstance(date, str):
            date_str = date
        elif hasattr(date, 'isoformat'):
            date_str = date.isoformat()
        else:
            # Convert to string if it's a date object
            date_str = str(date)
        
        if date_str not in chart_data:
            chart_data[date_str] = {}
        chart_data[date_str][change_type] = count
    
    return jsonify({
        'data': chart_data
    }), 200


@dashboard_bp.route('/project/<int:project_id>/field-changes', methods=['GET'])
@token_required
def get_field_changes(user, project_id):
    """Get changes grouped by field name"""
    project = Project.query.filter_by(id=project_id, user_id=user.id).first()
    
    if not project:
        return jsonify({'message': 'Project not found'}), 404
    
    # Get changes grouped by field
    field_changes = db.session.query(
        ChangeLog.field_name,
        func.count(ChangeLog.id).label('count')
    ).filter_by(project_id=project_id).group_by(ChangeLog.field_name).order_by(
        func.count(ChangeLog.id).desc()
    ).limit(20).all()
    
    return jsonify({
        'data': [{'field': field, 'count': count} for field, count in field_changes]
    }), 200


