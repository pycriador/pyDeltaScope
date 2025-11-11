from flask import Blueprint, render_template
from app.models.project import Project
from app.utils.security import login_required_template

comparison_template_bp = Blueprint('comparison_template', __name__)


@comparison_template_bp.route('/comparacao')
@login_required_template
def comparison_page(current_user):
    """Render comparison page"""
    projects = Project.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    return render_template('comparison.html', projects=projects, current_user=current_user)

