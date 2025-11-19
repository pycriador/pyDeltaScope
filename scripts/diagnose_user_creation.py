"""
Script to diagnose user creation issues
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from sqlalchemy import inspect, text
from werkzeug.security import generate_password_hash

def diagnose_user_creation():
    """Diagnose potential issues with user creation"""
    app = create_app()
    with app.app_context():
        print("=== DIAGNÓSTICO DE CRIAÇÃO DE USUÁRIO ===\n")
        
        # 1. Check table structure
        print("1. Verificando estrutura da tabela 'users':")
        inspector = inspect(db.engine)
        if 'users' not in inspector.get_table_names():
            print("   ❌ ERRO: Tabela 'users' não existe!")
            return
        
        columns = inspector.get_columns('users')
        print(f"   ✓ Tabela existe com {len(columns)} colunas")
        
        id_col = next((c for c in columns if c['name'] == 'id'), None)
        if id_col:
            print(f"   - Coluna 'id': tipo={id_col['type']}, primary_key={id_col.get('primary_key', False)}, autoincrement={id_col.get('autoincrement', False)}")
        else:
            print("   ❌ ERRO: Coluna 'id' não encontrada!")
        
        username_col = next((c for c in columns if c['name'] == 'username'), None)
        if username_col:
            print(f"   - Coluna 'username': tipo={username_col['type']}, nullable={username_col.get('nullable', True)}, unique={username_col.get('unique', False)}")
        
        email_col = next((c for c in columns if c['name'] == 'email'), None)
        if email_col:
            print(f"   - Coluna 'email': tipo={email_col['type']}, nullable={email_col.get('nullable', True)}, unique={email_col.get('unique', False)}")
        
        # 2. Check existing users
        print("\n2. Verificando usuários existentes:")
        try:
            result = db.session.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar()
            print(f"   ✓ Total de usuários: {count}")
            
            if count > 0:
                result2 = db.session.execute(text("SELECT id, username, email, is_active FROM users ORDER BY id DESC LIMIT 5"))
                rows = result2.fetchall()
                print("   Últimos 5 usuários:")
                for row in rows:
                    print(f"     - ID: {row[0]}, Username: {row[1]}, Email: {row[2]}, Ativo: {row[3]}")
        except Exception as e:
            print(f"   ❌ ERRO ao consultar usuários: {e}")
        
        # 3. Check for duplicate usernames/emails
        print("\n3. Verificando duplicatas:")
        try:
            result = db.session.execute(text("SELECT username, COUNT(*) as cnt FROM users GROUP BY username HAVING cnt > 1"))
            duplicates = result.fetchall()
            if duplicates:
                print(f"   ⚠️  Usernames duplicados encontrados:")
                for dup in duplicates:
                    print(f"     - {dup[0]}: {dup[1]} ocorrências")
            else:
                print("   ✓ Nenhum username duplicado")
            
            result = db.session.execute(text("SELECT email, COUNT(*) as cnt FROM users GROUP BY email HAVING cnt > 1"))
            duplicates = result.fetchall()
            if duplicates:
                print(f"   ⚠️  Emails duplicados encontrados:")
                for dup in duplicates:
                    print(f"     - {dup[0]}: {dup[1]} ocorrências")
            else:
                print("   ✓ Nenhum email duplicado")
        except Exception as e:
            print(f"   ❌ ERRO ao verificar duplicatas: {e}")
        
        # 4. Test user creation (dry run)
        print("\n4. Testando criação de usuário (dry run):")
        try:
            test_username = f"test_user_{db.session.execute(text('SELECT COALESCE(MAX(id), 0) + 1 FROM users')).scalar()}"
            test_email = f"test_{db.session.execute(text('SELECT COALESCE(MAX(id), 0) + 1 FROM users')).scalar()}@test.com"
            
            # Check if test user already exists
            existing = User.query.filter_by(username=test_username).first()
            if existing:
                print(f"   ⚠️  Usuário de teste '{test_username}' já existe, pulando teste")
            else:
                print(f"   Tentando criar usuário de teste: {test_username}")
                test_user = User(
                    username=test_username,
                    email=test_email,
                    is_admin=False,
                    is_active=True
                )
                test_user.set_password("test123")
                
                db.session.add(test_user)
                db.session.flush()
                
                if test_user.id:
                    print(f"   ✓ ID gerado: {test_user.id}")
                    # Rollback - não salvar o usuário de teste
                    db.session.rollback()
                    print("   ✓ Rollback realizado (usuário de teste não foi salvo)")
                else:
                    print("   ❌ ERRO: ID não foi gerado após flush()")
                    db.session.rollback()
        except Exception as e:
            import traceback
            print(f"   ❌ ERRO ao testar criação: {e}")
            print(traceback.format_exc())
            db.session.rollback()
        
        # 5. Check database type and connection
        print("\n5. Informações do banco de dados:")
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        db_type = 'unknown'
        if 'sqlite' in db_uri.lower():
            db_type = 'SQLite'
        elif 'mysql' in db_uri.lower() or 'mariadb' in db_uri.lower():
            db_type = 'MySQL/MariaDB'
        print(f"   Tipo: {db_type}")
        print(f"   URI: {db_uri.split('@')[-1] if '@' in db_uri else db_uri.split('///')[-1]}")
        
        print("\n=== FIM DO DIAGNÓSTICO ===")

if __name__ == '__main__':
    diagnose_user_creation()

