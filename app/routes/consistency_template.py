from flask import Blueprint, render_template
from app.models.data_consistency import DataConsistencyConfig, DataConsistencyCheck, DataConsistencyResult
from app.models.database_connection import DatabaseConnection
from app.utils.security import login_required_template

consistency_template_bp = Blueprint('consistency_template', __name__)


@consistency_template_bp.route('/consistencia')
@login_required_template
def consistency_page(current_user):
    """Render consistency configuration page"""
    from flask import session
    from app.utils.security import generate_token
    
    # Admins see all connections and configs, regular users see only their own
    if current_user.is_admin:
        connections = DatabaseConnection.query.filter_by(is_active=True).all()
        configs = DataConsistencyConfig.query.filter_by(is_active=True).all()
    else:
        connections = DatabaseConnection.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).all()
        configs = DataConsistencyConfig.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).all()
    
    # Generate token for API calls
    token = session.get('token') or generate_token(current_user)
    
    return render_template('consistency.html', 
                         connections=connections,
                         configs=configs,
                         current_user=current_user,
                         auth_token=token)


@consistency_template_bp.route('/relatorios-consistencia')
@login_required_template
def consistency_reports_page(current_user):
    """Render consistency reports page"""
    from flask import request, session
    from app.utils.security import generate_token
    
    # Admins see all configs, regular users see only their own
    if current_user.is_admin:
        configs = DataConsistencyConfig.query.filter_by(is_active=True).all()
    else:
        configs = DataConsistencyConfig.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).all()
    
    # Get config_id from URL parameter
    config_id_from_url = request.args.get('config_id', type=int)
    
    # Generate token for API calls
    token = session.get('token') or generate_token(current_user)
    
    return render_template('consistency_reports.html', 
                         configs=configs, 
                         current_user=current_user,
                         config_id_from_url=config_id_from_url,
                         auth_token=token)


@consistency_template_bp.route('/consistencia/<int:check_id>/resultados')
@login_required_template
def consistency_results_page(current_user, check_id):
    """Render consistency check results page"""
    try:
        # Get check
        check = DataConsistencyCheck.query.get(check_id)
        
        if not check:
            return render_template('error.html', message='Verificação de consistência não encontrada'), 404
        
        # Verify config ownership - admins can see any, regular users only their own
        config = DataConsistencyConfig.query.get(check.config_id)
        if not config:
            return render_template('error.html', message='Configuração não encontrada', current_user=current_user), 404
        if not current_user.is_admin and config.user_id != current_user.id:
            return render_template('error.html', message='Não autorizado', current_user=current_user), 403
        
        # Get results and convert to dict for template
        results = DataConsistencyResult.query.filter_by(check_id=check_id).order_by(DataConsistencyResult.detected_at.desc()).all()
        results_dict = [result.to_dict() for result in results]
        
        return render_template('consistency_results.html', 
                             check=check,
                             config=config,
                             results=results_dict,
                             current_user=current_user)
    except Exception as e:
        import traceback
        print(f"[CONSISTENCY] Error loading results: {str(e)}")
        print(traceback.format_exc())
        return render_template('error.html', message=f'Erro ao carregar resultados: {str(e)}'), 500

