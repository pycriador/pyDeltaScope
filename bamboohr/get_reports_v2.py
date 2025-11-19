#!/usr/bin/env python3
"""
Versão melhorada do get_reports.py que utiliza modelos SQLAlchemy gerados dinamicamente.

Este script:
- Carrega o modelo gerado dinamicamente pelo sync_report_dynamic.py
- Armazena dados estruturados nas colunas do modelo
- Armazena JSON completo em coluna raw_data para backup/auditoria
- Não utiliza pandas - apenas SQLAlchemy ORM

Características:
- Usa modelos SQLAlchemy gerados automaticamente
- Armazena JSON completo em coluna raw_data
- Suporte a append ou replace
- Logging detalhado
- Tratamento de erros robusto

Autor: DeltaScope Team
Data: 2025
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import json
import locale
from pathlib import Path
import importlib.util
import sys

# Importar módulo de log personalizado
from modules.logger_config import logger

# Importar módulo do app Flask e configurações do DB
from modules.flask_models import app, db

# Importar módulo BambooHR para buscar dados
from modules.bamboohr import bamboohr_get_report

# Importar modelos do banco de dados
from modules.db_models import InsertLog


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def get_utcnow() -> datetime:
    """
    Retorna datetime UTC atual de forma compatível com diferentes versões do Python.
    
    Python 3.12+: datetime.now(timezone.utc) (recomendado, utcnow() está deprecado)
    Python < 3.12: datetime.utcnow() (ainda funciona)
    
    Returns:
        datetime: Data/hora atual em UTC
    """
    python_version = sys.version_info
    
    if python_version >= (3, 12):
        # Python 3.12+ - usa o método recomendado
        return datetime.now(timezone.utc)
    else:
        # Python < 3.12 - usa utcnow() que ainda funciona
        return datetime.utcnow()

def load_model_class(table_name: str, modules_dir: Optional[Path] = None):
    """
    Carrega dinamicamente a classe do modelo gerado.
    
    Args:
        table_name: Nome da tabela (ex: 'report_all_users')
        modules_dir: Diretório onde está o arquivo do modelo (opcional)
        
    Returns:
        Classe do modelo SQLAlchemy
    """
    if modules_dir is None:
        # Assume que está na pasta bamboohr/modules
        script_dir = Path(__file__).parent
        modules_dir = script_dir / 'modules'
    
    filename = f'{table_name}_model.py'
    module_name = f'{table_name}_model'
    filepath = modules_dir / filename
    
    if not filepath.exists():
        raise FileNotFoundError(
            f"Arquivo do modelo não encontrado: {filepath}\n"
            f"Execute primeiro o sync_report_dynamic.py para gerar o modelo."
        )
    
    # Cria spec do módulo
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível carregar o módulo: {filepath}")
    
    # Cria e executa o módulo
    module = importlib.util.module_from_spec(spec)
    
    # Define o __name__ do módulo ANTES de registrar em sys.modules
    # Isso é necessário para que o código gerado possa usar sys.modules[__name__]
    module.__name__ = module_name
    
    # Registra o módulo em sys.modules ANTES de executar
    # Isso permite que o código gerado use sys.modules[__name__] com segurança
    sys.modules[module_name] = module
    
    # Adiciona o diretório modules ao sys.path temporariamente
    modules_parent = str(modules_dir.parent)
    modules_dir_str = str(modules_dir)
    path_added_parent = False
    path_added_modules = False
    
    if modules_parent not in sys.path:
        sys.path.insert(0, modules_parent)
        path_added_parent = True
    
    if modules_dir_str not in sys.path:
        sys.path.insert(0, modules_dir_str)
        path_added_modules = True
    
    try:
        # Injeta o db no módulo ANTES de executar para evitar problemas de importação
        # Isso permite que o módulo gerado use o db mesmo se não conseguir importar flask_models
        module.db = db
        
        # Também injeta no namespace do módulo para que possa ser acessado durante execução
        import types
        if not hasattr(module, '__dict__'):
            module.__dict__ = {}
        module.__dict__['db'] = db
        
        # Tenta executar o módulo
        try:
            spec.loader.exec_module(module)
        except (ImportError, ModuleNotFoundError) as e:
            # Se falhar o import, não é problema porque já injetamos o db
            logger.debug(f"Import falhou no módulo gerado (esperado): {e}")
            logger.debug("Usando db injetado diretamente...")
        except (NameError, KeyError) as e:
            # Se db não estiver definido ou __name__ não estiver em sys.modules, injeta novamente
            if 'db' in str(e) or '__name__' in str(e) or 'report_all_users_model' in str(e):
                logger.debug(f"Erro durante execução do módulo (esperado): {e}")
                logger.debug("Garantindo que db está disponível...")
                module.db = db
                module.__dict__['db'] = db
                # Garante que o módulo está em sys.modules
                if module_name not in sys.modules:
                    sys.modules[module_name] = module
            else:
                raise
        
        # Garante que o db está disponível no módulo após execução
        if not hasattr(module, 'db') or module.db is None:
            module.db = db
            module.__dict__['db'] = db
            logger.debug("db injetado no módulo após execução")
        
        # Verifica se as classes do modelo podem acessar db
        # Se não, tenta corrigir
        for attr_name in dir(module):
            if not attr_name.startswith('_'):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and hasattr(attr, '__bases__'):
                    # Verifica se a classe herda de db.Model mas db não está disponível
                    for base in attr.__bases__:
                        if hasattr(base, '__module__') and 'sqlalchemy' in str(base.__module__):
                            # Classe SQLAlchemy encontrada, garante que db está disponível
                            if not hasattr(module, 'db'):
                                module.db = db
                                module.__dict__['db'] = db
                            break
        
    finally:
        # Remove do sys.path se foi adicionado
        if path_added_modules and modules_dir_str in sys.path:
            sys.path.remove(modules_dir_str)
        if path_added_parent and modules_parent in sys.path:
            sys.path.remove(modules_parent)
    
    # Encontra a classe do modelo (primeira classe que herda de db.Model)
    # Tenta múltiplas formas de verificação para garantir compatibilidade
    for attr_name in dir(module):
        if attr_name.startswith('_') or attr_name in ('Serializer', 'datetime', 'sys', 'inspect', 'db', 'get_utcnow'):
            continue
        
        attr = getattr(module, attr_name)
        
        if not isinstance(attr, type):
            continue
        
        # Verifica se é a classe Serializer (pular)
        if attr_name == 'Serializer':
            continue
        
        # Verifica se tem __tablename__ (característica de modelo SQLAlchemy)
        if hasattr(attr, '__tablename__'):
            logger.info(f"Modelo carregado: {attr_name} (detectado por __tablename__)")
            return attr
        
        # Verifica se herda de db.Model usando o db do módulo
        try:
            module_db = getattr(module, 'db', None)
            if module_db and hasattr(module_db, 'Model'):
                if issubclass(attr, module_db.Model) and attr != module_db.Model:
                    logger.info(f"Modelo carregado: {attr_name} (detectado por herança de db.Model)")
                    return attr
        except (TypeError, AttributeError):
            pass
        
        # Verifica se herda de db.Model usando o db global
        try:
            if issubclass(attr, db.Model) and attr != db.Model:
                logger.info(f"Modelo carregado: {attr_name} (detectado por herança de db.Model global)")
                return attr
        except (TypeError, AttributeError):
            pass
        
        # Verifica pelas bases da classe
        if hasattr(attr, '__bases__'):
            for base in attr.__bases__:
                if hasattr(base, '__name__') and base.__name__ == 'Model':
                    # Pode ser um modelo SQLAlchemy
                    if hasattr(attr, '__table__') or hasattr(attr, '__tablename__'):
                        logger.info(f"Modelo carregado: {attr_name} (detectado por bases e __table__)")
                        return attr
    
    # Se não encontrou, lista as classes disponíveis para debug
    available_classes = [x for x in dir(module) if not x.startswith('_') and isinstance(getattr(module, x), type)]
    raise ValueError(
        f"Classe do modelo não encontrada em {filepath}. "
        f"Classes disponíveis: {available_classes}. "
        f"Verifique se o modelo foi gerado corretamente executando sync_report_dynamic.py"
    )


def normalize_column_name(column_name: str) -> str:
    """
    Normaliza o nome da coluna para corresponder ao nome usado no modelo.
    
    Args:
        column_name: Nome original da coluna
        
    Returns:
        Nome normalizado (lowercase, sem caracteres especiais)
    """
    import re
    # Remove caracteres especiais e espaços
    normalized = re.sub(r'[^a-zA-Z0-9_]', '_', column_name)
    # Remove underscores múltiplos
    normalized = re.sub(r'_+', '_', normalized)
    # Remove underscore no início/fim
    normalized = normalized.strip('_')
    return normalized.lower()


def get_column_max_length(ModelClass, column_name: str) -> Optional[int]:
    """
    Obtém o tamanho máximo de uma coluna String do modelo.
    
    Args:
        ModelClass: Classe do modelo SQLAlchemy
        column_name: Nome da coluna
        
    Returns:
        Tamanho máximo da coluna ou None se não for String ou não tiver limite
    """
    try:
        column = ModelClass.__table__.columns.get(column_name)
        if column and hasattr(column.type, 'length'):
            return column.type.length
    except:
        pass
    return None


def map_data_to_model(record: Dict[str, Any], ModelClass) -> Dict[str, Any]:
    """
    Mapeia dados do JSON para o formato do modelo SQLAlchemy.
    
    Valida e trunca strings que excedem o tamanho máximo das colunas.
    
    Args:
        record: Dicionário com dados do registro
        ModelClass: Classe do modelo SQLAlchemy
        
    Returns:
        Dicionário com dados mapeados para o modelo
    """
    mapped_data = {}
    
    # Obtém todas as colunas do modelo com seus tipos
    model_columns_info = {}
    for col in ModelClass.__table__.columns:
        max_length = None
        if hasattr(col.type, 'length'):
            max_length = col.type.length
        model_columns_info[col.name] = {
            'max_length': max_length,
            'type': type(col.type).__name__,
            'nullable': col.nullable
        }
    
    model_columns = set(model_columns_info.keys())
    
    # Mapeia cada campo do registro
    for original_key, value in record.items():
        normalized_key = normalize_column_name(original_key)
        
        # Se a coluna original se chama "ID", mapeia para "column_id"
        if original_key.upper() == 'ID':
            normalized_key = 'column_id'
        
        # Verifica se a coluna existe no modelo
        if normalized_key in model_columns:
            col_info = model_columns_info[normalized_key]
            is_nullable = col_info.get('nullable', True)
            
            # Se valor é None e coluna não aceita NULL, usa valor padrão
            # NOTA: Todas as colunas de texto são nullable=True por padrão,
            # então não precisamos converter None para string vazia em colunas de texto
            if value is None and not is_nullable:
                col_type = col_info.get('type', '')
                # Colunas de texto não devem chegar aqui pois são sempre nullable=True
                # Mas mantemos a lógica para outros tipos
                if 'String' in col_type or 'Text' in col_type:
                    # Se chegou aqui, a coluna não foi alterada ainda, usa string vazia temporariamente
                    value = ''  # String vazia para colunas NOT NULL (deve ser alterada para NULL)
                elif 'Integer' in col_type or 'BigInteger' in col_type:
                    value = 0  # Zero para números NOT NULL
                elif 'Float' in col_type:
                    value = 0.0  # Zero para floats NOT NULL
                elif 'Boolean' in col_type:
                    value = False  # False para booleanos NOT NULL
                elif 'DateTime' in col_type:
                    # Para DateTime NOT NULL sem valor, pode causar erro
                    # Mas vamos tentar usar um valor padrão ou deixar None e deixar o erro aparecer
                    value = None  # Deixa None e deixa o banco reclamar se necessário
                else:
                    value = ''  # Default para outros tipos
            
            # Valida e trunca strings se necessário
            if isinstance(value, str) and value:
                max_length = col_info.get('max_length')
                
                if max_length and len(value) > max_length:
                    # Trunca a string e adiciona aviso no log
                    original_value = value
                    value = value[:max_length]
                    logger.warning(
                        f"String truncada para coluna '{normalized_key}': "
                        f"{len(original_value)} -> {len(value)} caracteres "
                        f"(valor original: {original_value[:100]}...)"
                    )
            
            # Só inclui no mapeamento se não for None ou se a coluna aceita NULL
            if value is not None or is_nullable:
                mapped_data[normalized_key] = value
        else:
            # Coluna não existe no modelo, será armazenada apenas no JSON
            logger.debug(f"Coluna '{original_key}' não encontrada no modelo, será armazenada apenas no JSON")
    
    # Adiciona JSON completo em raw_data se a coluna existir
    if 'raw_data' in model_columns:
        mapped_data['raw_data'] = record
    
    return mapped_data


def parse_date(value: Any) -> Optional[datetime]:
    """
    Tenta converter um valor para datetime.
    
    Args:
        value: Valor a ser convertido
        
    Returns:
        Objeto datetime ou None
    """
    if value is None:
        return None
    
    if isinstance(value, datetime):
        return value
    
    if isinstance(value, str):
        # Tenta vários formatos de data
        date_formats = [
            '%Y-%m-%d',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%d/%m/%Y',
            '%d-%m-%Y',
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(value.strip(), fmt)
            except ValueError:
                continue
        
        # Tenta ISO format
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except:
            pass
    
    return None


# ============================================================================
# FUNÇÕES PRINCIPAIS
# ============================================================================

def registro_db(msg: str, app_name: str = 'bamboohr', 
                name: Optional[str] = None, email: Optional[str] = None) -> None:
    """
    Registra uma mensagem no banco de dados usando o modelo InsertLog.
    
    Se a tabela não existir ou houver erro, apenas registra no log sem falhar.
    
    Args:
        msg: Mensagem a ser registrada
        app_name: Nome da aplicação (padrão: 'bamboohr')
        name: Nome do usuário (opcional)
        email: Email do usuário (opcional)
    """
    try:
        # Verifica se a tabela existe antes de tentar inserir
        from sqlalchemy import inspect as sql_inspect
        inspector = sql_inspect(db.engine)
        
        if 'log' not in inspector.get_table_names():
            logger.debug(f"Tabela 'log' não existe, pulando registro no banco")
            logger.info(f"[LOG] {msg}")
            return
        
        log_entry = InsertLog(
            name=name,
            email=email,
            msg=msg,
            app=app_name,
            date=get_utcnow()
        )
        db.session.add(log_entry)
        db.session.commit()
        logger.debug(f"Log registrado no banco: {msg[:50]}...")
    except Exception as e:
        # Não falha se não conseguir registrar no banco, apenas loga
        logger.debug(f"Erro ao registrar log no banco (continuando): {e}")
        logger.info(f"[LOG] {msg}")
        try:
            db.session.rollback()
        except:
            pass


def gravar_relatorio(
    report_id: str,
    table_name: str,
    mode: str = 'replace',
    data_key: str = 'employees'
) -> Dict[str, int]:
    """
    Grava relatório do BambooHR no banco de dados usando modelo SQLAlchemy gerado.
    
    Args:
        report_id: ID do relatório no BambooHR
        table_name: Nome da tabela no banco de dados
        mode: Modo de operação ('append' ou 'replace')
        data_key: Chave no JSON que contém os dados (padrão: 'employees')
        
    Returns:
        Dicionário com estatísticas da gravação
    """
    stats = {
        'total': 0,
        'inserted': 0,
        'updated': 0,
        'errors': 0
    }
    
    try:
        logger.info(f"Buscando relatório {report_id} do BambooHR...")
        
        # Busca dados do relatório
        report_data = bamboohr_get_report(report_id=report_id)
        
        if not report_data:
            logger.error("Resposta inválida da API do BambooHR")
            return stats
        
        # Extrai dados (pode estar em 'employees' ou diretamente no root)
        if data_key in report_data:
            data = report_data[data_key]
        elif isinstance(report_data, list):
            data = report_data
        else:
            # Tenta encontrar a primeira lista no JSON
            for key, value in report_data.items():
                if isinstance(value, list) and len(value) > 0:
                    data = value
                    data_key = key
                    break
            else:
                logger.error("Não foi possível encontrar dados no formato esperado")
                return stats
        
        if not data or not isinstance(data, list):
            logger.error("Dados não estão no formato de lista")
            return stats
        
        stats['total'] = len(data)
        logger.info(f"Encontrados {stats['total']} registros")
        
        # Carrega modelo gerado dinamicamente
        logger.info(f"Carregando modelo para tabela '{table_name}'...")
        ModelClass = load_model_class(table_name)
        
        # Garante que a classe usa o mesmo db do contexto atual
        # Isso é importante porque o modelo pode ter sido criado com um db diferente
        if hasattr(ModelClass, '__bases__'):
            # Verifica se precisa atualizar a base da classe
            for base in ModelClass.__bases__:
                if hasattr(base, '__name__') and base.__name__ == 'Model':
                    # A classe já herda de algum Model, mas precisa garantir que é do db correto
                    # Na verdade, não podemos mudar as bases de uma classe já criada
                    # Então vamos usar db.session diretamente ao invés de ModelClass.query
                    pass
        
        # Cria tabela se não existir
        logger.info("Criando/verificando tabela no banco de dados...")
        ModelClass.__table__.create(db.engine, checkfirst=True)
        
        # Verifica e adiciona colunas faltantes (como raw_data e created_at)
        logger.info("Verificando colunas faltantes...")
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        
        if table_name in inspector.get_table_names():
            existing_columns_info = {col['name']: col for col in inspector.get_columns(table_name)}
            existing_columns = list(existing_columns_info.keys())
            model_columns = [col.name for col in ModelClass.__table__.columns]
            
            missing_columns = [col for col in model_columns if col not in existing_columns]
            
            # Verifica colunas que existem mas precisam ser alteradas para nullable
            # TODAS as colunas de texto devem ser nullable=True por padrão
            columns_to_update_nullable = []
            for col_name in model_columns:
                if col_name in existing_columns:
                    model_col = ModelClass.__table__.columns[col_name]
                    existing_col = existing_columns_info[col_name]
                    
                    # Verifica se é coluna de texto pelo tipo do modelo
                    col_type_str = str(model_col.type)
                    is_text_column = 'String' in col_type_str or 'Text' in col_type_str
                    
                    # Se for coluna de texto E a coluna existente é NOT NULL, precisa alterar
                    # OU se o modelo diz nullable=True mas a coluna existente é NOT NULL
                    if (is_text_column and not existing_col.get('nullable', True)) or \
                       (model_col.nullable and not existing_col.get('nullable', True)):
                        columns_to_update_nullable.append(col_name)
            
            if missing_columns:
                logger.info(f"Encontradas {len(missing_columns)} colunas faltantes: {', '.join(missing_columns)}")
                for col_name in missing_columns:
                    col = ModelClass.__table__.columns[col_name]
                    col_type = col.type
                    
                    # Detecta tipo do banco de dados
                    db_url = str(db.engine.url)
                    is_mysql = 'mysql' in db_url.lower() or 'mariadb' in db_url.lower()
                    
                    # Converte tipo SQLAlchemy para SQL
                    type_str = str(col_type)
                    if 'JSON' in type_str or (hasattr(col_type, 'python_type') and col_type.python_type == dict):
                        if is_mysql:
                            sql_type = 'JSON'
                        else:
                            sql_type = 'TEXT'  # Fallback para outros bancos
                    elif 'DateTime' in type_str or (hasattr(col_type, 'python_type') and col_type.python_type == datetime):
                        sql_type = 'DATETIME'
                    elif 'String' in type_str:
                        # Extrai tamanho se houver (ex: String(200))
                        import re
                        match = re.search(r'String\((\d+)\)', type_str)
                        if match:
                            size = match.group(1)
                            sql_type = f'VARCHAR({size})'
                        else:
                            sql_type = 'VARCHAR(255)'
                    elif 'Text' in type_str:
                        sql_type = 'TEXT'
                    elif 'Integer' in type_str:
                        sql_type = 'INTEGER'
                    else:
                        # Usa o tipo como está, mas remove prefixos do SQLAlchemy
                        sql_type = type_str.split('.')[-1] if '.' in type_str else type_str
                    
                    # Determina nullable
                    nullable_str = 'NULL' if col.nullable else 'NOT NULL'
                    
                    # Determina default se houver
                    default_str = ''
                    if col.default is not None:
                        if hasattr(col.default, 'arg'):
                            if callable(col.default.arg):
                                # É uma função como get_utcnow
                                if 'utcnow' in str(col.default.arg) or 'datetime' in str(col.default.arg):
                                    if is_mysql:
                                        default_str = 'DEFAULT CURRENT_TIMESTAMP'
                                    else:
                                        default_str = "DEFAULT (datetime('now'))"
                                else:
                                    default_str = ''
                            else:
                                default_str = f"DEFAULT {col.default.arg}"
                    
                    try:
                        # Monta SQL ALTER TABLE
                        alter_parts = [f"ALTER TABLE `{table_name}` ADD COLUMN `{col_name}` {sql_type}"]
                        if nullable_str:
                            alter_parts.append(nullable_str)
                        if default_str:
                            alter_parts.append(default_str)
                        
                        alter_sql = text(' '.join(alter_parts))
                        db.session.execute(alter_sql)
                        db.session.commit()
                        logger.info(f"  ✓ Coluna '{col_name}' adicionada com sucesso")
                    except Exception as e:
                        db.session.rollback()
                        error_msg = str(e)
                        # Se a coluna já existe, não é um erro crítico
                        if 'Duplicate column' in error_msg or 'already exists' in error_msg.lower():
                            logger.debug(f"  Coluna '{col_name}' já existe, ignorando")
                        else:
                            logger.warning(f"  ⚠ Não foi possível adicionar coluna '{col_name}': {error_msg}")
                        # Continua mesmo se não conseguir adicionar
            else:
                logger.debug("Todas as colunas já existem na tabela")
            
            # Atualiza colunas que precisam ser alteradas para nullable
            if columns_to_update_nullable:
                logger.info(f"Alterando {len(columns_to_update_nullable)} colunas para aceitar NULL: {', '.join(columns_to_update_nullable)}")
                db_url = str(db.engine.url)
                is_mysql = 'mysql' in db_url.lower() or 'mariadb' in db_url.lower()
                
                for col_name in columns_to_update_nullable:
                    try:
                        # MySQL/MariaDB: ALTER TABLE ... MODIFY COLUMN ... NULL
                        if is_mysql:
                            model_col = ModelClass.__table__.columns[col_name]
                            col_type = model_col.type
                            type_str = str(col_type)
                            
                            # Converte tipo SQLAlchemy para SQL
                            if 'String' in type_str:
                                import re
                                match = re.search(r'String\((\d+)\)', type_str)
                                if match:
                                    size = match.group(1)
                                    sql_type = f'VARCHAR({size})'
                                else:
                                    sql_type = 'VARCHAR(255)'
                            elif 'Text' in type_str:
                                sql_type = 'TEXT'
                            elif 'DateTime' in type_str:
                                sql_type = 'DATETIME'
                            elif 'Integer' in type_str:
                                sql_type = 'INTEGER'
                            else:
                                sql_type = type_str.split('.')[-1] if '.' in type_str else type_str
                            
                            alter_sql = text(f"ALTER TABLE `{table_name}` MODIFY COLUMN `{col_name}` {sql_type} NULL")
                            db.session.execute(alter_sql)
                            db.session.commit()
                            logger.info(f"  ✓ Coluna '{col_name}' alterada para aceitar NULL")
                        else:
                            # Outros bancos podem ter sintaxe diferente
                            logger.warning(f"  ⚠ Alteração de nullable não suportada para este tipo de banco")
                    except Exception as e:
                        db.session.rollback()
                        error_msg = str(e)
                        if 'Duplicate column' in error_msg or 'already exists' in error_msg.lower():
                            logger.debug(f"  Coluna '{col_name}' já está correta, ignorando")
                        else:
                            logger.warning(f"  ⚠ Não foi possível alterar coluna '{col_name}' para NULL: {error_msg}")
        
        # Se modo é 'replace', limpa a tabela usando db.session diretamente
        if mode == 'replace':
            logger.info("Limpando tabela existente...")
            # Usa db.session.query ao invés de ModelClass.query para evitar problemas de contexto
            from sqlalchemy import delete
            db.session.execute(delete(ModelClass))
            db.session.commit()
        
        # Processa e insere dados incrementalmente
        logger.info("Processando e inserindo dados em lotes de 100 registros...")
        
        for idx, record in enumerate(data, 1):
            try:
                # Mapeia dados para o formato do modelo
                mapped_data = map_data_to_model(record, ModelClass)
                
                # Converte datas se necessário
                for key, value in mapped_data.items():
                    if isinstance(value, str) and ('date' in key.lower() or 'time' in key.lower()):
                        parsed_date = parse_date(value)
                        if parsed_date:
                            mapped_data[key] = parsed_date
                
                # Verifica se registro já existe (modo append)
                existing = None
                if mode == 'append':
                    # Tenta encontrar por column_id se existir
                    # Usa db.session.query ao invés de ModelClass.query para garantir contexto correto
                    if 'column_id' in mapped_data and mapped_data['column_id']:
                        existing = db.session.query(ModelClass).filter_by(
                            column_id=str(mapped_data['column_id'])
                        ).first()
                
                if existing:
                    # Atualiza registro existente
                    for key, value in mapped_data.items():
                        if key != 'id':  # Não atualiza ID automático
                            setattr(existing, key, value)
                    existing.created_at = get_utcnow()
                    stats['updated'] += 1
                    logger.debug(f"Atualizado registro {idx}/{stats['total']}")
                else:
                    # Insere novo registro
                    new_record = ModelClass(**mapped_data)
                    db.session.add(new_record)
                    stats['inserted'] += 1
                    logger.debug(f"Inserido registro {idx}/{stats['total']}")
                
                # Commit em lotes de 100 registros para melhor performance
                if idx % 100 == 0:
                    try:
                        # Verifica se há mudanças pendentes antes de fazer commit
                        if db.session.dirty or db.session.new or db.session.deleted:
                            db.session.commit()
                            logger.info(f"Progresso: {idx}/{stats['total']} registros processados...")
                    except Exception as commit_error:
                        error_msg = str(commit_error)
                        logger.error(f"Erro ao fazer commit em lote: {error_msg}")
                        
                        # Faz rollback imediatamente para limpar a sessão
                        try:
                            db.session.rollback()
                        except Exception as rollback_err:
                            logger.debug(f"Erro ao fazer rollback: {rollback_err}")
                            # Tenta limpar objetos manualmente
                            try:
                                if db.session.new:
                                    for obj in list(db.session.new):
                                        try:
                                            db.session.expunge(obj)
                                        except:
                                            pass
                            except:
                                pass
                        
                        # Se o erro foi devido a dados muito longos, tenta identificar e corrigir
                        if 'Data too long for column' in error_msg or '1406' in error_msg:
                            logger.warning("Erro de dados muito longos detectado. Os próximos registros serão validados e truncados automaticamente.")
                        else:
                            logger.info("Continuando processamento após erro em lote...")
                
            except Exception as e:
                stats['errors'] += 1
                error_msg = str(e)
                logger.error(f"Erro ao processar registro {idx}: {error_msg}")
                
                # Verifica se é erro de dados muito longos
                if 'Data too long for column' in error_msg or '1406' in error_msg:
                    # Extrai o nome da coluna do erro
                    import re
                    match = re.search(r"column '(\w+)'", error_msg)
                    if match:
                        col_name = match.group(1)
                        logger.warning(f"Dados muito longos para coluna '{col_name}' no registro {idx}")
                        # Tenta truncar e reprocessar
                        try:
                            col_info = ModelClass.__table__.columns.get(col_name)
                            if col_info and hasattr(col_info.type, 'length'):
                                max_len = col_info.type.length
                                if col_name in mapped_data and isinstance(mapped_data[col_name], str):
                                    original = mapped_data[col_name]
                                    mapped_data[col_name] = original[:max_len] if max_len else original
                                    logger.info(f"Valor truncado para {max_len} caracteres, tentando novamente...")
                                    # Tenta inserir novamente com valor truncado
                                    try:
                                        new_record = ModelClass(**mapped_data)
                                        db.session.add(new_record)
                                        stats['inserted'] += 1
                                        stats['errors'] -= 1  # Remove do contador de erros
                                        logger.debug(f"Registro {idx} inserido após truncamento")
                                        continue
                                    except Exception as retry_error:
                                        logger.error(f"Erro ao tentar novamente após truncamento: {retry_error}")
                        except:
                            pass
                
                logger.debug(f"Dados do registro: {json.dumps(record, indent=2, default=str)}")
                
                # Faz rollback imediatamente para limpar a sessão após erro
                try:
                    db.session.rollback()
                except Exception as rollback_error:
                    logger.debug(f"Erro ao fazer rollback: {rollback_error}")
                    # Tenta limpar objetos problemáticos manualmente
                    try:
                        if db.session.new:
                            for obj in list(db.session.new):
                                try:
                                    db.session.expunge(obj)
                                except:
                                    pass
                    except:
                        pass
                continue
        
        # Commit final - apenas se houver mudanças pendentes
        try:
            if db.session.dirty or db.session.new or db.session.deleted:
                db.session.commit()
                logger.info("Gravação concluída com sucesso!")
            else:
                logger.info("Nenhuma mudança pendente para commit")
        except Exception as commit_error:
            logger.error(f"Erro ao fazer commit final: {commit_error}")
            try:
                if db.session.is_active:
                    db.session.rollback()
            except Exception as rollback_error:
                logger.debug(f"Erro ao fazer rollback final: {rollback_error}")
            stats['errors'] += 1
        
    except Exception as e:
        logger.error(f"Erro durante gravação: {e}")
        import traceback
        logger.error(traceback.format_exc())
        # Verifica se a sessão está ativa antes de fazer rollback
        try:
            if db.session.is_active:
                db.session.rollback()
        except Exception as rollback_error:
            logger.debug(f"Erro ao fazer rollback: {rollback_error}")
        stats['errors'] += 1
    
    return stats


def gravar_todos_usuarios(mode: str = 'replace'):
    """
    Grava o relatório de todos os usuários no banco de dados.
    
    Esta função é equivalente à função original, mas usa modelos SQLAlchemy
    gerados dinamicamente ao invés de pandas.
    
    Args:
        mode: Modo de operação ('append' ou 'replace')
    """
    return gravar_relatorio(
        report_id='184',
        table_name='report_all_users',
        mode=mode,
        data_key='employees'
    )


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """
    Função principal do script.
    
    Executa a gravação do relatório de todos os usuários do BambooHR
    usando o modelo SQLAlchemy gerado dinamicamente.
    """
    start_time = datetime.now()
    
    logger.info("=" * 70)
    logger.info("BAMBOOHR - Gravação de Relatórios (Versão 2)")
    logger.info("=" * 70)
    logger.info(f"Iniciado em: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    try:
        # Configura locale para português brasileiro
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
            logger.debug("Locale configurado para Português do Brasil")
        except locale.Error:
            try:
                locale.setlocale(locale.LC_ALL, 'pt_BR')
            except locale.Error as e:
                logger.warning(f"Não foi possível configurar locale: {e}")
        
        # Executa dentro do contexto da aplicação Flask
        with app.app_context():
            # Registra início no banco de dados
            registro_db(
                msg="Iniciando gravação do relatório de todos os usuários",
                app_name='bamboohr'
            )
            
            # Grava relatório de todos os usuários
            stats = gravar_todos_usuarios(mode='replace')
            
            # Exibe estatísticas
            logger.info("")
            logger.info("=" * 70)
            logger.info("ESTATÍSTICAS DA GRAVAÇÃO")
            logger.info("=" * 70)
            logger.info(f"Total de registros processados: {stats['total']}")
            logger.info(f"Novos registros inseridos: {stats['inserted']}")
            logger.info(f"Registros atualizados: {stats['updated']}")
            logger.info(f"Erros encontrados: {stats['errors']}")
            logger.info("=" * 70)
            
            # Registra conclusão no banco de dados
            registro_db(
                msg=f"Gravação concluída: {stats['inserted']} inseridos, {stats['updated']} atualizados, {stats['errors']} erros",
                app_name='bamboohr'
            )
            
    except Exception as e:
        logger.error(f"Erro fatal no script: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Registra erro no banco de dados
        try:
            with app.app_context():
                registro_db(
                    msg=f"Erro fatal: {str(e)}",
                    app_name='bamboohr'
                )
        except:
            pass
        
        raise
    
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

