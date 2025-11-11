# DeltaScope - Sistema de Comparação de Tabelas

Sistema completo para comparação de tabelas entre bancos de dados, com geração automática de modelos SQLAlchemy, dashboards dinâmicos e gerenciamento de usuários e permissões.

## 📋 Índice

- [Funcionalidades](#funcionalidades)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Inicialização](#inicialização)
- [Scripts Disponíveis](#scripts-disponíveis)
- [Estrutura do Banco de Dados](#estrutura-do-banco-de-dados)
- [API Endpoints](#api-endpoints)
- [Sistema de Modais](#sistema-de-modais)
- [Gerenciamento de Usuários](#gerenciamento-de-usuários)
- [Gerenciamento de Grupos](#gerenciamento-de-grupos)
- [Exemplos de Código](#exemplos-de-código)
- [Troubleshooting](#troubleshooting)

## ✨ Funcionalidades

- ✅ Autenticação de usuários com Werkzeug
- ✅ Sistema de grupos e permissões
- ✅ CRUD completo de projetos e conexões de banco de dados
- ✅ Seleção visual de tabelas antes de criar projeto
- ✅ Teste de conexão com bancos de dados
- ✅ Comparação automática entre tabelas (origem e destino)
- ✅ Geração automática de modelos SQLAlchemy baseados nas tabelas
- ✅ Criptografia de senhas de banco de dados (Fernet)
- ✅ Registro incremental de mudanças
- ✅ Envio de mudanças via API usando requests
- ✅ Dashboards dinâmicos com Plotly.js
- ✅ Suporte para MariaDB (produção) e SQLite (desenvolvimento)
- ✅ Interface moderna e responsiva
- ✅ Modais de notificação personalizados
- ✅ Verificação automática de tabelas na inicialização
- ✅ Setup inicial para criação do primeiro admin

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
│   │       └── __init__.py
│   ├── routes/                      # Rotas da API
│   │   ├── __init__.py
│   │   ├── auth.py                  # Autenticação (login, registro, logout)
│   │   ├── users.py                 # Gerenciamento de usuários (Admin)
│   │   ├── groups.py                # Gerenciamento de grupos (Admin)
│   │   ├── projects.py              # CRUD de projetos
│   │   ├── connections.py            # CRUD de conexões de banco
│   │   ├── comparisons.py           # Execução de comparações
│   │   ├── dashboard.py              # Dashboards e estatísticas
│   │   ├── tables.py                 # Operações com tabelas
│   │   └── setup.py                 # Setup inicial
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
│           └── app.js                # JavaScript da aplicação
├── templates/                       # Templates HTML
│   └── index.html                   # Template principal (SPA)
├── docs/                            # Documentação
│   └── QUICKSTART.md                # Guia rápido
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
- Criar grupos de permissões padrão
- Verificar se existe algum usuário admin

### 2. Criar o Primeiro Usuário Administrador

**Opção A: Via Interface Web (Recomendado)**

1. Inicie o servidor Flask:
```bash
python run.py
```

2. Acesse `http://localhost:5000`
3. O sistema detectará que é a primeira execução e mostrará um modal para criar o primeiro admin
4. Preencha os dados e crie o usuário

**Opção B: Via Script Interativo**

```bash
python create_admin.py
```

O script irá solicitar:
- Usuário
- Email
- Senha (com confirmação)

**Opção C: Via Script CLI (Não Interativo)**

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
- Cria grupos de permissões padrão:
  - Administradores
  - Criadores de Conexões
  - Criadores de Projetos
  - Visualizadores de Dashboard
  - Editores de Tabelas
  - Visualizadores de Tabelas
  - Visualizadores de Relatórios

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
| user_id | Integer | FK para users.id |
| created_at | DateTime | Data de criação |
| updated_at | DateTime | Data de atualização |

#### `comparisons`
Armazena execuções de comparação.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | Integer | Chave primária |
| project_id | Integer | FK para projects.id |
| executed_at | DateTime | Data de execução |
| status | String(50) | Status (completed, failed) |
| comparison_metadata | JSON | Metadados da comparação |
| user_id | Integer | FK para users.id |

#### `comparison_results`
Armazena resultados detalhados das comparações.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | Integer | Chave primária |
| comparison_id | Integer | FK para comparisons.id |
| field_name | String(200) | Nome do campo |
| source_value | Text | Valor origem |
| target_value | Text | Valor destino |
| change_type | String(50) | Tipo (added, modified, deleted) |

#### `change_logs`
Armazena logs incrementais de mudanças.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | Integer | Chave primária |
| comparison_id | Integer | FK para comparisons.id |
| field_name | String(200) | Nome do campo |
| old_value | Text | Valor antigo |
| new_value | Text | Valor novo |
| changed_at | DateTime | Data da mudança |

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

**Constraint único:** `(connection_id, table_name)`

## 🔌 API Endpoints

### Autenticação

#### `POST /api/auth/register`
Registrar novo usuário.

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
      "is_active": true
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
  "is_admin": false
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
  "is_active": true
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

**Request:**
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

**Para SQLite:**
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
Deletar conexão.

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
Deletar projeto.

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
- `start_date` (opcional): Data inicial (YYYY-MM-DD)
- `end_date` (opcional): Data final (YYYY-MM-DD)

**Response:**
```json
{
  "total_comparisons": 10,
  "total_changes": 150,
  "modified_fields_count": 25,
  "last_comparison": "2024-01-15T10:30:00"
}
```

#### `GET /api/dashboard/project/<project_id>/changes-over-time`
Obter mudanças ao longo do tempo.

**Query Parameters:**
- `start_date` (opcional)
- `end_date` (opcional)

#### `GET /api/dashboard/project/<project_id>/field-changes`
Obter mudanças por campo (para gráfico de pizza).

### Tabelas

#### `POST /api/tables/test-connection`
Testar conexão com banco de dados.

#### `POST /api/tables/list`
Listar tabelas de um banco.

#### `POST /api/tables/columns`
Obter colunas de uma tabela.

#### `POST /api/tables/update-column-type`
Atualizar tipo de coluna.

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

#### `POST /api/tables/update-primary-keys`
Atualizar chaves primárias de uma tabela.

#### `GET /api/tables/model/<connection_id>/<table_name>`
Obter código do modelo SQLAlchemy gerado.

#### `GET /api/tables/data-types`
Listar tipos de dados disponíveis.

## 🎨 Sistema de Modais

O sistema utiliza modais Bootstrap 5 personalizados para notificações e confirmações.

### Tipos de Modal

#### Modal de Notificação (`notificationModal`)

Exibe mensagens de sucesso, erro, aviso ou informação.

**Funções JavaScript:**
```javascript
showSuccess('Operação realizada com sucesso!');
showError('Erro ao processar requisição');
showWarning('Atenção: Esta ação não pode ser desfeita');
showInfo('Informação importante');
```

**Cores:**
- ✅ Sucesso: Verde (`#198754`)
- ❌ Erro: Vermelho (`#dc3545`)
- ⚠️ Aviso: Amarelo (`#ffc107`)
- ℹ️ Info: Azul (`#0dcaf0`)

#### Modal de Confirmação (`confirmationModal`)

Solicita confirmação do usuário antes de executar uma ação.

**Função JavaScript:**
```javascript
const confirmed = await showConfirmation('Confirmação', 'Deseja realmente deletar este item?');
if (confirmed) {
    // Executar ação
}
```

**Retorna:** `Promise<boolean>`
- `true` se confirmado
- `false` se cancelado

#### Modal de Loading (`loadingModal`)

Exibe durante operações assíncronas.

**Função JavaScript:**
```javascript
// Mostrar loading
const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
loadingModal.show();

// Ocultar loading
loadingModal.hide();
```

### Estrutura HTML dos Modais

Todos os modais estão definidos em `templates/index.html`:

- `#notificationModal` - Notificações
- `#confirmationModal` - Confirmações
- `#loadingModal` - Loading
- `#setupModal` - Setup inicial
- `#createConnectionModal` - Criar conexão
- `#editConnectionModal` - Editar conexão
- `#createProjectModal` - Criar projeto
- `#editProjectModal` - Editar projeto
- `#columnTypeModal` - Editar tipo de coluna
- `#tableDetailsModal` - Detalhes da tabela
- `#groupUsersModal` - Usuários do grupo
- `#addUserToGroupModal` - Adicionar usuário ao grupo

## 👥 Gerenciamento de Usuários

### Criar Usuário

**Via Interface Web:**
1. Faça login como administrador
2. Acesse "Usuários" no menu
3. Clique em "Novo Usuário"
4. Preencha os dados
5. Clique em "Criar"

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
    "is_admin": false
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
    "is_admin": False
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### Deletar Usuário

**Via Interface Web:**
1. Acesse "Usuários"
2. Clique no botão de deletar do usuário
3. Confirme a ação

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

**Via API:**
```bash
curl -X PUT http://localhost:5000/api/users/2/toggle-active \
  -H "Authorization: Bearer {token}" \
  -H "X-User-Id: {user_id}"
```

### Trocar Senha

**Via Interface Web:**
1. Acesse "Usuários"
2. Clique em "Alterar Senha"
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

#### Obter Resultados de Comparação

```python
import requests

token = "seu_token_aqui"
user_id = 1
comparison_id = 1

url = f"http://localhost:5000/api/comparisons/{comparison_id}/results"
headers = {
    "Authorization": f"Bearer {token}",
    "X-User-Id": str(user_id)
}

response = requests.get(url, headers=headers)
results = response.json()

print("Total de registros:", results['stats']['total_records'])
print("Adicionados:", results['stats']['added'])
print("Modificados:", results['stats']['modified'])
print("Deletados:", results['stats']['deleted'])

# Listar diferenças
for diff in results['differences']:
    print(f"Campo: {diff['field_name']}")
    print(f"  Origem: {diff['source_value']}")
    print(f"  Destino: {diff['target_value']}")
    print(f"  Tipo: {diff['change_type']}")
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
    "is_admin": false
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

#### Obter Dashboard

```bash
TOKEN="seu_token_aqui"
USER_ID=1
PROJECT_ID=1

curl -X GET "http://localhost:5000/api/dashboard/project/$PROJECT_ID/stats?start_date=2024-01-01&end_date=2024-01-31" \
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
}
?>
```

#### Exemplo Simples

```php
<?php

// Login
$ch = curl_init('http://localhost:5000/api/auth/login');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    'username' => 'admin',
    'password' => 'senha123'
]));
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);

$response = curl_exec($ch);
$data = json_decode($response, true);
curl_close($ch);

if (isset($data['token'])) {
    $token = $data['token'];
    $userId = $data['user']['id'];
    
    // Listar projetos
    $ch = curl_init('http://localhost:5000/api/projects');
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        "Authorization: Bearer $token",
        "X-User-Id: $userId"
    ]);
    
    $projects = json_decode(curl_exec($ch), true);
    curl_close($ch);
    
    print_r($projects);
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

## 📝 Notas Importantes

1. **Senhas de Banco de Dados:** São criptografadas usando Fernet antes de serem salvas. Se perder a `ENCRYPTION_KEY`, não será possível recuperar as senhas.

2. **Modelos SQLAlchemy Gerados:** São salvos em `app/models/generated/` e não são versionados no Git (adicionados ao `.gitignore`).

3. **Primeira Execução:** O sistema verifica automaticamente se é a primeira execução e solicita criação do primeiro admin.

4. **Permissões:** Usuários admin têm todas as permissões automaticamente. Outros usuários precisam estar em grupos com as permissões apropriadas.

5. **Sessões:** O sistema usa sessões Flask para autenticação. Tokens são gerados usando `secrets.token_urlsafe()`.

## 📄 Licença

Este projeto é de uso interno. Todos os direitos reservados.

## 🤝 Suporte

Para problemas ou dúvidas, consulte os logs do servidor Flask ou verifique o console do navegador (F12) para erros JavaScript.

---

**Última atualização:** 2024
