# Script Melhorado de Sincronização BambooHR

## Visão Geral

O script `get_reports_improved.py` é uma versão melhorada do script original `get_reports.py`, utilizando Flask SQLAlchemy ORM para operações no banco de dados ao invés de pandas.

## Principais Melhorias

### ✅ Uso de SQLAlchemy ORM
- Elimina dependência do pandas para gravação no banco
- Operações tipadas e seguras
- Suporte a transações do banco de dados
- Validação automática de dados

### ✅ Modelo de Dados Bem Definido
- Classe `BambooHRReportAllUsers` com todos os campos tipados
- Documentação completa de cada campo
- Métodos auxiliares (`to_dict()`, `__repr__()`)

### ✅ Funções Auxiliares
- `normalize_string()`: Normaliza e valida strings
- `parse_date()`: Converte strings de data para datetime
- `map_employee_data()`: Mapeia dados da API para o modelo
- Funções de busca: `get_all_users_from_db()`, `get_user_by_email()`, etc.

### ✅ Tratamento de Erros Robusto
- Try/except em operações críticas
- Rollback automático em caso de erro
- Logging detalhado de erros

### ✅ Performance Otimizada
- Commits em lotes (a cada 50 registros)
- Índices no banco de dados para campos importantes
- Queries otimizadas

### ✅ Documentação Completa
- Docstrings em todas as funções
- Comentários explicativos no código
- Type hints para melhor IDE support

## Estrutura do Modelo

### Tabela: `report_all_users`

```python
class BambooHRReportAllUsers(db.Model):
    # Chave primária
    id = db.Column(db.Integer, primary_key=True)
    
    # Informações básicas
    employee_id = db.Column(db.String(50), unique=True, index=True)
    employee_number = db.Column(db.String(50))
    status = db.Column(db.String(50))
    employment_status = db.Column(db.String(50))
    
    # Informações pessoais
    display_name = db.Column(db.String(200))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    # ... e mais campos
```

## Como Usar

### 1. Criar a Tabela no Banco de Dados

Primeiro, você precisa criar a tabela no banco de dados. Execute no contexto do Flask:

```python
from bamboohr.get_reports_improved import app, db, BambooHRReportAllUsers

with app.app_context():
    db.create_all()
```

Ou use Flask-Migrate:

```bash
flask db migrate -m "Create report_all_users table"
flask db upgrade
```

### 2. Executar o Script

```bash
cd bamboohr
python3 get_reports_improved.py
```

### 3. Usar as Funções Programaticamente

```python
from bamboohr.get_reports_improved import (
    sync_all_users_report,
    get_all_users_from_db,
    get_user_by_email,
    get_user_by_employee_id
)

# Sincronizar relatório
stats = sync_all_users_report(report_id='184', update_existing=True)
print(f"Inseridos: {stats['inserted']}, Atualizados: {stats['updated']}")

# Buscar usuários
users = get_all_users_from_db(active_only=True)
for user in users:
    print(f"{user.display_name} - {user.work_email}")

# Buscar usuário específico
user = get_user_by_email('usuario@exemplo.com')
if user:
    print(f"Encontrado: {user.display_name}")
```

## Comparação com o Script Original

| Característica | Script Original | Script Melhorado |
|---------------|----------------|------------------|
| Gravação no BD | Pandas `to_sql()` | SQLAlchemy ORM |
| Validação | Mínima | Completa |
| Tratamento de Erros | Básico | Robusto |
| Transações | Não | Sim |
| Documentação | Limitada | Completa |
| Type Hints | Não | Sim |
| Performance | Boa | Otimizada |
| Manutenibilidade | Média | Alta |

## Configuração Necessária

### Variáveis de Ambiente

O script utiliza as mesmas variáveis de ambiente do script original:

- `BAMBOOHR_KEY`: Chave da API do BambooHR
- `db_username`: Usuário do banco de dados
- `db_password`: Senha do banco de dados
- `db_host`: Host do banco de dados

### Dependências

```python
flask
flask-sqlalchemy
flask-migrate  # Opcional, mas recomendado
python-dotenv
requests
```

## Logs e Monitoramento

O script registra logs em:
1. **Arquivo de log**: `/tmp/infosec_bamboorh.log` (configurado em `logger_config.py`)
2. **Banco de dados**: Tabela `log` através da função `log_to_database()`

## Exemplo de Saída

```
======================================================================
BAMBOOHR - Script de Sincronização de Relatórios
======================================================================
Iniciado em: 2024-01-15 10:30:00

Iniciando sincronização do relatório 184...
Buscando dados do BambooHR...
Processando 150 funcionários...
Progresso: 50/150 funcionários processados...
Progresso: 100/150 funcionários processados...
Progresso: 150/150 funcionários processados...
Sincronização concluída com sucesso!

======================================================================
ESTATÍSTICAS DA SINCRONIZAÇÃO
======================================================================
Total de funcionários processados: 150
Novos registros inseridos: 5
Registros atualizados: 145
Erros encontrados: 0
======================================================================

Finalizado em: 2024-01-15 10:32:15
Duração total: 0:02:15
======================================================================
```

## Próximos Passos

1. Adicionar testes unitários
2. Implementar cache para reduzir chamadas à API
3. Adicionar suporte a outros tipos de relatórios
4. Implementar sincronização incremental (apenas mudanças)
5. Adicionar webhook para sincronização automática

## Suporte

Para dúvidas ou problemas, consulte:
- Logs em `/tmp/infosec_bamboorh.log`
- Tabela `log` no banco de dados
- Documentação do código (docstrings)

