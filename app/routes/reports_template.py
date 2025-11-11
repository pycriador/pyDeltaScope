from flask import Blueprint, render_template, jsonify
from app.models.project import Project
from app.models.comparison import Comparison, ComparisonResult
from app.models.scheduled_task import ScheduledTask
from app.utils.security import login_required_template

reports_template_bp = Blueprint('reports_template', __name__)


@reports_template_bp.route('/relatorios')
@login_required_template
def reports_page(current_user):
    """Render reports page"""
    from flask import request
    
    projects = Project.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    
    # Get project_id from URL parameter
    project_id_from_url = request.args.get('project_id', type=int)
    
    return render_template('reports.html', 
                         projects=projects, 
                         current_user=current_user,
                         project_id_from_url=project_id_from_url)


@reports_template_bp.route('/relatorios/<int:comparison_id>/resultados')
@login_required_template
def comparison_results_page(current_user, comparison_id):
    """Render comparison results page"""
    try:
        # Get comparison
        comparison = Comparison.query.get(comparison_id)
        
        if not comparison:
            return render_template('error.html', message='Comparação não encontrada'), 404
        
        # Verify project ownership
        project = Project.query.get(comparison.project_id)
        if not project or project.user_id != current_user.id:
            return render_template('error.html', message='Não autorizado'), 403
        
        # Get results
        results = ComparisonResult.query.filter_by(comparison_id=comparison_id).order_by(ComparisonResult.detected_at.desc()).all()
        
        print(f"[REPORTS] Loading results for comparison {comparison_id}")
        print(f"[REPORTS] Comparison total_differences: {comparison.total_differences}")
        print(f"[REPORTS] Results found in database: {len(results)}")
        
        # Check if comparison was executed by a scheduled task
        scheduled_task = None
        if comparison.comparison_metadata and isinstance(comparison.comparison_metadata, dict):
            scheduled_task_id = comparison.comparison_metadata.get('scheduled_task_id')
            if scheduled_task_id:
                scheduled_task = ScheduledTask.query.get(scheduled_task_id)
        
        return render_template('comparison_results.html', 
                             comparison=comparison, 
                             results=results,
                             project=project,
                             scheduled_task=scheduled_task,
                             current_user=current_user)
    except Exception as e:
        import traceback
        print(f"[REPORTS] Error loading comparison results: {str(e)}")
        print(traceback.format_exc())
        return render_template('error.html', message=f'Erro ao carregar resultados: {str(e)}'), 500

