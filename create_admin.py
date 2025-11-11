#!/usr/bin/env python3
"""
Interactive script to create an admin user
Usage: python create_admin.py
"""
import sys
import os
import getpass
from app import create_app, db
from app.models.user import User
from app.models.group import Group

def validate_email(email):
    """Basic email validation"""
    if '@' not in email or '.' not in email.split('@')[1]:
        return False
    return True

def create_admin_interactive():
    """Interactive function to create admin user"""
    app = create_app(os.getenv('FLASK_ENV', 'default'))
    
    with app.app_context():
        print("="*60)
        print("Criação de Usuário Administrador")
        print("="*60)
        print()
        
        # Check if admin already exists
        existing_admins = User.query.filter_by(is_admin=True).all()
        if existing_admins:
            print(f"ATENÇÃO: Já existem {len(existing_admins)} usuário(s) administrador(es) no sistema.")
            response = input("Deseja criar outro administrador? (s/N): ").strip().lower()
            if response not in ['s', 'sim', 'y', 'yes']:
                print("Operação cancelada.")
                return
        
        # Get username
        while True:
            username = input("Usuário: ").strip()
            if not username:
                print("Erro: O nome de usuário não pode estar vazio.")
                continue
            if len(username) < 3:
                print("Erro: O nome de usuário deve ter pelo menos 3 caracteres.")
                continue
            
            # Check if username already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print(f"Erro: O usuário '{username}' já existe.")
                response = input("Deseja tentar outro nome? (s/N): ").strip().lower()
                if response not in ['s', 'sim', 'y', 'yes']:
                    print("Operação cancelada.")
                    return
                continue
            
            break
        
        # Get email
        while True:
            email = input("Email: ").strip()
            if not email:
                print("Erro: O email não pode estar vazio.")
                continue
            if not validate_email(email):
                print("Erro: Email inválido. Use o formato: usuario@exemplo.com")
                continue
            
            # Check if email already exists
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                print(f"Erro: O email '{email}' já está em uso.")
                response = input("Deseja tentar outro email? (s/N): ").strip().lower()
                if response not in ['s', 'sim', 'y', 'yes']:
                    print("Operação cancelada.")
                    return
                continue
            
            break
        
        # Get password
        while True:
            password = getpass.getpass("Senha: ")
            if not password:
                print("Erro: A senha não pode estar vazia.")
                continue
            if len(password) < 6:
                print("Erro: A senha deve ter pelo menos 6 caracteres.")
                continue
            
            password_confirm = getpass.getpass("Confirmar senha: ")
            if password != password_confirm:
                print("Erro: As senhas não coincidem.")
                response = input("Deseja tentar novamente? (s/N): ").strip().lower()
                if response not in ['s', 'sim', 'y', 'yes']:
                    print("Operação cancelada.")
                    return
                continue
            
            break
        
        # Confirm creation
        print()
        print("Resumo:")
        print(f"  Usuário: {username}")
        print(f"  Email: {email}")
        print(f"  Tipo: Administrador")
        print()
        
        confirm = input("Confirmar criação? (S/n): ").strip().lower()
        if confirm in ['n', 'nao', 'no', 'não']:
            print("Operação cancelada.")
            return
        
        # Create admin user
        try:
            admin = User(
                username=username,
                email=email,
                is_admin=True,
                is_active=True
            )
            admin.set_password(password)
            
            # Verify password was set correctly
            if not admin.password_hash:
                raise Exception("Erro ao definir hash da senha")
            
            # Test password verification before committing
            if not admin.check_password(password):
                raise Exception("Erro: Verificação de senha falhou após criação")
            
            db.session.add(admin)
            db.session.commit()
            
            # Verify user was saved correctly
            saved_user = User.query.filter_by(username=username).first()
            if not saved_user:
                raise Exception("Erro: Usuário não foi salvo no banco de dados")
            
            # Test password verification on saved user
            if not saved_user.check_password(password):
                raise Exception("Erro: Verificação de senha falhou após salvar no banco")
            
            # Add admin to Administradores group if it exists
            admin_group = Group.query.filter_by(name='Administradores').first()
            if admin_group:
                admin_group.users.append(saved_user)
                db.session.commit()
                print(f"Usuário adicionado ao grupo 'Administradores'.")
            
            print()
            print("="*60)
            print("✓ Usuário administrador criado com sucesso!")
            print("="*60)
            print(f"  Usuário: {username}")
            print(f"  Email: {email}")
            print(f"  É Admin: Sim")
            print(f"  Status: Ativo")
            print(f"  ID: {saved_user.id}")
            print()
            print("Teste de login:")
            print(f"  Verificação de senha: {'✓ OK' if saved_user.check_password(password) else '✗ FALHOU'}")
            print()
            
        except Exception as e:
            db.session.rollback()
            print()
            print("="*60)
            print("✗ Erro ao criar usuário administrador")
            print("="*60)
            print(f"Erro: {str(e)}")
            import traceback
            print()
            print("Detalhes do erro:")
            print(traceback.format_exc())
            sys.exit(1)

if __name__ == '__main__':
    try:
        create_admin_interactive()
    except KeyboardInterrupt:
        print()
        print("\nOperação cancelada pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\nErro inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

