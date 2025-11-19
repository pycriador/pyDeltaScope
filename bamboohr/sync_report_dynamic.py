#!/usr/bin/env python3
"""
Script dinâmico para gerar modelos SQLAlchemy a partir de relatórios do BambooHR.

Este script:
1. Busca dados do relatório BambooHR via API
2. Analisa a estrutura dos dados JSON (usando apenas uma amostragem)
3. Infere tipos de dados automaticamente
4. Gera dinamicamente um modelo SQLAlchemy
5. Salva o modelo na pasta modules/

IMPORTANTE: Este script apenas gera o modelo, não grava dados no banco.
Para gravar dados no banco, use o script get_reports_v2.py.

Características:
- Geração automática de modelos baseada nos dados
- Análise apenas de amostragem para melhor performance
- Detecção automática de tipos de dados
- Renomeia coluna "ID" para "column_id" e cria ID automático
- Adiciona coluna created_at automaticamente
- Todas as colunas de texto são nullable=True por padrão
- Mínimo de 255 caracteres para colunas de texto
- Não utiliza pandas

Autor: DeltaScope Team
Data: 2025
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Set
import json
import os
import re
import sys
from pathlib import Path

# Importar módulo de log personalizado
from modules.logger_config import logger

# Importar módulo do app Flask e configurações do DB
from modules.flask_models import app, db

# Importar módulo BambooHR para buscar dados
from modules.bamboohr import bamboohr_get_report


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def get_utcnow_code() -> str:
    """
    Retorna código Python compatível para obter datetime UTC atual.
    
    Gera código que funciona em diferentes versões do Python:
    - Python 3.12+: datetime.now(timezone.utc) (recomendado)
    - Python < 3.12: datetime.utcnow() (ainda funciona)
    
    Returns:
        String com código Python compatível
    """
    python_version = sys.version_info
    
    if python_version >= (3, 12):
        # Python 3.12+ - usa o método recomendado
        return "datetime.now(timezone.utc)"
    else:
        # Python < 3.12 - usa utcnow() que ainda funciona
        return "datetime.utcnow()"


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


# ============================================================================
# FUNÇÕES DE ANÁLISE E INFERÊNCIA DE TIPOS
# ============================================================================

def infer_sqlalchemy_type(value: Any, column_name: str = None) -> str:
    """
    Infere o tipo SQLAlchemy apropriado baseado no valor Python.
    
    Args:
        value: Valor a ser analisado
        column_name: Nome da coluna (para casos especiais)
        
    Returns:
        String com o tipo SQLAlchemy (ex: 'db.String(200)', 'db.Integer', etc.)
    """
    if value is None:
        # Se for None, assume String como padrão (será nullable)
        return 'db.String(500)'
    
    # Tipo Python do valor
    value_type = type(value)
    
    # Boolean
    if value_type == bool:
        return 'db.Boolean'
    
    # Integer
    if value_type == int:
        # Verifica se é um ID ou número grande
        if column_name and 'id' in column_name.lower():
            return 'db.Integer'
        if abs(value) > 2147483647:  # Maior que INT32
            return 'db.BigInteger'
        return 'db.Integer'
    
    # Float/Double
    if value_type == float:
        return 'db.Float'
    
    # String
    if value_type == str:
        # Verifica se é uma data
        if is_date_string(value):
            return 'db.DateTime'
        
        # Verifica tamanho da string (garante mínimo de 255 caracteres)
        length = max(len(value), 255)
        
        # Verifica se é um email
        if '@' in value and '.' in value:
            if length <= 500:
                return 'db.String(500)'
            else:
                return 'db.Text'
        
        # Outras strings - mínimo de 255 caracteres
        if length <= 500:
            return 'db.String(500)'
        else:
            return 'db.Text'
    
    # List ou Dict (JSON)
    if value_type in (list, dict):
        return 'db.JSON'
    
    # Default: String
    return 'db.String(500)'


def is_date_string(value: str) -> bool:
    """
    Verifica se uma string parece ser uma data.
    
    Args:
        value: String a ser verificada
        
    Returns:
        True se parecer ser uma data, False caso contrário
    """
    if not isinstance(value, str):
        return False
    
    # Padrões comuns de data
    date_patterns = [
        r'^\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        r'^\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY
        r'^\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
    ]
    
    for pattern in date_patterns:
        if re.match(pattern, value.strip()):
            return True
    
    return False


def infer_string_type_from_length(length: int, column_name: str = None) -> str:
    """
    Infere o tipo String apropriado baseado no tamanho máximo encontrado.
    
    Garante que todas as colunas de texto tenham pelo menos 255 caracteres
    para evitar erros de "Data too long for column".
    
    Args:
        length: Tamanho máximo da string encontrado nos dados
        column_name: Nome da coluna (para casos especiais como 'address')
        
    Returns:
        String com o tipo SQLAlchemy apropriado
    """
    # Garante mínimo de 255 caracteres para todas as colunas de texto
    min_length = max(length, 255)
    
    # Colunas de endereço geralmente precisam de mais espaço
    if column_name and 'address' in column_name.lower():
        if min_length <= 500:
            return 'db.String(500)'
        else:
            return 'db.Text'
    
    # Outras colunas - mínimo de 255 caracteres
    if min_length <= 500:
        return 'db.String(500)'
    else:
        return 'db.Text'


def analyze_data_structure(data: List[Dict[str, Any]], sample_size: int = 100) -> Dict[str, Dict[str, Any]]:
    """
    Analisa a estrutura dos dados para inferir tipos e características das colunas.
    
    Usa apenas uma amostragem dos dados para otimizar performance.
    
    Args:
        data: Lista de dicionários com os dados
        sample_size: Tamanho da amostragem a ser analisada (padrão: 100 registros)
        
    Returns:
        Dicionário com informações sobre cada coluna:
        {
            'column_name': {
                'type': 'db.String(200)',
                'nullable': True,
                'max_length': 200,
                'has_id_in_name': False
            }
        }
    """
    if not data:
        return {}
    
    # Pega apenas uma amostragem dos dados para análise
    total_records = len(data)
    sample = data[:sample_size] if total_records > sample_size else data
    sample_count = len(sample)
    
    # Log informativo sobre a amostragem
    if total_records > sample_size:
        print(f"Analisando amostragem de {sample_count} registros (de {total_records} totais) para inferir tipos...")
    else:
        print(f"Analisando todos os {sample_count} registros para inferir tipos...")
    
    column_info = {}
    
    # Analisa apenas a amostragem para determinar tipos e tamanhos
    # Executa apenas um loop sobre a amostragem
    for record in sample:
        for column_name, value in record.items():
            if column_name not in column_info:
                column_info[column_name] = {
                    'values': [],
                    'types': set(),
                    'max_length': 0,
                    'has_id_in_name': 'id' in column_name.lower() and column_name.lower() != 'id'
                }
            
            column_info[column_name]['values'].append(value)
            column_info[column_name]['types'].add(type(value))
            
            if isinstance(value, str):
                column_info[column_name]['max_length'] = max(
                    column_info[column_name]['max_length'],
                    len(value)
                )
    
    # Processa informações e infere tipos finais
    result = {}
    for column_name, info in column_info.items():
        # Encontra o tipo mais comum (não-None)
        non_none_values = [v for v in info['values'] if v is not None]
        
        if non_none_values:
            # Usa o primeiro valor não-None para inferir tipo base
            sample_value = non_none_values[0]
            
            # Se for string, usa o tamanho máximo encontrado para inferir o tipo
            if isinstance(sample_value, str):
                # Verifica se é uma data
                if is_date_string(sample_value):
                    inferred_type = 'db.DateTime'
                    # DateTime pode ser nullable se houver valores None
                    is_text_column = False
                # Verifica se é um email
                elif '@' in sample_value and '.' in sample_value:
                    # Emails também devem ter pelo menos 255 caracteres
                    email_length = max(info['max_length'], 255)
                    if email_length <= 500:
                        inferred_type = 'db.String(500)'
                    else:
                        inferred_type = 'db.Text'
                    is_text_column = True
                else:
                    # Usa o tamanho máximo encontrado para inferir o tipo String
                    # A função já garante mínimo de 255 caracteres
                    inferred_type = infer_string_type_from_length(info['max_length'], column_name)
                    is_text_column = True
            else:
                # Para outros tipos, usa a inferência padrão
                inferred_type = infer_sqlalchemy_type(sample_value, column_name)
                # Verifica se é coluna de texto
                is_text_column = 'String' in inferred_type or 'Text' in inferred_type
        else:
            # Se todos são None, assume String com tamanho razoável
            inferred_type = 'db.String(500)'
            is_text_column = True
        
        # Todas as colunas de texto são nullable=True por padrão
        # Outras colunas são nullable apenas se houver valores None na amostragem
        if is_text_column:
            nullable = True
        else:
            nullable = None in info['values']
        
        result[column_name] = {
            'type': inferred_type,
            'nullable': nullable,
            'max_length': info['max_length'],
            'has_id_in_name': info['has_id_in_name']
        }
    
    return result


def normalize_column_name(column_name: str) -> str:
    """
    Normaliza o nome da coluna para ser válido em Python e SQL.
    
    Args:
        column_name: Nome original da coluna
        
    Returns:
        Nome normalizado
    """
    # Remove caracteres especiais e espaços
    normalized = re.sub(r'[^a-zA-Z0-9_]', '_', column_name)
    
    # Remove underscores múltiplos
    normalized = re.sub(r'_+', '_', normalized)
    
    # Remove underscore no início/fim
    normalized = normalized.strip('_')
    
    # Se começar com número, adiciona prefixo
    if normalized and normalized[0].isdigit():
        normalized = 'col_' + normalized
    
    # Se estiver vazio, usa nome padrão
    if not normalized:
        normalized = 'column'
    
    return normalized.lower()


# ============================================================================
# GERAÇÃO DE MODELO SQLALCHEMY
# ============================================================================

def generate_model_code(table_name: str, column_info: Dict[str, Dict[str, Any]]) -> str:
    """
    Gera o código Python do modelo SQLAlchemy baseado nas informações das colunas.
    
    Args:
        table_name: Nome da tabela
        column_info: Informações sobre as colunas
        
    Returns:
        String com o código Python do modelo
    """
    # Nome da classe (PascalCase)
    class_name = ''.join(word.capitalize() for word in table_name.split('_'))
    
    # Código do modelo
    code_lines = [
        '"""',
        f'Modelo SQLAlchemy gerado automaticamente para a tabela {table_name}.',
        '',
        f'Gerado em: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        'Este arquivo é gerado automaticamente e pode ser sobrescrito.',
        '"""',
        '',
        'from datetime import datetime, timezone',
        'import sys',
        'from sqlalchemy.inspection import inspect',
        '',
        '# Importar do Flask app o db',
        '# Tenta importar de diferentes formas para compatibilidade',
        '# Se todos os imports falharem, usa o db injetado externamente',
        'try:',
        '    # Tenta import relativo primeiro',
        '    from .flask_models import db',
        'except ImportError:',
        '    try:',
        '        # Tenta import absoluto',
        '        from flask_models import db',
        '    except ImportError:',
        '        try:',
        '            # Tenta import do módulo modules',
        '            from modules.flask_models import db',
        '        except ImportError:',
        '            # Se tudo falhar, usa o db injetado externamente',
        '            # Isso acontece quando o modelo é carregado dinamicamente',
        '            # O db será injetado antes da execução do módulo',
        '            try:',
        '                # Tenta pegar do módulo atual usando __name__',
        '                import sys',
        '                if __name__ in sys.modules:',
        '                    _current_module = sys.modules[__name__]',
        '                    if hasattr(_current_module, \'db\'):',
        '                        db = _current_module.db',
        '                    else:',
        '                        db = globals().get(\'db\')',
        '                else:',
        '                    db = globals().get(\'db\')',
        '            except (KeyError, NameError):',
        '                # Se __name__ não estiver disponível, usa globals',
        '                db = globals().get(\'db\')',
        '',
        '',
        'def get_utcnow():',
        '    """Retorna datetime UTC atual de forma compatível com diferentes versões do Python"""',
        '    python_version = sys.version_info',
        '    if python_version >= (3, 12):',
        '        return datetime.now(timezone.utc)',
        '    else:',
        '        return datetime.utcnow()',
        '',
        '',
        'class Serializer(object):',
        '    """Classe auxiliar para serialização de objetos"""',
        '    def serialize(self):',
        '        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}',
        '',
        '    @staticmethod',
        '    def serialize_list(list):',
        '        return [info.serialize() for info in list]',
        '',
        '',
        f'class {class_name}(db.Model, Serializer):',
        f'    """Modelo SQLAlchemy para a tabela {table_name}"""',
        f'    __tablename__ = \'{table_name}\'',
        '',
        '    # Chave primária automática',
        '    id = db.Column(db.Integer, primary_key=True, autoincrement=True)',
        '',
    ]
    
    # Processa cada coluna
    for original_name, info in column_info.items():
        normalized_name = normalize_column_name(original_name)
        
        # Se a coluna original se chama "ID", renomeia para "column_id"
        if original_name.upper() == 'ID':
            normalized_name = 'column_id'
        
        # Tipo da coluna
        column_type = info['type']
        nullable = info['nullable']
        
        # Comentário com nome original
        if normalized_name != original_name.lower():
            code_lines.append(f'    # Coluna original: {original_name}')
        
        # Define nullable
        nullable_str = 'nullable=True' if nullable else 'nullable=False'
        
        # Adiciona índice se for ID ou email
        index_str = ''
        if 'id' in normalized_name or 'email' in normalized_name:
            index_str = ', index=True'
        
        # Linha da coluna
        code_lines.append(
            f'    {normalized_name} = db.Column({column_type}, {nullable_str}{index_str})'
        )
        code_lines.append('')
    
    # Adiciona coluna raw_data para armazenar JSON completo
    utcnow_code = get_utcnow_code()
    code_lines.extend([
        '    # Coluna para armazenar JSON completo dos dados (backup/auditoria)',
        '    raw_data = db.Column(db.JSON, nullable=True)',
        '',
        '    # Coluna de auditoria - data/hora da gravação',
        f'    created_at = db.Column(db.DateTime, default=get_utcnow, nullable=False)',
        '',
        '    def __repr__(self):',
        f'        """Representação string do objeto"""',
        f'        return f\'<{class_name} {{self.id}}>\'',
        '',
        '    def serialize(self):',
        '        """Converte o objeto para dicionário"""',
        '        data = Serializer.serialize(self)',
        '        return data',
        '',
    ])
    
    return '\n'.join(code_lines)


