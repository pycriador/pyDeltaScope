# Script de Sincronização Dinâmica de Relatórios BambooHR

## Visão Geral

O script `sync_report_dynamic.py` é uma solução avançada que **gera automaticamente modelos SQLAlchemy** baseados na estrutura dos dados retornados pela API do BambooHR. Ele elimina a necessidade de criar manualmente modelos para cada tipo de relatório.

## Características Principais

### ✅ Geração Automática de Modelos
- Analisa automaticamente a estrutura dos dados JSON
- Infere tipos de dados (String, Integer, DateTime, Boolean, JSON, etc.)
- Gera código Python do modelo SQLAlchemy
- Salva o modelo na pasta `modules/` com nome `{table_name}_model.py`

### ✅ Tratamento Inteligente de Colunas
- **Coluna "ID"**: Automaticamente renomeada para `column_id`
- **ID Automático**: Cria sempre uma coluna `id` como chave primária auto-incremental
- **Coluna `created_at`**: Adicionada automaticamente com data/hora da gravação

### ✅ Modos de Operação
- **`replace`**: Limpa a tabela e insere todos os dados (padrão)
- **`append`**: Adiciona novos registros ou atualiza existentes (baseado em `column_id`)

### ✅ Sem Dependência de Pandas
- Usa apenas SQLAlchemy ORM para operações no banco
- Mais eficiente e tipado

### ✅ Detecção Automática de Estrutura
- Detecta automaticamente a chave no JSON que contém os dados
- Suporta diferentes formatos de resposta da API

## Como Usar

### Uso Básico

```bash
cd bamboohr
python3 sync_report_dynamic.py
```

Isso usa as configurações padrão:
- Relatório ID: `184`
- Tabela: `report_all_users`
- Modo: `replace`

### Uso com Parâmetros

```bash
python3 sync_report_dynamic.py <report_id> <table_name> <mode> [data_key]
```

**Parâmetros:**
1. `report_id`: ID do relatório no BambooHR (obrigatório)
2. `table_name`: Nome da tabela no banco de dados (obrigatório)
3. `mode`: Modo de operação - `append` ou `replace` (opcional, padrão: `replace`)
4. `data_key`: Chave no JSON que contém os dados (opcional, padrão: `employees`)

### Exemplos

```bash
# Sincronizar relatório 184 na tabela report_all_users (modo replace)
python3 sync_report_dynamic.py 184 report_all_users replace

# Sincronizar relatório 200 na tabela report_custom (modo append)
python3 sync_report_dynamic.py 200 report_custom append

# Sincronizar relatório 150 na tabela report_employees (modo replace, chave customizada)
python3 sync_report_dynamic.py 150 report_employees replace users
```

## Fluxo de Execução

1. **Busca Dados**: Chama `bamboohr_get_report()` para obter dados do relatório
2. **Análise**: Analisa a estrutura dos dados JSON para inferir tipos
3. **Geração**: Gera código Python do modelo SQLAlchemy
4. **Salvamento**: Salva modelo em `modules/{table_name}_model.py`
5. **Carregamento**: Carrega dinamicamente o modelo gerado
6. **Criação**: Cria/atualiza tabela no banco de dados
7. **Processamento**: Processa e insere dados conforme modo escolhido

## Estrutura do Modelo Gerado

O modelo gerado terá sempre:

```python
class ReportTableName(db.Model, Serializer):
    __tablename__ = 'report_table_name'
    
    # ID automático (sempre presente)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Colunas baseadas nos dados (com tipos inferidos)
    column_id = db.Column(...)  # Se havia coluna "ID" original
    field1 = db.Column(...)
    field2 = db.Column(...)
    # ...
    
    # Coluna created_at (sempre presente)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
```

## Inferência de Tipos

O script infere tipos automaticamente:

| Tipo Python | Tipo SQLAlchemy Inferido |
|------------|-------------------------|
| `bool` | `db.Boolean` |
| `int` | `db.Integer` ou `db.BigInteger` |
| `float` | `db.Float` |
| `str` (curta) | `db.String(50)` ou `db.String(100)` |
| `str` (longa) | `db.String(200)`, `db.String(500)` ou `db.Text` |
| `str` (data) | `db.DateTime` |
| `str` (email) | `db.String(200)` |
| `list` / `dict` | `db.JSON` |
| `None` | `db.String(500)` (nullable) |

## Tratamento de Coluna "ID"

Se os dados contiverem uma coluna chamada **"ID"**:

1. ✅ A coluna original é renomeada para **`column_id`**
2. ✅ Uma nova coluna **`id`** é criada como chave primária auto-incremental
3. ✅ O valor original da coluna "ID" é preservado em `column_id`

**Exemplo:**
```python
# Dados originais
{"ID": "123", "name": "John"}

# No modelo gerado
id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Novo
column_id = db.Column(db.String(50), nullable=True)  # Original renomeado
name = db.Column(db.String(100), nullable=True)
```

## Modos de Operação

### Modo `replace` (Padrão)
- **Limpa** toda a tabela antes de inserir
- **Insere** todos os registros do relatório
- Útil para sincronização completa

