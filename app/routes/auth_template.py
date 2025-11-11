from flask import Blueprint, render_template, redirect, session, request, flash
from app.models.user import User
from app import db
from app.utils.security import generate_token

auth_template_bp = Blueprint('auth_template', __name__)


def check_if_logged_in():
    """Helper function to check if user is already logged in"""
    user_id = session.get('user_id')
    if user_id:
        try:
            user = User.query.get(int(user_id))
            if user and user.is_active:
                return True
        except Exception:
            pass
    return False


@auth_template_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    """Render login page and handle login form submission"""
    # If already logged in, redirect to home
    if check_if_logged_in():
        return redirect('/')
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            return render_template('login.html', error='Preencha todos os campos')
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return render_template('login.html', error='Usuário ou senha incorretos')
        
        if not user.is_active:
            return render_template('login.html', error='Usuário inativo. Entre em contato com o administrador.')
        
        # Check password
        if not user.check_password(password):
            return render_template('login.html', error='Usuário ou senha incorretos')
        
        # Login successful - set session
        token = generate_token(user)
        session['user_id'] = user.id
        session['token'] = token
        session.permanent = True
        
        # Redirect to home page
        return redirect('/home')
    
    # GET request - show login form
    return render_template('login.html')


@auth_template_bp.route('/create_user', methods=['GET', 'POST'])
def create_user_page():
    """Render create user page and handle registration form submission"""
    # If already logged in, redirect to home
    if check_if_logged_in():
        return redirect('/')
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Validation
        if not username or not email or not password:
            return render_template('create_user_auth.html', error='Preencha todos os campos')
        
        if len(password) < 6:
            return render_template('create_user_auth.html', error='A senha deve ter pelo menos 6 caracteres')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return render_template('create_user_auth.html', error='Nome de usuário já existe')
        
        if User.query.filter_by(email=email).first():
            return render_template('create_user_auth.html', error='Email já cadastrado')
        
        # Create new user
        try:
            from app.models.group import Group, user_groups
            
            user = User(
                username=username,
                email=email,
                is_admin=False,
                is_active=True
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.flush()  # Get user ID
            
            # Add user to "Usuários Básicos" group (no permissions, only view home)
            basic_group = Group.query.filter_by(name='Usuários Básicos').first()
            if not basic_group:
                # Create the group if it doesn't exist
                basic_group = Group(
                    name='Usuários Básicos',
                    description='Usuários com acesso limitado - apenas visualização da tela inicial',
                    can_create_connections=False,
                    can_create_projects=False,
                    can_view_dashboards=False,
                    can_edit_tables=False,
                    can_view_tables=False,
                    can_view_reports=False,
                    can_download_reports=False
                )
                db.session.add(basic_group)
                db.session.flush()
            
            # Add user to group
            basic_group.users.append(user)
            db.session.commit()
            
            # Show success message and redirect to login
            return render_template('create_user_auth.html', success='Usuário criado com sucesso! Redirecionando para login...')
        except Exception as e:
            db.session.rollback()
            import traceback
            print(f"[CREATE USER ERROR] {str(e)}")
            print(traceback.format_exc())
            return render_template('create_user_auth.html', error=f'Erro ao criar usuário: {str(e)}')
    
    # GET request - show create user form
    return render_template('create_user_auth.html')

