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
- ✅ Permissões granulares:
  - Criar conexões de banco
  - Criar projetos
  - Visualizar dashboards
  - Editar tabelas
  - Visualizar tabelas
  - Visualizar relatórios
  - Baixar relatórios
- ✅ Associação de usuários a grupos
- ✅ Usuários admin têm todas as permissões automaticamente

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
- ✅ Exportação de dados

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
- Criar grupos de permissões padrão:
  - Administradores
  - Criadores de Conexões
  - Criadores de Projetos
  - Visualizadores de Dashboard
  - Editores de Tabelas
  - Visualizadores de Tabelas
  - Visualizadores de Relatórios

### 2. Criar o Primeiro Usuário Administrador

**Opção A: Via Interface Web (Recomendado)**

1. Inicie o servidor Flask:
```bash
python run.py
```

2. Acesse `http://localhost:5000`
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

```bash
python run.py
```

O servidor estará disponível em `http://localhost:5000`

## 📜 Scripts Disponíveis

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
Armazena grupos de permissões.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | Integer | Chave primária |
| name | String(100) | Nome do grupo (único) |
| description | String(500) | Descrição do grupo |
| can_create_connections | Boolean | Pode criar conexões |
| can_create_projects | Boolean | Pode criar projetos |
| can_view_dashboards | Boolean | Pode ver dashboards |
| can_edit_tables | Boolean | Pode editar tabelas |
| can_view_tables | Boolean | Pode ver tabelas |
| can_view_reports | Boolean | Pode ver relatórios |
| can_download_reports | Boolean | Pode baixar relatórios |
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
- `/comparacao/<id>/execution` - Execução de comparação
- `/relatorios` - Visualização de relatórios
- `/relatorios/<id>/resultados` - Resultados detalhados de comparação
- `/dashboard` - Dashboard com gráficos e estatísticas
- `/tabelas` - Visualização de tabelas
- `/tabelas/<connection_id>/edit/<table_name>` - Edição de colunas de tabela

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
Listar projetos do usuário.

#### `POST /api/projects`
Criar novo projeto.

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

#### `POST /api/comparisons/project/<project_id>/send-changes`
Enviar mudanças para API externa.

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

**Resultados de Comparação:**
```
/relatorios/<comparison_id>/resultados
```

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

4. **Permissões:** Usuários admin têm todas as permissões automaticamente. Outros usuários precisam estar em grupos com as permissões apropriadas.

5. **Sessões:** O sistema usa sessões Flask para autenticação em páginas HTML. APIs usam tokens Bearer.

6. **Edição de Tabelas:** 
   - SQLite requer recriação da tabela (única limitação)
   - MySQL/MariaDB suporta `ALTER TABLE` diretamente
   - Modelos são sempre atualizados após alterações

7. **Filtros por URL:** 
   - Dashboard suporta `project_id`, `start_date` e `end_date`
   - Tabelas suporta `connection_id`
   - URLs podem ser compartilhadas e bookmarkadas

## 📄 Licença

Este projeto é de uso interno. Todos os direitos reservados.

## 🤝 Suporte

Para problemas ou dúvidas, consulte os logs do servidor Flask ou verifique o console do navegador (F12) para erros JavaScript.

---

**Última atualização:** 2024
