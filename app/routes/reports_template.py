from flask import Blueprint, render_template, jsonify
from app.models.project import Project
from app.models.comparison import Comparison, ComparisonResult
from app.utils.security import login_required_template

reports_template_bp = Blueprint('reports_template', __name__)


@reports_template_bp.route('/relatorios')
@login_required_template
def reports_page(current_user):
    """Render reports page"""
    projects = Project.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    return render_template('reports.html', projects=projects, current_user=current_user)


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
        
        return render_template('comparison_results.html', 
                             comparison=comparison, 
                             results=results,
                             project=project,
                             current_user=current_user)
    except Exception as e:
        import traceback
        print(f"[REPORTS] Error loading comparison results: {str(e)}")
        print(traceback.format_exc())
        return render_template('error.html', message=f'Erro ao carregar resultados: {str(e)}'), 500