### Modo `append`
- **Mantém** registros existentes
- **Insere** novos registros
- **Atualiza** registros existentes (baseado em `column_id`)
- Útil para atualizações incrementais

## Arquivos Gerados

### Modelo SQLAlchemy
**Localização**: `bamboohr/modules/{table_name}_model.py`

**Características:**
- Código Python completo e funcional
- Documentado com docstrings
- Inclui classe `Serializer` para serialização
- Sobrescrito a cada execução (mantém apenas versão mais recente)

### Exemplo de Arquivo Gerado

```python
"""
Modelo SQLAlchemy gerado automaticamente para a tabela report_all_users.

Gerado em: 2025-01-15 10:30:00
Este arquivo é gerado automaticamente e pode ser sobrescrito.
"""

from datetime import datetime
from sqlalchemy.inspection import inspect

from .flask_models import db

class Serializer(object):
    """Classe auxiliar para serialização de objetos"""
    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(list):
        return [info.serialize() for info in list]

class ReportAllUsers(db.Model, Serializer):
    """Modelo SQLAlchemy para a tabela report_all_users"""
    __tablename__ = 'report_all_users'

    # Chave primária automática
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Colunas baseadas nos dados
    employee_id = db.Column(db.String(50), nullable=True)
    display_name = db.Column(db.String(200), nullable=True)
    # ...

    # Coluna de auditoria
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<ReportAllUsers {self.id}>'

    def serialize(self):
        data = Serializer.serialize(self)
        return data
```

## Logs e Monitoramento

O script registra logs detalhados em:
- **Arquivo**: `/tmp/infosec_bamboorh.log` (configurado em `logger_config.py`)

**Informações registradas:**
- Progresso da sincronização
- Estatísticas (inseridos, atualizados, erros)
- Localização do arquivo do modelo gerado
- Erros e warnings

## Exemplo de Saída

```
======================================================================
BAMBOOHR - Sincronização Dinâmica de Relatórios
======================================================================
Iniciado em: 2025-01-15 10:30:00
Relatório ID: 184
Tabela: report_all_users
Modo: replace

Iniciando sincronização dinâmica do relatório 184...
Buscando dados do BambooHR...
Encontrados 150 registros
Analisando estrutura dos dados...
Encontradas 25 colunas
Gerando modelo SQLAlchemy...
Modelo salvo em: /path/to/bamboohr/modules/report_all_users_model.py
Carregando modelo gerado...
Criando/atualizando tabela no banco de dados...
Limpando tabela existente...
Processando e inserindo dados...
Progresso: 50/150 registros processados...
Progresso: 100/150 registros processados...
Progresso: 150/150 registros processados...
Sincronização concluída com sucesso!

======================================================================
ESTATÍSTICAS DA SINCRONIZAÇÃO
======================================================================
Tabela: report_all_users
Total de registros processados: 150
Novos registros inseridos: 150
Registros atualizados: 0
Erros encontrados: 0
Arquivo do modelo: /path/to/bamboohr/modules/report_all_users_model.py
======================================================================

Finalizado em: 2025-01-15 10:32:15
Duração total: 0:02:15
======================================================================
```

## Uso Programático

Você também pode usar o script programaticamente:

```python
from sync_report_dynamic import sync_report_dynamic
from modules.flask_models import app

with app.app_context():
    stats = sync_report_dynamic(
        report_id='184',
        table_name='report_all_users',
        mode='replace',
        data_key='employees'
    )
    
    print(f"Inseridos: {stats['inserted']}")
    print(f"Atualizados: {stats['updated']}")
    print(f"Erros: {stats['errors']}")
```

## Requisitos

- Python 3.7+
- Flask
- Flask-SQLAlchemy
- requests
- python-dotenv

## Vantagens sobre o Script Original

| Característica | Script Original | Script Dinâmico |
|---------------|----------------|-----------------|
| Criação de Modelo | Manual | Automática |
| Tipos de Dados | Fixos | Inferidos automaticamente |
| Coluna ID | Manual | Tratamento automático |
| Coluna created_at | Manual | Adicionada automaticamente |
| Reutilização | Baixa | Alta (gera modelo para qualquer relatório) |
| Manutenção | Alta | Baixa (modelo gerado automaticamente) |

## Troubleshooting

### Erro: "Arquivo do modelo não encontrado"
- Verifique se o modelo foi gerado em `modules/{table_name}_model.py`
- Execute o script novamente para regenerar o modelo

### Erro: "Classe do modelo não encontrada"
- Verifique se o arquivo do modelo foi gerado corretamente
- Verifique se a classe herda de `db.Model`

### Erro: "Não foi possível encontrar dados"
- Verifique se o `report_id` está correto
- Verifique se a `data_key` está correta (padrão: `employees`)
- Verifique a resposta da API do BambooHR

## Próximos Passos

1. Adicionar suporte a relacionamentos entre tabelas
2. Implementar cache de modelos gerados
3. Adicionar validação de dados antes da inserção
4. Implementar sincronização incremental mais inteligente
5. Adicionar suporte a múltiplos relatórios em uma execução

