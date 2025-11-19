# DeltaScope - Sistema de Comparação de Tabelas

Sistema completo para comparação de tabelas entre bancos de dados, com geração automática de modelos SQLAlchemy, dashboards dinâmicos, gerenciamento de usuários e permissões, e interface moderna com suporte a temas claro/escuro.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Inicialização](#inicialização)
- [Scripts Disponíveis](#scripts-disponíveis)
- [Estrutura do Banco de Dados](#estrutura-do-banco-de-dados)
- [Páginas e Rotas](#páginas-e-rotas)
- [API Endpoints](#api-endpoints)
- [Webhooks e Cliente HTTP](#webhooks-e-cliente-http)
- [Filtros por URL](#filtros-por-url)
- [Gerenciamento de Usuários](#gerenciamento-de-usuários)
- [Gerenciamento de Grupos](#gerenciamento-de-grupos)
- [Edição de Tabelas](#edição-de-tabelas)
- [Dashboard e Gráficos](#dashboard-e-gráficos)
- [Exemplos de Código](#exemplos-de-código)
- [Troubleshooting](#troubleshooting)

## 🎯 Sobre o Projeto

O **DeltaScope** é uma aplicação web desenvolvida em Flask que permite comparar tabelas entre diferentes bancos de dados, identificar diferenças, gerar modelos SQLAlchemy automaticamente e visualizar mudanças através de dashboards interativos.

### Principais Características

- 🔐 **Autenticação Segura**: Sistema de login com sessões Flask e tokens
- 👥 **Gerenciamento de Usuários**: Criação, edição, ativação/desativação e exclusão de usuários
- 🔑 **Sistema de Permissões**: Grupos com permissões granulares por funcionalidade
- 🗄️ **Múltiplos Bancos**: Suporte para SQLite, MariaDB e MySQL
- 🔒 **Criptografia**: Senhas de banco de dados criptografadas com Fernet
- 📊 **Dashboards Interativos**: Gráficos dinâmicos com Plotly.js
- 🎨 **Interface Moderna**: Design responsivo com suporte a tema claro/escuro
- 📝 **Geração Automática**: Modelos SQLAlchemy gerados automaticamente
- 🔄 **Comparação Inteligente**: Identificação de diferenças entre tabelas origem e destino
- 📈 **Relatórios**: Exportação de resultados em CSV, JSON e Excel

## ✨ Funcionalidades

### Autenticação e Usuários
- ✅ Login e logout com sessões Flask
- ✅ Cadastro de novos usuários (página pública `/create_user`)
- ✅ Criação de usuários por administradores (página `/usuarios/novo`)
- ✅ Ativação/desativação de usuários
- ✅ Alteração de senhas
- ✅ Exclusão de usuários (remove automaticamente de todos os grupos)
- ✅ Proteção contra auto-exclusão e auto-desativação de admins

### Grupos e Permissões
- ✅ Criação e gerenciamento de grupos
- ✅ **Sistema de Permissões Granulares (Criar/Executar)**:
  - Cada funcionalidade possui duas permissões distintas:
    - **Criar**: Permite criar novos recursos (conexões, projetos, etc.)
    - **Executar**: Permite visualizar e usar recursos criados por outros usuários
  - Funcionalidades com permissões granulares:
    - Conexões (`can_create_connections`, `can_execute_connections`)
    - Projetos (`can_create_projects`, `can_execute_projects`)
    - Tabelas (`can_create_tables`, `can_execute_tables`)
    - Usuários (`can_create_users`, `can_execute_users`)
    - Grupos (`can_create_groups`, `can_execute_groups`)
    - Relatórios de Comparação (`can_create_comparison_reports`, `can_execute_comparison_reports`)
    - Relatórios de Consistência (`can_create_consistency_reports`, `can_execute_consistency_reports`)
    - Dashboard (`can_create_dashboard`, `can_execute_dashboard`)
    - Comparação (`can_create_comparison`, `can_execute_comparison`)
    - Agendamentos (`can_create_scheduled_tasks`, `can_execute_scheduled_tasks`)
    - Webhooks (`can_create_webhooks`, `can_execute_webhooks`)
    - Consistência de Dados (`can_create_data_consistency`, `can_execute_data_consistency`)
- ✅ **Compartilhamento Inteligente**: Projetos, conexões e outros recursos criados por usuários com permissão de criar são automaticamente visíveis para todos os usuários com permissão de executar
- ✅ Associação de usuários a grupos
- ✅ Usuários admin têm todas as permissões automaticamente e podem ver todos os recursos

### Conexões de Banco de Dados
- ✅ CRUD completo de conexões
- ✅ Suporte para SQLite, MariaDB e MySQL
- ✅ Teste de conexão antes de salvar
- ✅ Criptografia de senhas com Fernet
- ✅ Visualização de tabelas disponíveis

### Projetos
- ✅ CRUD completo de projetos
- ✅ Seleção visual de tabelas antes de criar projeto
- ✅ Mapeamento de tabelas origem e destino
- ✅ Geração automática de modelos SQLAlchemy

### Comparações
- ✅ Execução de comparações entre tabelas
- ✅ Seleção de chaves primárias para comparação
- ✅ Mapeamento de colunas com nomes diferentes
- ✅ Identificação de registros adicionados, modificados e deletados
- ✅ Visualização de resultados detalhados
- ✅ Exportação de resultados (CSV, JSON, Excel/TXT)
- ✅ Execução via URL com parâmetros de chaves primárias

### Agendamento de Tarefas (CRON)
- ✅ Criação de tarefas agendadas para comparações automáticas
- ✅ Tipos de agendamento:
  - Preset: 15min, 1h, 6h, 12h, diário
  - Intervalo: minutos personalizados
  - CRON: expressões CRON customizadas
- ✅ Seleção visual de colunas origem e destino
- ✅ Mapeamento automático de chaves primárias
- ✅ Execução manual de tarefas agendadas
- ✅ Histórico de execuções (sucesso/falha)
- ✅ Ativação/desativação de tarefas
- ✅ Execução automática em background
- ✅ Proteção contra execuções duplicadas simultâneas

### Tabelas
- ✅ Visualização de tabelas por conexão
- ✅ Informações detalhadas de colunas
- ✅ Edição de tipos de colunas
- ✅ Modificação de propriedades (nullable, primary key)
- ✅ Atualização automática no banco de dados
- ✅ Geração/atualização de modelos SQLAlchemy locais

### Dashboard
- ✅ Estatísticas do projeto
- ✅ Gráficos interativos:
  - Mudanças ao longo do tempo (linha)
  - Mudanças por campo (barras)
  - Campos modificados no período (pizza)
  - Mudanças por tipo (pizza)
  - Comparações por status (barras)
  - Tendência de mudanças (área)
- ✅ Filtros por data (início e fim)
- ✅ Filtros por URL (compartilhamento de links)

### Relatórios
- ✅ Visualização de comparações executadas
- ✅ Detalhes de resultados por comparação
- ✅ Exportação de dados (CSV, JSON, TXT)
- ✅ Filtro por projeto via URL
- ✅ Identificação de execução manual vs agendada
- ✅ Deleção de relatórios individuais
- ✅ Deleção em massa por projeto

### Interface
- ✅ Design moderno e responsivo
- ✅ Tema claro/escuro com toggle
- ✅ Navegação por URLs significativas
- ✅ Páginas HTML renderizadas no servidor
- ✅ Modais Bootstrap para notificações
- ✅ Loading states e feedback visual

## 📁 Estrutura do Projeto

```
pyDeltaScope/
├── app/
│   ├── __init__.py                 # Factory da aplicação Flask
│   ├── models/                     # Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   ├── user.py                 # Modelo de usuário
│   │   ├── group.py                 # Modelo de grupos e permissões
│   │   ├── project.py               # Modelo de projeto
│   │   ├── comparison.py            # Modelo de comparação
│   │   ├── comparison_result.py     # Modelo de resultado de comparação
│   │   ├── change_log.py            # Modelo de log de mudanças
│   │   ├── database_connection.py   # Modelo de conexão de banco
│   │   ├── table_model_mapping.py   # Mapeamento tabela-modelo
│   │   └── generated/               # Modelos SQLAlchemy gerados automaticamente
│   │       └── *.py                 # Modelos gerados dinamicamente
│   ├── routes/                      # Rotas da aplicação
│   │   ├── __init__.py
│   │   ├── auth.py                  # API de autenticação
│   │   ├── auth_template.py         # Páginas de autenticação (login, registro)
│   │   ├── users.py                 # API de usuários (Admin)
│   │   ├── users_template.py         # Páginas de usuários
│   │   ├── groups.py                # API de grupos (Admin)
│   │   ├── groups_template.py       # Páginas de grupos
│   │   ├── projects.py              # API de projetos
│   │   ├── projects_template.py     # Páginas de projetos
│   │   ├── connections.py           # API de conexões
│   │   ├── connections_template.py  # Páginas de conexões
│   │   ├── comparisons.py           # API de comparações
│   │   ├── comparison_template.py  # Páginas de comparação
│   │   ├── dashboard.py             # API de dashboard
│   │   ├── dashboard_template.py    # Página de dashboard
│   │   ├── tables.py                # API de tabelas
│   │   ├── tables_template.py       # Páginas de tabelas
│   │   ├── reports_template.py      # Páginas de relatórios
│   │   ├── home_template.py         # Página inicial
│   │   ├── api_docs.py              # Página de documentação da API
│   │   └── setup.py                 # API de setup inicial
│   ├── services/                    # Serviços de negócio
│   │   ├── __init__.py
│   │   ├── database.py              # Serviço de conexão com bancos
│   │   ├── table_mapper.py          # Mapeamento de tabelas para modelos
│   │   └── comparison_service.py    # Serviço de comparação
│   ├── utils/                       # Utilitários
│   │   ├── __init__.py
│   │   ├── security.py              # Geração e verificação de tokens
│   │   ├── encryption.py            # Criptografia de senhas (Fernet)
│   │   ├── permissions.py           # Verificação de permissões
│   │   └── db_check.py              # Verificação de tabelas do banco
│   └── static/                      # Arquivos estáticos
│       ├── css/
│       │   └── style.css            # Estilos customizados
│       └── js/
│           └── app.js               # JavaScript da aplicação
├── templates/                       # Templates HTML
│   ├── base.html                    # Template base
│   ├── login.html                   # Página de login
│   ├── create_user_auth.html        # Página pública de cadastro
│   ├── create_user.html             # Página admin de criação de usuário
│   ├── home.html                    # Página inicial (bem-vindo)
│   ├── users.html                   # Página de gerenciamento de usuários
│   ├── groups.html                  # Página de gerenciamento de grupos
│   ├── connections.html             # Página de conexões
│   ├── projects.html                # Página de projetos
│   ├── comparison.html              # Página de seleção de projeto
│   ├── comparison_execution.html    # Página de execução de comparação
│   ├── comparison_results.html      # Página de resultados
│   ├── dashboard.html               # Página de dashboard
│   ├── tables.html                  # Página de tabelas
│   ├── edit_table.html              # Página de edição de colunas
│   ├── reports.html                 # Página de relatórios
│   ├── api_docs.html                # Página de documentação da API
│   ├── change_password.html         # Página de alteração de senha
│   └── error.html                   # Página de erro
├── instance/                        # Banco de dados SQLite (dev)
│   └── deltascope.db
├── config.py                        # Configurações da aplicação
├── requirements.txt                 # Dependências Python
├── run.py                          # Script de execução principal
├── init_db.py                      # Script de inicialização do banco
├── create_admin.py                 # Script interativo para criar admin
├── change_password.py              # Script CLI para trocar senha
├── .env.example                    # Exemplo de variáveis de ambiente
├── .env                            # Variáveis de ambiente (não versionado)
├── .gitignore                      # Arquivos ignorados pelo Git
└── README.md                       # Este arquivo
```

## 🚀 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- MariaDB/MySQL (opcional, para produção)
- SQLite (incluído no Python)

### Passo a Passo

1. **Clone o repositório ou baixe o projeto**

```bash
cd pyDeltaScope
```

2. **Crie um ambiente virtual (recomendado)**

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Instale as dependências**

```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**

Copie o arquivo `.env.example` para `.env` e configure:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
# Chave secreta do Flask (gere uma nova com: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=sua_chave_secreta_aqui

# Chave de criptografia para senhas de banco (gere uma nova com: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
ENCRYPTION_KEY=sua_chave_de_criptografia_aqui

# Tipo de banco de dados (sqlite ou mariadb)
DATABASE_TYPE=sqlite

# Configurações para SQLite
SQLITE_DB_PATH=instance/deltascope.db

# Configurações para MariaDB/MySQL (se DATABASE_TYPE=mariadb)
DB_HOST=localhost
DB_PORT=3306
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_NAME=deltascope

# Endpoint da API externa (opcional)
EXTERNAL_API_ENDPOINT=https://api.exemplo.com/webhook
EXTERNAL_API_TOKEN=seu_token_aqui

# Ambiente Flask
FLASK_ENV=development
FLASK_APP=run.py
```

## ⚙️ Configuração

### Geração de Chaves

**SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**ENCRYPTION_KEY:**

Recomendado: Use o script fornecido para gerar uma chave forte e segura:
```bash
python3 generate_encryption_key.py
```

O script irá:
- Gerar uma chave de criptografia forte usando Fernet
- Exibir a chave de forma segura
- Opcionalmente salvar no arquivo `.env`

Alternativa manual:
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

⚠️ **IMPORTANTE:** Guarde essas chaves em local seguro. Se perder a `ENCRYPTION_KEY`, não será possível descriptografar senhas de banco de dados já salvas.

## 🏁 Inicialização

### 1. Inicializar o Banco de Dados

Execute o script de inicialização para criar todas as tabelas e grupos padrão:

```bash
python init_db.py
```

Este script irá:
- Criar todas as tabelas necessárias
- Criar grupos de permissões padrão com sistema granular (criar/executar):
  - **Administradores**: Todas as permissões de criar e executar
  - **Criadores de Conexões**: `can_create_connections=True`
  - **Executores de Conexões**: `can_execute_connections=True`
  - **Criadores de Projetos**: `can_create_projects=True`
  - **Executores de Projetos**: `can_execute_projects=True`
  - E assim por diante para todas as funcionalidades...

### 2. Criar o Primeiro Usuário Administrador

**Opção A: Via Interface Web (Recomendado)**

1. Inicie o servidor Flask:

**Recomendado:** Use o script `start.py` que resolve automaticamente conflitos de porta:
```bash
python3 start.py
```

Ou use o script shell:
```bash
./start.sh
```

**Alternativa:** Inicie diretamente (pode dar erro se porta 5000 estiver em uso):
```bash
python3 run.py
```

2. Acesse `http://localhost:5000` (ou a porta indicada pelo script)
3. O sistema detectará que é a primeira execução e mostrará um modal para criar o primeiro admin
4. Preencha os dados e crie o usuário

**Opção B: Via Página de Cadastro Pública**

1. Acesse `http://localhost:5000/create_user`
2. Preencha os dados do primeiro usuário
3. O primeiro usuário criado será automaticamente um administrador

**Opção C: Via Script Interativo**

```bash
python create_admin.py
```

O script irá solicitar:
- Usuário
- Email
- Senha (com confirmação)

**Opção D: Via Script CLI (Não Interativo)**

```bash
python change_password.py admin senha123 --create-admin
```

### 3. Iniciar o Servidor

**Recomendado:** Use o script `start.py` que resolve automaticamente conflitos de porta:
```bash
python3 start.py
```

Ou use o script shell:
```bash
./start.sh
```

**Alternativa:** Inicie diretamente (pode dar erro se porta 5000 estiver em uso):
```bash
python3 run.py
```

O servidor estará disponível em `http://localhost:5000` (ou na porta indicada pelo script)

## 📜 Scripts Disponíveis

### `start.py` / `start.sh`

Scripts para iniciar o servidor Flask resolvendo automaticamente conflitos de porta.

```bash
# Python (recomendado)
python3 start.py

# Shell script (alternativa)
./start.sh
```

**Características:**
- ✅ Detecta se a porta 5000 está em uso
- ✅ Identifica processos Flask/Python usando a porta
- ✅ Oferece opção de encerrar processo conflitante
- ✅ Encontra automaticamente porta alternativa se necessário
- ✅ Detecta AirPlay Receiver do macOS e oferece soluções
- ✅ Exibe informações claras sobre o processo encontrado

**Comportamento:**
- Se a porta 5000 estiver livre, inicia normalmente
- Se estiver em uso por outro Flask/Python, oferece encerrar o processo
- Se estiver em uso por outro serviço (ex: AirPlay), sugere usar outra porta
- Busca automaticamente portas livres de 5001 a 5009 se necessário

### `generate_encryption_key.py`

Script para gerar uma chave de criptografia forte e segura.

```bash
python3 generate_encryption_key.py
```

**Características:**
- ✅ Gera chave Fernet compatível com a aplicação
- ✅ Exibe a chave de forma segura
- ✅ Opcionalmente salva no arquivo `.env`
- ✅ Inclui avisos de segurança importantes

### `init_db.py`

Inicializa o banco de dados criando todas as tabelas e grupos padrão.

```bash
python init_db.py
```

**O que faz:**
- Cria todas as tabelas do sistema
- Cria grupos de permissões padrão
- Verifica se existe algum usuário admin

### `create_admin.py`

Script interativo para criar usuário administrador.

```bash
python create_admin.py
```

**Características:**
- Validação de dados em tempo real
- Verificação de duplicatas
- Confirmação antes de criar
- Teste de senha após criação

### `change_password.py`

Script CLI para trocar senha de usuário ou criar admin.

**Trocar senha de usuário existente:**
```bash
python change_password.py usuario nova_senha123
```

**Criar novo usuário admin:**
```bash
python change_password.py admin senha123 --create-admin
```

## 🗄️ Estrutura do Banco de Dados

### Tabelas Principais

#### `users`
Armazena informações dos usuários do sistema.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | Integer | Chave primária |
| username | String(80) | Nome de usuário (único) |
| email | String(120) | Email (único) |
| password_hash | String(255) | Hash da senha (Werkzeug) |
| is_active | Boolean | Status ativo/inativo |
| is_admin | Boolean | É administrador |
| created_at | DateTime | Data de criação |
| updated_at | DateTime | Data de atualização |

#### `groups`
Armazena grupos de permissões com sistema granular de criar/executar.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | Integer | Chave primária |
| name | String(100) | Nome do grupo (único) |
| description | String(500) | Descrição do grupo |
| **Conexões** | | |
| can_create_connections | Boolean | Pode criar conexões |
| can_execute_connections | Boolean | Pode visualizar/usar conexões criadas por outros |
| **Projetos** | | |
| can_create_projects | Boolean | Pode criar projetos |
| can_execute_projects | Boolean | Pode visualizar/usar projetos criados por outros |
| **Tabelas** | | |
| can_create_tables | Boolean | Pode criar tabelas |
| can_execute_tables | Boolean | Pode visualizar/editar tabelas |
| **Usuários** | | |
| can_create_users | Boolean | Pode criar usuários |
| can_execute_users | Boolean | Pode gerenciar usuários |
| **Grupos** | | |
| can_create_groups | Boolean | Pode criar grupos |
| can_execute_groups | Boolean | Pode gerenciar grupos |
| **Relatórios de Comparação** | | |
| can_create_comparison_reports | Boolean | Pode criar relatórios de comparação |
| can_execute_comparison_reports | Boolean | Pode visualizar relatórios de comparação |
| **Relatórios de Consistência** | | |
| can_create_consistency_reports | Boolean | Pode criar relatórios de consistência |
| can_execute_consistency_reports | Boolean | Pode visualizar relatórios de consistência |
| **Dashboard** | | |
| can_create_dashboard | Boolean | Pode criar dashboards |
| can_execute_dashboard | Boolean | Pode visualizar dashboards |
| **Comparação** | | |
| can_create_comparison | Boolean | Pode criar comparações |
| can_execute_comparison | Boolean | Pode executar comparações |
| **Agendamentos** | | |
| can_create_scheduled_tasks | Boolean | Pode criar tarefas agendadas |
| can_execute_scheduled_tasks | Boolean | Pode executar tarefas agendadas |
| **Webhooks** | | |
| can_create_webhooks | Boolean | Pode criar configurações de webhook |
| can_execute_webhooks | Boolean | Pode usar webhooks |
| **Consistência de Dados** | | |
| can_create_data_consistency | Boolean | Pode criar configurações de consistência |
| can_execute_data_consistency | Boolean | Pode executar verificações de consistência |
| **Permissões Legadas** (deprecated) | | |
| can_view_dashboards | Boolean | Pode ver dashboards (legado) |
| can_edit_tables | Boolean | Pode editar tabelas (legado) |
| can_view_tables | Boolean | Pode ver tabelas (legado) |
| can_view_reports | Boolean | Pode ver relatórios (legado) |
| can_download_reports | Boolean | Pode baixar relatórios (legado) |
| created_at | DateTime | Data de criação |
| updated_at | DateTime | Data de atualização |

#### `user_groups`
Tabela de associação muitos-para-muitos entre usuários e grupos.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| user_id | Integer | FK para users.id |
| group_id | Integer | FK para groups.id |
| created_at | DateTime | Data de associação |

#### `database_connections`
Armazena configurações de conexão com bancos de dados.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | Integer | Chave primária |
| name | String(200) | Nome da conexão |
| description | String(500) | Descrição |
| db_type | String(50) | Tipo (sqlite, mariadb, mysql) |
| encrypted_config | Text | Configuração criptografada |
| user_id | Integer | FK para users.id |
| is_active | Boolean | Status ativo/inativo |
| created_at | DateTime | Data de criação |
| updated_at | DateTime | Data de atualização |

#### `projects`
Armazena projetos de comparação.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | Integer | Chave primária |
| name | String(200) | Nome do projeto |
| description | String(500) | Descrição |
| source_connection_id | Integer | FK para database_connections.id |
| target_connection_id | Integer | FK para database_connections.id |
| source_table | String(200) | Nome da tabela origem |
| target_table | String(200) | Nome da tabela destino |
| model_file_path | String(500) | Caminho do arquivo do modelo |
| user_id | Integer | FK para users.id |
| is_active | Boolean | Status ativo/inativo |
| created_at | DateTime | Data de criação |
| updated_at | DateTime | Data de atualização |

#### `comparisons`
Armazena execuções de comparação.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | Integer | Chave primária |
| project_id | Integer | FK para projects.id |
| executed_at | DateTime | Data de execução |
| status | String(50) | Status (pending, running, completed, failed) |
| total_differences | Integer | Total de diferenças encontradas |
| comparison_metadata | JSON | Metadados da comparação |
| user_id | Integer | FK para users.id |

#### `comparison_results`
Armazena resultados detalhados das comparações.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | Integer | Chave primária |
| comparison_id | Integer | FK para comparisons.id |
| record_id | String(200) | ID do registro (chave primária) |
| field_name | String(200) | Nome do campo |
| source_value | Text | Valor origem |
| target_value | Text | Valor destino |
| change_type | String(50) | Tipo (added, modified, deleted) |

#### `change_logs`
Armazena logs incrementais de mudanças.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | Integer | Chave primária |
| project_id | Integer | FK para projects.id |
| comparison_id | Integer | FK para comparisons.id |
| record_id | String(200) | ID do registro |
| field_name | String(200) | Nome do campo |
| old_value | Text | Valor antigo |
| new_value | Text | Valor novo |
| change_type | String(50) | Tipo (added, modified, deleted) |
| detected_at | DateTime | Data da detecção |
| sent_to_api | Boolean | Se foi enviado para API externa |

#### `table_model_mappings`
Mapeia tabelas para seus arquivos de modelo SQLAlchemy gerados.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | Integer | Chave primária |
| connection_id | Integer | FK para database_connections.id |
| table_name | String(200) | Nome da tabela |
| model_file_path | String(500) | Caminho do arquivo do modelo |
| user_id | Integer | FK para users.id |
| created_at | DateTime | Data de criação |
| updated_at | DateTime | Data de atualização |

**Constraint único:** `(connection_id, table_name, user_id)`

## 🌐 Páginas e Rotas

### Páginas Públicas (Não Autenticadas)

- `/` - Página inicial (redireciona para login se não autenticado)
- `/login` - Página de login
- `/create_user` - Página pública de cadastro de usuário
- `/docs` - Documentação da API (pública)

### Páginas Autenticadas

- `/home` - Página inicial após login (bem-vindo)
- `/usuarios` - Gerenciamento de usuários (Admin)
- `/usuarios/novo` - Criar novo usuário (Admin)
- `/usuarios/<id>/senha` - Alterar senha de usuário (Admin)
- `/grupos` - Gerenciamento de grupos (Admin)
- `/conexoes` - Gerenciamento de conexões de banco
- `/conexoes/novo` - Criar nova conexão
- `/conexoes/<id>/editar` - Editar conexão
- `/projetos` - Gerenciamento de projetos
- `/projetos/novo` - Criar novo projeto
- `/projetos/<id>/editar` - Editar projeto
- `/comparacao` - Seleção de projeto para comparação
- `/comparacao/<id>/execution` - Execução de comparação (suporta parâmetros de URL)
- `/relatorios` - Visualização de relatórios (suporta filtro por `project_id`)
- `/relatorios/<id>/resultados` - Resultados detalhados de comparação
- `/dashboard` - Dashboard com gráficos e estatísticas (suporta filtros por URL)
- `/tabelas` - Visualização de tabelas (suporta filtro por `connection_id`)
- `/tabelas/<connection_id>/edit/<table_name>` - Edição de colunas de tabela
- `/agendamentos` - Gerenciamento de tarefas agendadas

## 🔌 API Endpoints

### Autenticação

#### `POST /api/auth/register`
Registrar novo usuário (público).

**Request:**
```json
{
  "username": "usuario",
  "email": "usuario@exemplo.com",
  "password": "senha123"
}
```

**Response (201):**
```json
{
  "message": "User created successfully",
  "user": {
    "id": 1,
    "username": "usuario",
    "email": "usuario@exemplo.com",
    "is_admin": false,
    "is_active": true
  },
  "token": "token_gerado"
}
```

#### `POST /api/auth/login`
Fazer login.

**Request:**
```json
{
  "username": "usuario",
  "password": "senha123"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "usuario",
    "email": "usuario@exemplo.com",
    "is_admin": false,
    "is_active": true
  },
  "token": "token_gerado"
}
```

#### `POST /api/auth/logout`
Fazer logout.

**Response (200):**
```json
{
  "message": "Logout successful"
}
```

#### `GET /api/auth/me`
Obter usuário atual autenticado.

**Headers:**
```
Authorization: Bearer {token}
X-User-Id: {user_id}
```

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "username": "usuario",
    "email": "usuario@exemplo.com",
    "is_admin": false,
    "is_active": true
  }
}
```

### Setup Inicial

#### `GET /api/setup/check`
Verificar se o setup inicial é necessário.

**Response (200):**
```json
{
  "needs_setup": true
}
```

#### `POST /api/setup/create-admin`
Criar o primeiro usuário administrador (apenas se nenhum admin existir).

**Request:**
```json
{
  "username": "admin",
  "email": "admin@exemplo.com",
  "password": "senha123"
}
```

**Response (201):**
```json
{
  "message": "Admin user created successfully",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@exemplo.com",
    "is_admin": true,
    "is_active": true
  }
}
```

### Usuários (Admin Only)

#### `GET /api/users/`
Listar todos os usuários.

**Headers:**
```
Authorization: Bearer {token}
X-User-Id: {user_id}
```

**Response (200):**
```json
{
  "users": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@exemplo.com",
      "is_admin": true,
      "is_active": true,
      "groups": []
    }
  ]
}
```

#### `POST /api/users/`
Criar novo usuário.

**Request:**
```json
{
  "username": "novo_usuario",
  "email": "novo@exemplo.com",
  "password": "senha123",
  "is_admin": false,
  "group_ids": [1, 2]
}
```

#### `PUT /api/users/<user_id>`
Atualizar usuário.

**Request:**
```json
{
  "username": "usuario_atualizado",
  "email": "atualizado@exemplo.com",
  "is_admin": false,
  "is_active": true,
  "group_ids": [1]
}
```

#### `PUT /api/users/<user_id>/password`
Trocar senha de usuário.

**Request:**
```json
{
  "password": "nova_senha123"
}
```

#### `PUT /api/users/<user_id>/toggle-active`
Ativar/desativar usuário.

**Response (200):**
```json
{
  "message": "User status updated",
  "user": {
    "id": 1,
    "is_active": false
  }
}
```

#### `DELETE /api/users/<user_id>`
Deletar usuário (remove de todos os grupos).

**Response (200):**
```json
{
  "message": "User deleted successfully and removed from all groups"
}
```

### Grupos (Admin Only)

#### `GET /api/groups/`
Listar todos os grupos.

**Response (200):**
```json
{
  "groups": [
    {
      "id": 1,
      "name": "Administradores",
      "description": "Acesso total ao sistema",
      "can_create_connections": true,
      "can_create_projects": true,
      "can_view_dashboards": true,
      "can_edit_tables": true,
      "can_view_tables": true,
      "can_view_reports": true,
      "can_download_reports": true,
      "user_count": 2
    }
  ]
}
```

#### `POST /api/groups/`
Criar novo grupo.

**Request:**
```json
{
  "name": "Novo Grupo",
  "description": "Descrição do grupo",
  "can_create_connections": true,
  "can_create_projects": false,
  "can_view_dashboards": true,
  "can_edit_tables": false,
  "can_view_tables": true,
  "can_view_reports": true,
  "can_download_reports": false
}
```

#### `GET /api/groups/<group_id>`
Obter detalhes de um grupo.

#### `PUT /api/groups/<group_id>`
Atualizar grupo.

#### `DELETE /api/groups/<group_id>`
Deletar grupo.

#### `GET /api/groups/<group_id>/users`
Listar usuários de um grupo.

#### `POST /api/groups/<group_id>/users/<user_id>`
Adicionar usuário a um grupo.

#### `DELETE /api/groups/<group_id>/users/<user_id>`
Remover usuário de um grupo.

#### `GET /api/groups/users/<user_id>`
Obter grupos de um usuário.

### Conexões de Banco de Dados

#### `GET /api/connections`
Listar conexões do usuário.

**Headers:**
```
Authorization: Bearer {token}
X-User-Id: {user_id}
```

#### `POST /api/connections`
Criar nova conexão.

**Request (MariaDB/MySQL):**
```json
{
  "name": "Conexão Produção",
  "description": "Banco de produção",
  "db_type": "mariadb",
  "db_config": {
    "host": "localhost",
    "port": 3306,
    "user": "usuario",
    "password": "senha",
    "database": "banco_dados"
  }
}
```

**Request (SQLite):**
```json
{
  "name": "Conexão Local",
  "db_type": "sqlite",
  "db_config": {
    "path": "/caminho/para/banco.db"
  }
}
```

#### `GET /api/connections/<connection_id>`
Obter detalhes de uma conexão.

#### `PUT /api/connections/<connection_id>`
Atualizar conexão.

#### `DELETE /api/connections/<connection_id>`
Deletar conexão (soft delete).

#### `POST /api/connections/<connection_id>/test`
Testar conexão.

#### `GET /api/connections/<connection_id>/tables`
Listar tabelas de uma conexão.

#### `GET /api/connections/<connection_id>/tables/<table_name>/info`
Obter informações de uma tabela (colunas, chaves primárias, etc).

### Projetos

#### `GET /api/projects`
Listar projetos. Usuários veem projetos criados por qualquer usuário com permissão de executar projetos. Administradores veem todos os projetos.

**Comportamento:**
- Administradores: Veem todos os projetos ativos
- Usuários regulares: Veem projetos criados por usuários que têm `can_execute_projects=True` em seus grupos
- Isso permite compartilhamento automático de projetos entre equipes

#### `POST /api/projects`
Criar novo projeto. Requer permissão `can_create_projects`.

**Request:**
```json
{
  "name": "Projeto Comparação",
  "description": "Comparar tabelas A e B",
  "source_connection_id": 1,
  "target_connection_id": 2,
  "source_table": "tabela_origem",
  "target_table": "tabela_destino"
}
```

#### `GET /api/projects/<project_id>`
Obter detalhes de um projeto.

#### `PUT /api/projects/<project_id>`
Atualizar projeto.

#### `DELETE /api/projects/<project_id>`
Deletar projeto (soft delete).

### Comparações

#### `POST /api/comparisons/project/<project_id>`
Executar comparação.

**Request:**
```json
{
  "key_mappings": {
    "id": "user_id",
    "email": "email_address"
  }
}
```

**Response (200):**
```json
{
  "message": "Comparison completed",
  "comparison_id": 1,
  "stats": {
    "total_records": 100,
    "added": 5,
    "modified": 10,
    "deleted": 2
  }
}
```

#### `GET /api/comparisons/project/<project_id>`
Listar comparações de um projeto.

#### `GET /api/comparisons`
Listar todas as comparações do usuário.

#### `GET /api/comparisons/<comparison_id>/results`
Obter resultados detalhados de uma comparação.

#### `DELETE /api/comparisons/<comparison_id>`
Deletar uma comparação específica e seus resultados.

**Response (200):**
```json
{
  "message": "Comparison deleted successfully"
}
```

#### `DELETE /api/comparisons/project/<project_id>`
Deletar todas as comparações de um projeto.

**Response (200):**
```json
{
  "message": "All comparisons for project \"Nome do Projeto\" deleted successfully",
  "deleted_count": 5,
  "project_id": 1,
  "project_name": "Nome do Projeto"
}
```

#### `POST /api/comparisons/project/<project_id>/send-changes`
Enviar mudanças para API externa.

### Agendamento de Tarefas

#### `GET /api/scheduled-tasks`
Listar todas as tarefas agendadas do usuário.

**Headers:**
```
Authorization: Bearer {token}
X-User-Id: {user_id}
```

**Response (200):**
```json
{
  "tasks": [
    {
      "id": 1,
      "name": "Comparação Diária",
      "description": "Executa comparação todos os dias",
      "project_id": 1,
      "project_name": "Projeto Teste",
      "schedule_type": "preset",
      "schedule_value": "daily",
      "key_mappings": {
        "id": "user_id",
        "email": "email_address"
      },
      "is_active": true,
      "last_run_at": "2024-01-15T10:00:00",
      "next_run_at": "2024-01-16T00:00:00",
      "last_run_status": "success",
      "total_runs": 10,
      "successful_runs": 9,
      "failed_runs": 1
    }
  ]
}
```

#### `GET /api/scheduled-tasks/<task_id>`
Obter detalhes de uma tarefa agendada específica.

#### `POST /api/scheduled-tasks`
Criar nova tarefa agendada.

**Request:**
```json
{
  "name": "Comparação a cada 15 minutos",
  "description": "Executa comparação a cada 15 minutos",
  "project_id": 1,
  "schedule_type": "preset",
  "schedule_value": "15min",
  "key_mappings": {
    "id": "user_id",
    "email": "email_address"
  },
  "is_active": true
}
```

**Tipos de Agendamento (`schedule_type`):**
- `preset`: Valores pré-definidos (`schedule_value`: `15min`, `1hour`, `6hours`, `12hours`, `daily`)
- `interval`: Intervalo em minutos (`schedule_value`: número de minutos, ex: `30`)
- `cron`: Expressão CRON (`schedule_value`: expressão CRON, ex: `0 0 * * *` para diário à meia-noite)

**Response (201):**
```json
{
  "message": "Scheduled task created successfully",
  "task": {
    "id": 1,
    "name": "Comparação a cada 15 minutos",
    "next_run_at": "2024-01-15T10:15:00",
    "is_active": true
  }
}
```

#### `PUT /api/scheduled-tasks/<task_id>`
Atualizar tarefa agendada.

**Request:**
```json
{
  "name": "Comparação Atualizada",
  "schedule_type": "cron",
  "schedule_value": "0 */6 * * *",
  "key_mappings": {
    "id": "user_id"
  },
  "is_active": true
}
```

#### `DELETE /api/scheduled-tasks/<task_id>`
Deletar tarefa agendada.

**Response (200):**
```json
{
  "message": "Scheduled task deleted successfully"
}
```

#### `PUT /api/scheduled-tasks/<task_id>/toggle`
Ativar/desativar tarefa agendada.

**Response (200):**
```json
{
  "message": "Scheduled task toggled successfully",
  "task": {
    "id": 1,
    "is_active": false
  }
}
```

#### `POST /api/scheduled-tasks/<task_id>/run-now`
Executar tarefa agendada manualmente (redireciona para página de execução).

**Response (200):**
```json
{
  "message": "Redirecting to execution page",
  "redirect_url": "/comparacao/1/execution?source_key=id&target_key=user_id"
}
```

#### `GET /api/scheduled-tasks/project/<project_id>/columns`
Obter colunas das tabelas origem e destino de um projeto.

**Response (200):**
```json
{
  "source_columns": ["id", "nome", "email"],
  "target_columns": ["user_id", "name", "email_address"],
  "source_primary_keys": ["id"],
  "target_primary_keys": ["user_id"],
  "source_table": "usuarios",
  "target_table": "users"
}
```

### Webhooks e Cliente HTTP

O DeltaScope inclui um cliente HTTP integrado (tipo Postman) para enviar requisições HTTP para servidores externos, com suporte a templates de payload usando namespaces para substituir valores dinamicamente.

#### Namespaces Disponíveis

Os templates de payload suportam placeholders no formato `{{namespace.key}}` que são substituídos automaticamente pelos valores reais quando o webhook é enviado.

##### Namespace: `comparison`
Dados da comparação executada:
- `{{comparison.id}}` - ID da comparação
- `{{comparison.project_id}}` - ID do projeto
- `{{comparison.executed_at}}` - Data/hora de execução (ISO format)
- `{{comparison.status}}` - Status (pending, running, completed, failed)
- `{{comparison.total_differences}}` - Total de diferenças encontradas

##### Namespace: `difference` ou `result`
Dados de uma diferença individual:
- `{{difference.id}}` - ID da diferença/resultado
- `{{difference.comparison_id}}` - ID da comparação
- `{{difference.record_id}}` - ID do registro (chave primária)
- `{{difference.field_name}}` - Nome do campo alterado
- `{{difference.source_value}}` - Valor na origem
- `{{difference.target_value}}` - Valor no destino
- `{{difference.change_type}}` - Tipo de mudança (added, modified, deleted)
- `{{difference.detected_at}}` - Data/hora de detecção (ISO format)

##### Namespace: `json_raw` (Novo)
Acessa todos os campos do registro completo da tabela destino, incluindo as chaves primárias usadas para comparação:
- `{{json_raw.email}}` - Acessa o campo `email` do registro destino
- `{{json_raw.id}}` - Acessa o campo `id` do registro destino
- `{{json_raw.campo_qualquer}}` - Substitua `campo_qualquer` pelo nome real da coluna no banco de dados

**Nota:** Use o nome exato da coluna como aparece no banco de dados. O namespace `json_raw` contém todos os dados do registro completo da tabela destino, incluindo chaves primárias.

**Importante sobre Aspas Duplas:** Quando você usa placeholders em templates JSON, os valores de **string** são automaticamente envolvidos em aspas duplas. Valores numéricos e booleanos não recebem aspas. Isso garante que o JSON gerado seja sempre válido.

**Exemplo:** Se `{{json_raw.email}}` retornar `usuario@exemplo.com`, ele será inserido como `"usuario@exemplo.com"` no JSON final.

##### Namespace: `project` (quando disponível)
Dados do projeto:
- `{{project.id}}` - ID do projeto
- `{{project.name}}` - Nome do projeto
- `{{project.description}}` - Descrição do projeto
- `{{project.source_table}}` - Nome da tabela origem
- `{{project.target_table}}` - Nome da tabela destino

#### Exemplos de Templates

**Exemplo Básico:**
```json
{
  "comparison_id": "{{comparison.id}}",
  "project_id": "{{comparison.project_id}}",
  "total_differences": "{{comparison.total_differences}}",
  "status": "{{comparison.status}}"
}
```

**Exemplo Detalhado:**
```json
{
  "comparison": {
    "id": "{{comparison.id}}",
    "project_id": "{{comparison.project_id}}",
    "executed_at": "{{comparison.executed_at}}",
    "total_differences": "{{comparison.total_differences}}"
  },
  "difference": {
    "id": "{{difference.id}}",
    "record_id": "{{difference.record_id}}",
    "field_name": "{{difference.field_name}}",
    "source_value": "{{difference.source_value}}",
    "target_value": "{{difference.target_value}}",
    "change_type": "{{difference.change_type}}",
    "detected_at": "{{difference.detected_at}}"
  }
}
```

**Exemplo Notificação Webhook:**
```json
{
  "event": "comparison.difference.detected",
  "timestamp": "{{difference.detected_at}}",
  "data": {
    "comparison_id": "{{comparison.id}}",
    "project_id": "{{comparison.project_id}}",
    "record_id": "{{difference.record_id}}",
    "field": "{{difference.field_name}}",
    "old_value": "{{difference.source_value}}",
    "new_value": "{{difference.target_value}}",
    "change_type": "{{difference.change_type}}"
  }
}
```

**Exemplo com json_raw (Dados Completos do Registro Destino):**
```json
{
  "leader": {{json_raw.reportsto}},
  "cost_center": {{json_raw.customcostcenter}},
  "action": "update",
  "leader_email": {{json_raw.supervisoremail}},
  "employee_email": {{json_raw.workemail}}
}
```

**Resultado processado:**
```json
{
  "leader": "João Silva (1234)",
  "cost_center": 999,
  "action": "update",
  "leader_email": "joao.silva@exemplo.com",
  "employee_email": "funcionario@exemplo.com"
}
```

**Nota:** Valores de string são automaticamente envolvidos em aspas duplas. Valores numéricos não recebem aspas.

#### `GET /api/webhooks/configs`
Listar todas as configurações de webhook do usuário.

**Headers:**
```
Authorization: Bearer {token}
X-User-Id: {user_id}
```

**Response (200):**
```json
{
  "configs": [
    {
      "id": 1,
      "name": "Webhook Produção",
      "description": "Envia notificações para API de produção",
      "url": "https://api.exemplo.com/webhook",
      "method": "POST",
      "headers": {
        "Content-Type": "application/json"
      },
      "auth_type": "bearer",
      "is_active": true,
      "created_at": "2024-01-15T10:00:00"
    }
  ]
}
```

#### `POST /api/webhooks/configs`
Criar nova configuração de webhook.

**Request:**
```json
{
  "name": "Webhook Produção",
  "description": "Envia notificações para API de produção",
  "url": "https://api.exemplo.com/webhook",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json",
    "X-Custom-Header": "valor"
  },
  "auth_type": "bearer",
  "auth_config": {
    "token": "seu_token_aqui"
  },
  "default_payload": "{\"event\": \"comparison.detected\", \"comparison_id\": \"{{comparison.id}}\"}",
  "is_active": true
}
```

**Tipos de Autenticação (`auth_type`):**
- `none` - Sem autenticação
- `bearer` - Bearer Token (requer `token` em `auth_config`)
- `basic` - Basic Auth (requer `username` e `password` em `auth_config`)
- `api_key` - API Key (requer `key_name` e `key_value` em `auth_config`)

**Nota:** Todas as credenciais (`token`, `password`, `key_value`) são criptografadas antes de serem armazenadas no banco de dados.

#### `POST /api/webhooks/send`
Enviar requisição HTTP manualmente (cliente HTTP).

**Request:**
```json
{
  "url": "https://api.exemplo.com/webhook",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer token123"
  },
  "payload": {
    "event": "test",
    "data": "{{comparison.id}}"
  }
}
```

**Response (200):**
```json
{
  "message": "Request sent successfully",
  "status_code": 200,
  "response": "{\"success\": true}",
  "headers": {
    "Content-Type": "application/json"
  }
}
```

#### `POST /api/webhooks/process-template`
Processar um template de payload com dados fornecidos.

**Request:**
```json
{
  "template": "{\"comparison_id\": \"{{comparison.id}}\", \"field\": \"{{difference.field_name}}\"}",
  "comparison": {
    "id": 1,
    "project_id": 1,
    "total_differences": 5
  },
  "difference": {
    "id": 10,
    "field_name": "nome",
    "source_value": "João",
    "target_value": "João Silva"
  }
}
```

**Response (200):**
```json
{
  "processed": {
    "comparison_id": "1",
    "field": "nome"
  }
}
```

#### `GET /api/webhooks/payloads`
Listar todos os templates de payload salvos.

#### `POST /api/webhooks/payloads`
Criar novo template de payload.

**Request:**
```json
{
  "name": "Notificação de Diferença",
  "description": "Template para notificar diferenças detectadas",
  "payload_template": "{\"event\": \"difference.detected\", \"comparison_id\": \"{{comparison.id}}\", \"field\": \"{{difference.field_name}}\"}",
  "payload_example": "{\"event\": \"difference.detected\", \"comparison_id\": \"1\", \"field\": \"nome\"}"
}
```

#### Envio em Massa de Diferenças para Webhook

Na página de resultados de comparação (`/relatorios/<comparison_id>/resultados`), você pode enviar todas as diferenças encontradas para um webhook configurado em loop.

**Como Funciona:**

1. **Acesse a página de resultados** de uma comparação executada
2. **Clique no botão "Enviar Todas as Diferenças para Webhook"**
3. **Configure o envio:**
   - Selecione um webhook previamente configurado
   - Escolha filtrar por campo específico (ex: "username") ou enviar todos os campos
   - Escolha enviar no Body (Payload) ou Parâmetros (Query String)
   - Escolha qual valor enviar: Origem ou Destino
4. **O sistema enviará em loop:**
   - Se você selecionar o campo "username" e houver 5 diferenças nesse campo, serão enviadas 5 requisições
   - Cada requisição usa o mesmo payload template do webhook configurado
   - Os namespaces `{{comparison.*}}`, `{{difference.*}}` e `{{project.*}}` são substituídos automaticamente com os dados específicos de cada diferença
   - As requisições são enviadas sequencialmente (uma por vez) com um pequeno delay de 100ms entre elas

**Exemplo de Uso:**

Suponha que você tenha:
- Uma comparação com ID 16
- 5 diferenças no campo "username"
- Um webhook configurado com o payload template:
```json
{
  "event": "field.changed",
  "comparison_id": "{{comparison.id}}",
  "field_name": "{{difference.field_name}}",
  "record_id": "{{difference.record_id}}",
  "old_value": "{{difference.source_value}}",
  "new_value": "{{difference.target_value}}",
  "change_type": "{{difference.change_type}}"
}
```

Ao clicar em "Enviar Todas as Diferenças para Webhook" e selecionar:
- Webhook: "Meu Webhook"
- Campo: "username"
- Enviar em: Body (Payload)
- Valor: Origem

O sistema enviará 5 requisições HTTP, uma para cada diferença encontrada no campo "username", substituindo os placeholders com os dados específicos de cada diferença.

**Recursos:**

- ✅ **Barra de progresso em tempo real**: Mostra o progresso do envio (ex: "3 / 5")
- ✅ **Log detalhado**: Exibe o resultado de cada envio (sucesso ou erro)
- ✅ **Filtro por campo**: Permite enviar apenas diferenças de um campo específico
- ✅ **Processamento de templates**: Suporta todos os namespaces disponíveis
- ✅ **Envio sequencial**: Evita sobrecarregar o servidor de destino
- ✅ **Resumo final**: Mostra total de sucessos e erros ao final

**URL da Página:**
```
/relatorios/<comparison_id>/resultados
```

### Dashboard

#### `GET /api/dashboard/project/<project_id>/stats`
Obter estatísticas do projeto.

**Query Parameters:**
- `start_date` (opcional): Data inicial (ISO format: YYYY-MM-DDTHH:mm:ss)
- `end_date` (opcional): Data final (ISO format: YYYY-MM-DDTHH:mm:ss)

**Response:**
```json
{
  "total_comparisons": 10,
  "completed_comparisons": 8,
  "total_changes": 150,
  "total_differences": 120,
  "unsent_changes": 5,
  "modified_fields_count": 25
}
```

#### `GET /api/dashboard/project/<project_id>/changes-over-time`
Obter mudanças ao longo do tempo (para gráfico de linha).

**Query Parameters:**
- `start_date` (opcional)
- `end_date` (opcional)

**Response:**
```json
{
  "data": {
    "2024-01-01": {
      "added": 5,
      "modified": 10,
      "deleted": 2
    },
    "2024-01-02": {
      "added": 3,
      "modified": 8,
      "deleted": 1
    }
  }
}
```

#### `GET /api/dashboard/project/<project_id>/field-changes`
Obter mudanças por campo (para gráfico de pizza e barras).

**Query Parameters:**
- `start_date` (opcional)
- `end_date` (opcional)

**Response:**
```json
{
  "data": [
    {"field": "nome", "count": 45},
    {"field": "email", "count": 30},
    {"field": "ativo", "count": 15}
  ]
}
```

#### `GET /api/dashboard/project/<project_id>/changes-by-type`
Obter mudanças agrupadas por tipo (added, modified, deleted).

**Query Parameters:**
- `start_date` (opcional)
- `end_date` (opcional)

**Response:**
```json
{
  "data": {
    "added": 20,
    "modified": 50,
    "deleted": 10
  }
}
```

#### `GET /api/dashboard/project/<project_id>/comparisons-by-status`
Obter comparações agrupadas por status.

**Response:**
```json
{
  "data": {
    "pending": 2,
    "running": 1,
    "completed": 15,
    "failed": 1
  }
}
```

### Tabelas

#### `POST /api/tables/test-connection`
Testar conexão com banco de dados.

#### `POST /api/tables/list`
Listar tabelas de um banco.

#### `POST /api/tables/columns`
Obter colunas de uma tabela.

#### `POST /api/tables/update-column-type`
Atualizar tipo de coluna no banco de dados e regenerar modelo.

**Request:**
```json
{
  "connection_id": 1,
  "table_name": "usuarios",
  "column_name": "ativo",
  "new_type": "BOOLEAN",
  "nullable": true,
  "primary_key": false
}
```

**Response (200):**
```json
{
  "message": "Column type updated successfully. Models regenerated for 1 project(s).",
  "updated_projects": [
    {"id": 1, "name": "Projeto Teste"}
  ],
  "model_file_path": "app/models/generated/ProjetoTeste_usuarios_model.py"
}
```

**Notas:**
- Para SQLite: Recria a tabela com a nova estrutura (única forma de alterar tipos)
- Para MySQL/MariaDB: Usa `ALTER TABLE MODIFY COLUMN`
- Sempre atualiza o modelo SQLAlchemy local
- Cria ou atualiza o `TableModelMapping` no banco

#### `POST /api/tables/update-primary-keys`
Atualizar chaves primárias de uma tabela.

#### `GET /api/tables/model/<connection_id>/<table_name>`
Obter código do modelo SQLAlchemy gerado.

## 🔗 Filtros por URL

O sistema suporta filtros diretamente na URL para facilitar compartilhamento e bookmarking.

### Dashboard

**URL Base:**
```
/dashboard
```

**Com Filtros:**
```
/dashboard?project_id=1&start_date=2024-01-01T00:00&end_date=2024-01-31T23:59
```

**Parâmetros:**
- `project_id` (opcional): ID do projeto a visualizar
- `start_date` (opcional): Data de início (formato: `YYYY-MM-DDTHH:mm`)
- `end_date` (opcional): Data de fim (formato: `YYYY-MM-DDTHH:mm`)

**Exemplos:**
```
# Dashboard com projeto específico
/dashboard?project_id=1

# Dashboard com período específico
/dashboard?project_id=1&start_date=2024-01-01T00:00&end_date=2024-01-31T23:59

# Dashboard apenas com data de início
/dashboard?project_id=1&start_date=2024-01-15T08:00
```

**Comportamento:**
- Ao acessar uma URL com parâmetros, os campos são preenchidos automaticamente
- Se houver `project_id` na URL, o dashboard carrega automaticamente
- Ao alterar filtros, a URL é atualizada automaticamente (sem recarregar a página)
- A URL pode ser compartilhada e manterá os filtros aplicados

### Tabelas

**URL Base:**
```
/tabelas
```

**Com Conexão Selecionada:**
```
/tabelas?connection_id=1
```

**Parâmetros:**
- `connection_id` (opcional): ID da conexão a visualizar

**Comportamento:**
- Ao acessar com `connection_id`, a conexão é selecionada automaticamente
- As tabelas são carregadas automaticamente
- Ao voltar de uma página de edição, a conexão permanece selecionada

### Relatórios

**URL Base:**
```
/relatorios
```

**Com Filtro por Projeto:**
```
/relatorios?project_id=1
```

**Parâmetros:**
- `project_id` (opcional): ID do projeto para filtrar relatórios

**Resultados de Comparação:**
```
/relatorios/<comparison_id>/resultados
```

**Comportamento:**
- Ao acessar com `project_id`, o projeto é selecionado automaticamente
- Os relatórios são carregados automaticamente para o projeto selecionado
- A URL pode ser compartilhada para acesso direto aos relatórios de um projeto

### Execução de Comparação

**URL Base:**
```
/comparacao/<project_id>/execution
```

**Com Mapeamento de Chaves Primárias:**
```
/comparacao/1/execution?source_key=id&target_key=user_id&source_key=email&target_key=email_address
```

**Parâmetros:**
- `source_key` (múltiplos): Nome da coluna na tabela origem
- `target_key` (múltiplos): Nome da coluna correspondente na tabela destino

**Exemplos:**
```
# Mapeamento simples (uma chave)
/comparacao/1/execution?source_key=id&target_key=user_id

# Mapeamento múltiplo (chaves compostas)
/comparacao/1/execution?source_key=id&target_key=user_id&source_key=email&target_key=email_address

# Mapeamento com 3 chaves
/comparacao/1/execution?source_key=id&target_key=user_id&source_key=code&target_key=product_code&source_key=date&target_key=created_date
```

**Comportamento:**
- Ao acessar com parâmetros `source_key` e `target_key`, as chaves são mapeadas automaticamente
- As checkboxes correspondentes são marcadas automaticamente
- A comparação pode ser executada automaticamente após carregar as colunas (se configurado)
- Útil para execução de tarefas agendadas ou compartilhamento de links de comparação específica

## 👥 Gerenciamento de Usuários

### Cadastro Público de Usuário

Qualquer pessoa pode criar uma conta através da página pública de cadastro.

**URL:** `/create_user`

**Características:**
- Página pública (não requer autenticação)
- O primeiro usuário criado será automaticamente um administrador
- Validação de dados em tempo real
- Verificação de duplicatas (username e email)
- Senha mínima de 6 caracteres

**Campos:**
- Usuário (obrigatório, único)
- Email (obrigatório, único, formato válido)
- Senha (obrigatório, mínimo 6 caracteres)
- Confirmar Senha (obrigatório, deve coincidir)

### Criação de Usuário por Administrador

Administradores podem criar usuários através da interface administrativa.

**URL:** `/usuarios/novo`

**Características:**
- Requer autenticação como administrador
- Permite definir grupos do usuário
- Permite definir se o usuário é administrador
- Validação completa de dados

### Listar Usuários

**Via Interface Web:**
1. Faça login como administrador
2. Acesse "Usuários" no menu
3. Visualize todos os usuários com seus grupos

**Via API:**
```bash
curl -X GET http://localhost:5000/api/users/ \
  -H "Authorization: Bearer {token}" \
  -H "X-User-Id: {user_id}"
```

### Criar Usuário

**Via Interface Web:**
1. Acesse "Usuários" > "Novo Usuário"
2. Preencha os dados
3. Selecione os grupos (opcional)
4. Clique em "Criar"

**Via API:**
```bash
curl -X POST http://localhost:5000/api/users/ \
  -H "Authorization: Bearer {token}" \
  -H "X-User-Id: {user_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "novo_usuario",
    "email": "novo@exemplo.com",
    "password": "senha123",
    "is_admin": false,
    "group_ids": [1, 2]
  }'
```

**Via Script Python:**
```python
import requests

url = "http://localhost:5000/api/users/"
headers = {
    "Authorization": "Bearer {token}",
    "X-User-Id": "{user_id}",
    "Content-Type": "application/json"
}
data = {
    "username": "novo_usuario",
    "email": "novo@exemplo.com",
    "password": "senha123",
    "is_admin": False,
    "group_ids": [1]
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### Deletar Usuário

**Via Interface Web:**
1. Acesse "Usuários"
2. Clique no botão de deletar do usuário
3. Confirme a ação

**Proteções:**
- Administradores não podem deletar a si mesmos
- Usuário é removido automaticamente de todos os grupos

**Via API:**
```bash
curl -X DELETE http://localhost:5000/api/users/2 \
  -H "Authorization: Bearer {token}" \
  -H "X-User-Id: {user_id}"
```

### Ativar/Desativar Usuário

**Via Interface Web:**
1. Acesse "Usuários"
2. Clique no botão de ativar/desativar

**Proteções:**
- Administradores não podem desativar a si mesmos
- Usuários desativados não podem fazer login

**Via API:**
```bash
curl -X PUT http://localhost:5000/api/users/2/toggle-active \
  -H "Authorization: Bearer {token}" \
  -H "X-User-Id: {user_id}"
```

### Trocar Senha

**Via Interface Web:**
1. Acesse "Usuários"
2. Clique em "Alterar Senha" do usuário
3. Digite a nova senha
4. Confirme

**Via Script CLI:**
```bash
python change_password.py usuario nova_senha123
```

## 👥 Gerenciamento de Grupos

### Criar Grupo

**Via Interface Web:**
1. Faça login como administrador
2. Acesse "Grupos" no menu
3. Clique em "Novo Grupo"
4. Configure as permissões
5. Clique em "Salvar"

**Via API:**
```bash
curl -X POST http://localhost:5000/api/groups/ \
  -H "Authorization: Bearer {token}" \
  -H "X-User-Id: {user_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Editores",
    "description": "Podem editar tabelas",
    "can_create_connections": false,
    "can_create_projects": false,
    "can_view_dashboards": true,
    "can_edit_tables": true,
    "can_view_tables": true,
    "can_view_reports": true,
    "can_download_reports": true
  }'
```

### Adicionar Usuário a Grupo

**Via Interface Web:**
1. Acesse "Grupos"
2. Clique em "Ver Usuários" do grupo
3. Clique em "Adicionar Usuário"
4. Selecione o usuário
5. Confirme

**Via API:**
```bash
curl -X POST http://localhost:5000/api/groups/1/users/2 \
  -H "Authorization: Bearer {token}" \
  -H "X-User-Id: {user_id}"
```

### Remover Usuário de Grupo

**Via Interface Web:**
1. Acesse "Grupos"
2. Clique em "Ver Usuários"
3. Clique em "Remover" ao lado do usuário

**Via API:**
```bash
curl -X DELETE http://localhost:5000/api/groups/1/users/2 \
  -H "Authorization: Bearer {token}" \
  -H "X-User-Id: {user_id}"
```

### Deletar Grupo

**Via Interface Web:**
1. Acesse "Grupos"
2. Clique em "Deletar" do grupo
3. Confirme

**Via API:**
```bash
curl -X DELETE http://localhost:5000/api/groups/1 \
  -H "Authorization: Bearer {token}" \
  -H "X-User-Id: {user_id}"
```

## 🔧 Edição de Tabelas

### Visualizar Tabelas

1. Acesse "Tabelas" no menu
2. Selecione uma conexão
3. Visualize todas as tabelas disponíveis
4. Clique em "Informações" para ver detalhes da tabela
5. Clique em "Editar" para editar colunas

### Editar Colunas de Tabela

**URL:** `/tabelas/<connection_id>/edit/<table_name>`

**Funcionalidades:**
- Visualizar todas as colunas da tabela
- Alterar tipo de dado da coluna
- Modificar propriedade nullable (permite nulos ou não)
- Modificar chave primária
- Salvar alterações no banco de dados
- Atualizar modelo SQLAlchemy local automaticamente

**Tipos de Dados Suportados:**
- VARCHAR(255)
- TEXT
- INT
- BIGINT
- DECIMAL(10,2)
- DATE
- DATETIME
- TIMESTAMP
- BOOLEAN
- TINYINT(1)

**Comportamento por Banco:**

**SQLite:**
- Recria a tabela com a nova estrutura
- Copia todos os dados da tabela antiga
- Remove a tabela antiga
- Renomeia a nova tabela

**MySQL/MariaDB:**
- Usa `ALTER TABLE MODIFY COLUMN`
- Atualiza dados existentes quando necessário (ex: conversão para Boolean)
- Suporta alteração de chaves primárias

**Após Salvar:**
- Alterações são aplicadas no banco de dados
- Modelo SQLAlchemy é regenerado automaticamente
- `TableModelMapping` é criado ou atualizado
- Página recarrega mostrando as alterações

## 📊 Dashboard e Gráficos

### Acessar Dashboard

**URL:** `/dashboard`

**Com Filtros:**
```
/dashboard?project_id=1&start_date=2024-01-01T00:00&end_date=2024-01-31T23:59
```

### Gráficos Disponíveis

1. **Mudanças ao Longo do Tempo** (Linha)
   - Mostra evolução de mudanças por dia
   - Separa por tipo: Adicionado, Modificado, Deletado
   - Altura: 400px

2. **Mudanças por Campo** (Barras)
   - Mostra quantidade de mudanças por campo
   - Ordenado por quantidade (maior para menor)
   - Altura: 600px (aumentada para evitar corte de números)

3. **Campos Modificados no Período** (Pizza)
   - Distribuição percentual de mudanças por campo
   - Cores automáticas para melhor visualização
   - Altura: 500px

4. **Mudanças por Tipo** (Pizza)
   - Distribuição entre Adicionado, Modificado e Deletado
   - Cores: Verde (Adicionado), Amarelo (Modificado), Vermelho (Deletado)
   - Altura: 500px

5. **Comparações por Status** (Barras)
   - Quantidade de comparações por status
   - Status: Pendente, Em Execução, Concluída, Falhou
   - Altura: 400px

6. **Tendência de Mudanças** (Área)
   - Evolução do total de mudanças ao longo do tempo
   - Gráfico de área preenchido
   - Altura: 400px

### Estatísticas Exibidas

- **Total de Comparações**: Número total de comparações executadas
- **Total de Mudanças**: Número total de mudanças detectadas
- **Campos Modificados**: Quantidade de campos únicos modificados
- **Comparações Concluídas**: Comparações com status "completed"
- **Total de Diferenças**: Soma de todas as diferenças encontradas
- **Mudanças Não Enviadas**: Mudanças ainda não enviadas para API externa

### Filtros de Data

- **Data Início**: Filtra desde esta data
- **Data Fim**: Filtra até esta data
- **Botão "Hoje"**: Define automaticamente início e fim do dia atual
- Todos os gráficos respeitam os filtros de data selecionados

## 💻 Exemplos de Código

### Python

#### Autenticação e Listar Projetos

```python
import requests

# Login
login_url = "http://localhost:5000/api/auth/login"
login_data = {
    "username": "admin",
    "password": "senha123"
}

response = requests.post(login_url, json=login_data)
data = response.json()

if response.status_code == 200:
    token = data['token']
    user_id = data['user']['id']
    
    # Listar projetos
    projects_url = "http://localhost:5000/api/projects"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-User-Id": str(user_id)
    }
    
    projects_response = requests.get(projects_url, headers=headers)
    projects = projects_response.json()
    
    print("Projetos:", projects)
else:
    print("Erro no login:", data['message'])
```

#### Criar Conexão de Banco

```python
import requests

token = "seu_token_aqui"
user_id = 1

url = "http://localhost:5000/api/connections"
headers = {
    "Authorization": f"Bearer {token}",
    "X-User-Id": str(user_id),
    "Content-Type": "application/json"
}

# Conexão MariaDB
connection_data = {
    "name": "Banco Produção",
    "description": "Banco de dados de produção",
    "db_type": "mariadb",
    "db_config": {
        "host": "localhost",
        "port": 3306,
        "user": "usuario",
        "password": "senha",
        "database": "meu_banco"
    }
}

response = requests.post(url, json=connection_data, headers=headers)
print(response.json())
```

#### Executar Comparação

```python
import requests

token = "seu_token_aqui"
user_id = 1
project_id = 1

url = f"http://localhost:5000/api/comparisons/project/{project_id}"
headers = {
    "Authorization": f"Bearer {token}",
    "X-User-Id": str(user_id),
    "Content-Type": "application/json"
}

# Mapeamento de chaves primárias
key_mappings = {
    "id": "user_id",  # coluna origem -> coluna destino
    "email": "email_address"
}

data = {
    "key_mappings": key_mappings
}

response = requests.post(url, json=data, headers=headers)
result = response.json()

print("Comparação ID:", result['comparison_id'])
print("Estatísticas:", result['stats'])
```

#### Obter Dashboard com Filtros

```python
import requests
from datetime import datetime

token = "seu_token_aqui"
user_id = 1
project_id = 1

# Definir período
start_date = datetime(2024, 1, 1, 0, 0, 0).isoformat()
end_date = datetime(2024, 1, 31, 23, 59, 59).isoformat()

url = f"http://localhost:5000/api/dashboard/project/{project_id}/stats"
params = {
    "start_date": start_date,
    "end_date": end_date
}
headers = {
    "Authorization": f"Bearer {token}",
    "X-User-Id": str(user_id)
}

response = requests.get(url, params=params, headers=headers)
stats = response.json()

print("Total de comparações:", stats['total_comparisons'])
print("Total de mudanças:", stats['total_changes'])
print("Campos modificados:", stats['modified_fields_count'])
```

#### Atualizar Tipo de Coluna

```python
import requests

token = "seu_token_aqui"
user_id = 1

url = "http://localhost:5000/api/tables/update-column-type"
headers = {
    "Authorization": f"Bearer {token}",
    "X-User-Id": str(user_id),
    "Content-Type": "application/json"
}
data = {
    "connection_id": 1,
    "table_name": "usuarios",
    "column_name": "ativo",
    "new_type": "BOOLEAN",
    "nullable": True,
    "primary_key": False
}

response = requests.post(url, json=data, headers=headers)
result = response.json()

print("Mensagem:", result['message'])
print("Modelo atualizado:", result['model_file_path'])
```

### cURL

#### Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "senha123"
  }'
```

#### Criar Usuário (Admin)

```bash
TOKEN="seu_token_aqui"
USER_ID=1

curl -X POST http://localhost:5000/api/users/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "novo_usuario",
    "email": "novo@exemplo.com",
    "password": "senha123",
    "is_admin": false,
    "group_ids": [1, 2]
  }'
```

#### Criar Conexão

```bash
TOKEN="seu_token_aqui"
USER_ID=1

curl -X POST http://localhost:5000/api/connections \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Banco Local",
    "db_type": "sqlite",
    "db_config": {
      "path": "/caminho/para/banco.db"
    }
  }'
```

#### Executar Comparação

```bash
TOKEN="seu_token_aqui"
USER_ID=1
PROJECT_ID=1

curl -X POST http://localhost:5000/api/comparisons/project/$PROJECT_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "key_mappings": {
      "id": "user_id"
    }
  }'
```

#### Obter Dashboard com Filtros

```bash
TOKEN="seu_token_aqui"
USER_ID=1
PROJECT_ID=1

curl -X GET "http://localhost:5000/api/dashboard/project/$PROJECT_ID/stats?start_date=2024-01-01T00:00:00&end_date=2024-01-31T23:59:59" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID"
```

### PHP

#### Classe para Integração

```php
<?php

class DeltaScopeClient {
    private $baseUrl;
    private $token;
    private $userId;
    
    public function __construct($baseUrl, $token, $userId) {
        $this->baseUrl = rtrim($baseUrl, '/');
        $this->token = $token;
        $this->userId = $userId;
    }
    
    private function request($method, $endpoint, $data = null) {
        $url = $this->baseUrl . $endpoint;
        
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);
        
        $headers = [
            "Authorization: Bearer " . $this->token,
            "X-User-Id: " . $this->userId,
            "Content-Type: application/json"
        ];
        
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        
        if ($data !== null) {
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        }
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        return [
            'code' => $httpCode,
            'data' => json_decode($response, true)
        ];
    }
    
    public function login($username, $password) {
        $response = $this->request('POST', '/api/auth/login', [
            'username' => $username,
            'password' => $password
        ]);
        
        if ($response['code'] == 200) {
            $this->token = $response['data']['token'];
            $this->userId = $response['data']['user']['id'];
            return $response['data'];
        }
        
        return null;
    }
    
    public function getProjects() {
        return $this->request('GET', '/api/projects');
    }
    
    public function createConnection($name, $dbType, $dbConfig) {
        return $this->request('POST', '/api/connections', [
            'name' => $name,
            'db_type' => $dbType,
            'db_config' => $dbConfig
        ]);
    }
    
    public function runComparison($projectId, $keyMappings = []) {
        return $this->request('POST', "/api/comparisons/project/$projectId", [
            'key_mappings' => $keyMappings
        ]);
    }
    
    public function getComparisonResults($comparisonId) {
        return $this->request('GET', "/api/comparisons/$comparisonId/results");
    }
    
    public function getDashboardStats($projectId, $startDate = null, $endDate = null) {
        $endpoint = "/api/dashboard/project/$projectId/stats";
        if ($startDate || $endDate) {
            $params = [];
            if ($startDate) $params[] = "start_date=" . urlencode($startDate);
            if ($endDate) $params[] = "end_date=" . urlencode($endDate);
            $endpoint .= "?" . implode("&", $params);
        }
        return $this->request('GET', $endpoint);
    }
}

