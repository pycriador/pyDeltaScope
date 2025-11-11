from flask import Blueprint, render_template
from app.utils.security import login_required_template

webhooks_template_bp = Blueprint('webhooks_template', __name__)


@webhooks_template_bp.route('/webhooks')
@login_required_template
def webhooks_client_page(current_user):
    """Render webhook client page (Postman-like)"""
    return render_template('webhooks_client.html', current_user=current_user)


@webhooks_template_bp.route('/webhooks/payloads')
@login_required_template
def webhooks_payloads_page(current_user):
    """Render webhook payloads management page"""
    return render_template('webhooks_payloads.html', current_user=current_user)


@webhooks_template_bp.route('/webhooks/params')
@login_required_template
def webhooks_params_page(current_user):
    """Render webhook parameters management page"""
    return render_template('webhooks_params.html', current_user=current_user)

