# Pasta BambooHR - Estrutura Independente

## 📋 Visão Geral

A pasta `bamboohr/` é **completamente independente** do projeto principal (pyDeltaScope). Ela possui sua própria estrutura Flask, modelos SQLAlchemy e configurações, funcionando como um módulo autônomo.

## 🏗️ Estrutura

```
bamboohr/
├── modules/
│   ├── flask_models.py      # App Flask e configuração do banco de dados
│   ├── db_models.py         # Modelos SQLAlchemy (InsertLog)
│   ├── logger_config.py     # Configuração de logging
│   ├── bamboohr.py          # Cliente API BambooHR
│   └── *_model.py           # Modelos gerados dinamicamente
├── get_reports.py           # Script original (usa pandas)
├── get_reports_v2.py        # Script melhorado (usa SQLAlchemy ORM)
├── sync_report_dynamic.py   # Script para gerar modelos dinamicamente
└── README.md                # Este arquivo
```

## 🔧 Características de Independência

### ✅ Estrutura Flask Própria
- App Flask independente (`flask_models.py`)
- Instância SQLAlchemy própria (`db`)
- Configurações de banco de dados próprias

### ✅ Caminhos Relativos
- Todos os caminhos são relativos à pasta `bamboohr/`
- Procura `.env` primeiro em `bamboohr/.env`, depois na raiz do projeto
- Não depende de estrutura do projeto principal

### ✅ Imports Locais
- Todos os imports são relativos à pasta `bamboohr/`
- Usa apenas `modules.*` para imports internos
- Não importa nada do projeto raiz

## 📝 Configuração

### Variáveis de Ambiente

A pasta `bamboohr/` procura variáveis de ambiente na seguinte ordem:

1. **`bamboohr/.env`** (prioridade)
2. **`.env` na raiz do projeto** (fallback)
3. **Variáveis de ambiente do sistema**

### Variáveis Necessárias

```env
# Banco de dados
db_username=seu_usuario
db_password=sua_senha
db_host=localhost

# BambooHR API
BAMBOOHR_KEY=sua_chave_api
```

## 🚀 Como Usar

### 1. Gerar Modelo Dinamicamente

```bash
cd bamboohr
python3 sync_report_dynamic.py <report_id> <table_name> <mode>
```

Exemplo:
```bash
python3 sync_report_dynamic.py 184 report_all_users replace
```

### 2. Sincronizar Dados

```bash
cd bamboohr
python3 get_reports_v2.py
```

## 📦 Dependências

A pasta `bamboohr/` requer apenas:

- Python 3.7+
- Flask
- Flask-SQLAlchemy
- Flask-Migrate (opcional)
- requests
- python-dotenv
- pandas (apenas para `get_reports.py`)

**Não requer nenhuma dependência do projeto principal.**

## 🔄 Fluxo de Trabalho

1. **Gerar Modelo**: Execute `sync_report_dynamic.py` para criar/atualizar o modelo SQLAlchemy
2. **Sincronizar Dados**: Execute `get_reports_v2.py` para buscar e armazenar dados do BambooHR
3. **Modelos Gerados**: Os modelos são salvos em `modules/*_model.py`

## 📌 Notas Importantes

- ✅ A pasta `bamboohr/` pode ser movida para outro projeto sem modificações
- ✅ Não há dependências do projeto principal
- ✅ Todos os caminhos são relativos à pasta `bamboohr/`
- ✅ Configurações são independentes
- ✅ Pode ter seu próprio `.env` na pasta `bamboohr/`

## 🛠️ Manutenção

Para manter a independência:

1. **Nunca importe** módulos do projeto raiz
2. **Use apenas** imports relativos à pasta `bamboohr/`
3. **Mantenha** a estrutura de pastas `modules/`
4. **Use** caminhos relativos com `Path(__file__).parent`

## 📚 Scripts Disponíveis

### `sync_report_dynamic.py`
Gera modelos SQLAlchemy dinamicamente baseados nos dados do BambooHR.

### `get_reports_v2.py`
Sincroniza dados do BambooHR usando modelos SQLAlchemy gerados.

### `get_reports.py`
Script original que usa pandas (mantido para compatibilidade).