// Uso
$client = new DeltaScopeClient('http://localhost:5000', '', '');

// Login
$loginResult = $client->login('admin', 'senha123');
if ($loginResult) {
    echo "Login realizado com sucesso!\n";
    echo "Token: " . $client->token . "\n";
    
    // Listar projetos
    $projects = $client->getProjects();
    print_r($projects);
    
    // Executar comparação
    $comparison = $client->runComparison(1, [
        'id' => 'user_id',
        'email' => 'email_address'
    ]);
    
    if ($comparison['code'] == 200) {
        $comparisonId = $comparison['data']['comparison_id'];
        
        // Obter resultados
        $results = $client->getComparisonResults($comparisonId);
        print_r($results);
    }
    
    // Obter dashboard com filtros
    $stats = $client->getDashboardStats(1, '2024-01-01T00:00:00', '2024-01-31T23:59:59');
    print_r($stats);
}
?>
```

## 🔧 Troubleshooting

### Problema: "Access denied" ao conectar no MariaDB

**Solução:**
1. Verifique se a `ENCRYPTION_KEY` está correta no `.env`
2. Recrie a conexão com a senha correta
3. Verifique se o usuário tem permissões no banco

### Problema: Modal de setup não aparece na primeira execução

**Solução:**
1. Verifique se executou `python init_db.py`
2. Verifique os logs do servidor Flask
3. Acesse diretamente `/api/setup/check` para verificar

### Problema: Erro ao gerar modelos SQLAlchemy

**Solução:**
1. Verifique se a conexão está funcionando
2. Verifique se a tabela existe no banco
3. Verifique permissões de escrita na pasta `app/models/generated/`

### Problema: Token inválido ou expirado

**Solução:**
1. Faça logout e login novamente
2. Verifique se o token está sendo enviado no header `Authorization`
3. Verifique se o header `X-User-Id` está presente

### Problema: Erro ao deletar usuário

**Solução:**
1. Verifique se o usuário não é admin tentando deletar a si mesmo
2. Verifique se há projetos associados ao usuário
3. Verifique os logs do servidor para mais detalhes

### Problema: Alterações em tabelas não são salvas

**Solução:**
1. Verifique os logs do servidor para erros de SQL
2. Para SQLite, verifique permissões de escrita no arquivo do banco
3. Para MySQL/MariaDB, verifique se o usuário tem permissão `ALTER TABLE`
4. Verifique se o modelo está sendo gerado em `app/models/generated/`

### Problema: Dashboard não carrega gráficos

**Solução:**
1. Verifique se há dados de comparação no período selecionado
2. Verifique o console do navegador (F12) para erros JavaScript
3. Verifique se o Plotly.js está carregando corretamente
4. Verifique os logs do servidor para erros na API

## 📝 Notas Importantes

1. **Senhas de Banco de Dados:** São criptografadas usando Fernet antes de serem salvas. Se perder a `ENCRYPTION_KEY`, não será possível recuperar as senhas.

2. **Modelos SQLAlchemy Gerados:** São salvos em `app/models/generated/` e não são versionados no Git (adicionados ao `.gitignore`).

3. **Primeira Execução:** O sistema verifica automaticamente se é a primeira execução e solicita criação do primeiro admin.

4. **Sistema de Permissões Granulares:**
   - Cada funcionalidade possui duas permissões: **Criar** e **Executar**
   - **Criar**: Permite criar novos recursos (projetos, conexões, etc.)
   - **Executar**: Permite visualizar e usar recursos criados por outros usuários
   - **Compartilhamento Automático**: Recursos criados por usuários com permissão de criar são automaticamente visíveis para todos os usuários com permissão de executar
   - **Administradores**: Têm todas as permissões automaticamente e podem ver todos os recursos, independente de quem os criou

5. **Sessões:** O sistema usa sessões Flask para autenticação em páginas HTML. APIs usam tokens Bearer.

6. **Edição de Tabelas:** 
   - SQLite requer recriação da tabela (única limitação)
   - MySQL/MariaDB suporta `ALTER TABLE` diretamente
   - Modelos são sempre atualizados após alterações

7. **Filtros por URL:** 
   - Dashboard suporta `project_id`, `start_date` e `end_date`
   - Tabelas suporta `connection_id`
   - Relatórios suporta `project_id`
   - URLs podem ser compartilhadas e bookmarkadas

8. **Passos para Iniciar um Projeto Novo:**
   - **Passo 1**: Criar conexões de banco de dados (origem e destino)
   - **Passo 2**: Criar um projeto de comparação selecionando as tabelas origem e destino
   - **Passo 3**: Executar comparação mapeando as chaves primárias
   - **Passo 4**: Visualizar resultados e exportar se necessário
   - **Passo 5** (Opcional): Configurar agendamento automático para comparações periódicas
   - **Passo 6** (Opcional): Configurar webhooks para notificações automáticas

9. **Dicas da Interface Web:**
   - Use o botão de tema claro/escuro no canto superior direito para alternar entre temas
   - Modais são centralizados automaticamente - não é necessário ajustar manualmente
   - Notificações aparecem no canto da tela como toasts não bloqueantes
   - Use filtros por URL para compartilhar visualizações específicas (dashboard, relatórios, etc.)
   - Administradores veem todos os recursos criados por qualquer usuário
   - Usuários regulares veem apenas recursos criados por usuários com permissão de executar

## 📄 Licença

Este projeto é de uso interno. Todos os direitos reservados.

## 🤝 Suporte

Para problemas ou dúvidas, consulte os logs do servidor Flask ou verifique o console do navegador (F12) para erros JavaScript.

---

**Última atualização:** 2024
