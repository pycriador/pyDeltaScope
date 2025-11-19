#!/usr/bin/env python3
"""
Script para fazer backup de tabelas renomeando-as com sufixo _old.

Este script renomeia uma tabela existente adicionando um sufixo padrão (_old)
para indicar que é de uma execução anterior. Isso permite que o get_reports_v2.py
crie uma nova tabela com o nome original.

Uso:
    python3 backup_table.py <table_name>
    python3 backup_table.py report_all_users

Autor: DeltaScope Team
Data: 2025
"""

import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy import inspect, text

# Importar módulo de log personalizado
from modules.logger_config import logger

# Importar módulo do app Flask e configurações do DB
from modules.flask_models import app, db


def backup_table(table_name: str, suffix: str = '_old') -> bool:
    """
    Renomeia uma tabela adicionando um sufixo padrão.
    
    Args:
        table_name: Nome da tabela a ser renomeada
        suffix: Sufixo a ser adicionado (padrão: '_old')
        
    Returns:
        True se a tabela foi renomeada com sucesso, False caso contrário
    """
    try:
        with app.app_context():
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            # Verifica se a tabela existe
            if table_name not in existing_tables:
                logger.warning(f"Tabela '{table_name}' não existe no banco de dados")
                return False
            
            # Gera novo nome da tabela
            new_table_name = f"{table_name}{suffix}"
            
            # Verifica se já existe uma tabela com o novo nome
            if new_table_name in existing_tables:
                # Adiciona timestamp ao sufixo para evitar conflito
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                new_table_name = f"{table_name}{suffix}_{timestamp}"
                logger.info(f"Tabela '{new_table_name}' já existe, usando timestamp: {new_table_name}")
            
            # Detecta tipo do banco de dados
            db_url = str(db.engine.url)
            is_mysql = 'mysql' in db_url.lower() or 'mariadb' in db_url.lower()
            is_postgres = 'postgresql' in db_url.lower() or 'postgres' in db_url.lower()
            is_sqlite = 'sqlite' in db_url.lower()
            
            # Executa RENAME TABLE conforme o tipo de banco
            if is_mysql:
                rename_sql = text(f"RENAME TABLE `{table_name}` TO `{new_table_name}`")
            elif is_postgres:
                rename_sql = text(f'ALTER TABLE "{table_name}" RENAME TO "{new_table_name}"')
            elif is_sqlite:
                rename_sql = text(f'ALTER TABLE "{table_name}" RENAME TO "{new_table_name}"')
            else:
                # Tentativa genérica
                rename_sql = text(f'ALTER TABLE "{table_name}" RENAME TO "{new_table_name}"')
            
            logger.info(f"Renomeando tabela '{table_name}' para '{new_table_name}'...")
            db.session.execute(rename_sql)
            db.session.commit()
            
            logger.info(f"✓ Tabela renomeada com sucesso!")
            logger.info(f"  Antiga: {table_name}")
            logger.info(f"  Nova: {new_table_name}")
            
            return True
            
    except Exception as e:
        logger.error(f"Erro ao renomear tabela '{table_name}': {e}")
        import traceback
        logger.error(traceback.format_exc())
        try:
            db.session.rollback()
        except:
            pass
        return False


def main():
    """
    Função principal do script.
    """
    if len(sys.argv) < 2:
        print("Uso: python3 backup_table.py <table_name> [suffix]")
        print("Exemplo: python3 backup_table.py report_all_users")
        print("Exemplo: python3 backup_table.py report_all_users _backup")
        sys.exit(1)
    
    table_name = sys.argv[1]
    suffix = sys.argv[2] if len(sys.argv) > 2 else '_old'
    
    start_time = datetime.now()
    
    logger.info("=" * 70)
    logger.info("BAMBOOHR - Backup de Tabela")
    logger.info("=" * 70)
    logger.info(f"Iniciado em: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Tabela: {table_name}")
    logger.info(f"Sufixo: {suffix}")
    logger.info("")
    
    try:
        success = backup_table(table_name, suffix)
        
        if success:
            logger.info("")
            logger.info("=" * 70)
            logger.info("Backup concluído com sucesso!")
            logger.info("=" * 70)
            logger.info("")
            logger.info("Agora você pode executar get_reports_v2.py para criar a nova tabela")
        else:
            logger.error("")
            logger.error("=" * 70)
            logger.error("Falha ao fazer backup da tabela")
            logger.error("=" * 70)
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Erro fatal no script: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
    
    finally:
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info("")
        logger.info("=" * 70)
        logger.info(f"Finalizado em: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Duração total: {duration}")
        logger.info("=" * 70)


if __name__ == '__main__':
    main()

