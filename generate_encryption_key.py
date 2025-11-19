#!/usr/bin/env python3
"""
Script to generate a strong and secure ENCRYPTION_KEY for DeltaScope

This script generates a Fernet-compatible encryption key that can be used
to encrypt database passwords securely.

Usage:
    python generate_encryption_key.py

The generated key will be displayed and optionally saved to .env file.
"""

import secrets
import base64
import os
from pathlib import Path
from cryptography.fernet import Fernet


def generate_encryption_key():
    """
    Generate a strong encryption key compatible with Fernet
    
    Returns:
        str: Base64-encoded encryption key (32 bytes)
    """
    # Generate 32 random bytes using cryptographically secure random
    key_bytes = secrets.token_bytes(32)
    
    # Encode to base64 URL-safe format (Fernet format)
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    
    return fernet_key.decode('utf-8')


def generate_fernet_key():
    """
    Generate a Fernet key using the cryptography library
    
    Returns:
        str: Base64-encoded Fernet key
    """
    return Fernet.generate_key().decode('utf-8')


def save_to_env(key: str, env_file: Path = None):
    """
    Save encryption key to .env file
    
    Args:
        key: The encryption key to save
        env_file: Path to .env file (default: .env in project root)
    """
    if env_file is None:
        # Get project root (parent of this script)
        script_dir = Path(__file__).parent
        env_file = script_dir / '.env'
    
    # Read existing .env file if it exists
    env_content = []
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            env_content = f.readlines()
    
    # Check if ENCRYPTION_KEY already exists
    key_found = False
    updated_content = []
    
    for line in env_content:
        if line.strip().startswith('ENCRYPTION_KEY='):
            # Replace existing key
            updated_content.append(f'ENCRYPTION_KEY={key}\n')
            key_found = True
        else:
            updated_content.append(line)
    
    # If key not found, append it
    if not key_found:
        # Add newline if file doesn't end with one
        if updated_content and not updated_content[-1].endswith('\n'):
            updated_content.append('\n')
        updated_content.append(f'ENCRYPTION_KEY={key}\n')
    
    # Write back to file
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(updated_content)
    
    return env_file


def main():
    """Main function to generate and optionally save encryption key"""
    print("=" * 70)
    print("DeltaScope - Gerador de Chave de Criptografia")
    print("=" * 70)
    print()
    
    # Generate key using Fernet (recommended method)
    print("Gerando chave de criptografia forte e segura...")
    encryption_key = generate_fernet_key()
    
    print()
    print("✓ Chave gerada com sucesso!")
    print()
    print("-" * 70)
    print("SUA CHAVE DE CRIPTOGRAFIA:")
    print("-" * 70)
    print(encryption_key)
    print("-" * 70)
    print()
    
    # Security warnings
    print("⚠️  AVISOS IMPORTANTES:")
    print("   1. Guarde esta chave em local seguro!")
    print("   2. Se perder esta chave, não será possível descriptografar")
    print("      senhas de banco de dados já salvas.")
    print("   3. NÃO compartilhe esta chave publicamente.")
    print("   4. Use variáveis de ambiente ou gerenciador de segredos")
    print("      em produção.")
    print()
    
    # Ask if user wants to save to .env
    env_file = Path(__file__).parent / '.env'
    
    if env_file.exists():
        print(f"📄 Arquivo .env encontrado: {env_file}")
        response = input("Deseja salvar a chave no arquivo .env? (s/N): ").strip().lower()
        
        if response in ['s', 'sim', 'y', 'yes']:
            try:
                save_to_env(encryption_key, env_file)
                print(f"✓ Chave salva com sucesso em {env_file}")
                print()
                print("⚠️  Lembre-se de:")
                print("   - Adicionar .env ao .gitignore (se ainda não estiver)")
                print("   - Não commitar o arquivo .env no controle de versão")
                print("   - Fazer backup seguro da chave")
            except Exception as e:
                print(f"✗ Erro ao salvar chave: {e}")
                print("   Por favor, adicione manualmente ao .env:")
                print(f"   ENCRYPTION_KEY={encryption_key}")
        else:
            print()
            print("Para usar esta chave, adicione ao seu arquivo .env:")
            print(f"ENCRYPTION_KEY={encryption_key}")
    else:
        print(f"📄 Arquivo .env não encontrado em: {env_file}")
        response = input("Deseja criar o arquivo .env com esta chave? (s/N): ").strip().lower()
        
        if response in ['s', 'sim', 'y', 'yes']:
            try:
                save_to_env(encryption_key, env_file)
                print(f"✓ Arquivo .env criado com sucesso em {env_file}")
                print()
                print("⚠️  Lembre-se de:")
                print("   - Adicionar .env ao .gitignore")
                print("   - Não commitar o arquivo .env no controle de versão")
                print("   - Fazer backup seguro da chave")
            except Exception as e:
                print(f"✗ Erro ao criar arquivo .env: {e}")
                print("   Por favor, crie manualmente o arquivo .env com:")
                print(f"   ENCRYPTION_KEY={encryption_key}")
        else:
            print()
            print("Para usar esta chave, crie um arquivo .env com:")
            print(f"ENCRYPTION_KEY={encryption_key}")
    
    print()
    print("=" * 70)
    print("Geração de chave concluída!")
    print("=" * 70)


if __name__ == '__main__':
    main()