def save_model_to_file(table_name: str, model_code: str, modules_dir: Path) -> Path:
    """
    Salva o código do modelo em um arquivo Python na pasta modules.
    
    Args:
        table_name: Nome da tabela (usado como nome do arquivo)
        model_code: Código Python do modelo
        modules_dir: Diretório onde salvar o arquivo
        
    Returns:
        Path do arquivo criado
    """
    # Nome do arquivo: nome_da_tabela_model.py
    filename = f'{table_name}_model.py'
    filepath = modules_dir / filename
    
    # Salva o arquivo
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(model_code)
    
    logger.info(f"Modelo salvo em: {filepath}")
    return filepath


def load_model_class(table_name: str, modules_dir: Path):
    """
    Carrega dinamicamente a classe do modelo gerado.
    
    Args:
        table_name: Nome da tabela
        modules_dir: Diretório onde está o arquivo do modelo
        
    Returns:
        Classe do modelo SQLAlchemy
    """
    filename = f'{table_name}_model.py'
    module_name = f'{table_name}_model'
    
    # Importa o módulo dinamicamente
    import importlib.util
    import sys
    
    filepath = modules_dir / filename
    
    if not filepath.exists():
        raise FileNotFoundError(f"Arquivo do modelo não encontrado: {filepath}")
    
    # Cria spec do módulo
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível carregar o módulo: {filepath}")
    
    # Cria e executa o módulo
    module = importlib.util.module_from_spec(spec)
    
    # Adiciona o diretório modules ao sys.path temporariamente se necessário
    modules_parent = str(modules_dir.parent)
    if modules_parent not in sys.path:
        sys.path.insert(0, modules_parent)
    
    try:
        spec.loader.exec_module(module)
    finally:
        # Remove do sys.path se foi adicionado
        if modules_parent in sys.path:
            sys.path.remove(modules_parent)
    
    # Encontra a classe do modelo (primeira classe que herda de db.Model)
    for attr_name in dir(module):
        if attr_name.startswith('_'):
            continue
        attr = getattr(module, attr_name)
        if (isinstance(attr, type) and 
            issubclass(attr, db.Model) and 
            attr != db.Model and
            attr_name != 'Serializer'):
            logger.info(f"Classe do modelo encontrada: {attr_name}")
            return attr
    
    raise ValueError(f"Classe do modelo não encontrada em {filepath}. Classes encontradas: {[x for x in dir(module) if not x.startswith('_')]}")


# ============================================================================
# FUNÇÕES DE SINCRONIZAÇÃO
# ============================================================================

def sync_report_dynamic(
    report_id: str,
    table_name: str,
    data_key: str = 'employees'
) -> Dict[str, Any]:
    """
    Gera dinamicamente o modelo SQLAlchemy para um relatório do BambooHR.
    
    Este script apenas cria o modelo, não grava dados no banco.
    Para gravar dados, use o script get_reports_v2.py.
    
    Args:
        report_id: ID do relatório no BambooHR
        table_name: Nome da tabela no banco de dados
        data_key: Chave no JSON que contém os dados (padrão: 'employees')
        
    Returns:
        Dicionário com informações sobre o modelo gerado
    """
    stats = {
        'total': 0,
        'table_name': table_name,
        'model_file': None,
        'columns_count': 0
    }
    
    try:
        logger.info(f"Gerando modelo dinâmico para o relatório {report_id}...")
        logger.info(f"Tabela: {table_name}")
        
        # 1. Busca dados do relatório
        logger.info("Buscando dados do BambooHR...")
        report_data = bamboohr_get_report(report_id=report_id)
        
        if not report_data:
            logger.error("Resposta inválida da API do BambooHR")
            return stats
        
        # 2. Extrai dados (pode estar em 'employees' ou diretamente no root)
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
        
        # 3. Analisa estrutura dos dados
        logger.info("Analisando estrutura dos dados...")
        column_info = analyze_data_structure(data)
        logger.info(f"Encontradas {len(column_info)} colunas")
        
        # 4. Gera modelo SQLAlchemy
        logger.info("Gerando modelo SQLAlchemy...")
        model_code = generate_model_code(table_name, column_info)
        
        # 5. Salva modelo na pasta modules
        script_dir = Path(__file__).parent
        modules_dir = script_dir / 'modules'
        modules_dir.mkdir(exist_ok=True)
        
        model_file = save_model_to_file(table_name, model_code, modules_dir)
        stats['model_file'] = str(model_file)
        stats['columns_count'] = len(column_info)
        
        logger.info("=" * 70)
        logger.info("Modelo gerado com sucesso!")
        logger.info(f"Arquivo: {model_file}")
        logger.info(f"Tabela: {table_name}")
        logger.info(f"Colunas: {len(column_info)}")
        logger.info(f"Registros analisados: {stats['total']}")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"Erro durante geração do modelo: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    return stats


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """
    Função principal do script.
    
    Gera apenas o modelo SQLAlchemy, não grava dados no banco.
    Para gravar dados, use o script get_reports_v2.py.
    
    Permite configurar:
    - report_id: ID do relatório no BambooHR
    - table_name: Nome da tabela no banco de dados
    - data_key: Chave no JSON que contém os dados (opcional)
    """
    import sys
    
    # Configurações padrão
    report_id = '184'
    table_name = 'report_all_users'
    data_key = 'employees'  # Chave no JSON que contém os dados
    
    # Permite sobrescrever via argumentos da linha de comando
    if len(sys.argv) > 1:
        report_id = sys.argv[1]
    if len(sys.argv) > 2:
        table_name = sys.argv[2]
    if len(sys.argv) > 3:
        data_key = sys.argv[3]
    
    start_time = datetime.now()
    
    logger.info("=" * 70)
    logger.info("BAMBOOHR - Geração Dinâmica de Modelos SQLAlchemy")
    logger.info("=" * 70)
    logger.info(f"Iniciado em: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Relatório ID: {report_id}")
    logger.info(f"Tabela: {table_name}")
    logger.info("")
    
    try:
        # Executa geração do modelo
        with app.app_context():
            stats = sync_report_dynamic(
                report_id=report_id,
                table_name=table_name,
                data_key=data_key
            )
        
        # Exibe estatísticas
        logger.info("")
        logger.info("=" * 70)
        logger.info("ESTATÍSTICAS DA GERAÇÃO DO MODELO")
        logger.info("=" * 70)
        logger.info(f"Tabela: {stats['table_name']}")
        logger.info(f"Total de registros analisados: {stats['total']}")
        logger.info(f"Colunas identificadas: {stats['columns_count']}")
        if stats['model_file']:
            logger.info(f"Arquivo do modelo: {stats['model_file']}")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"Erro fatal no script: {e}")
        import traceback
        logger.error(traceback.format_exc())
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

