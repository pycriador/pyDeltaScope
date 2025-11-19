# DeltaScope - Guia Completo de API: Comparações e Webhooks

Este documento fornece exemplos detalhados de como executar comparações via API e enviar webhooks via API no DeltaScope.

## 📋 Índice

- [Autenticação](#autenticação)
- [Executar Comparações via API](#executar-comparações-via-api)
- [Obter Resultados de Comparação](#obter-resultados-de-comparação)
- [Enviar Webhooks via API](#enviar-webhooks-via-api)
- [Processar Templates de Payload](#processar-templates-de-payload)
- [Exemplos Completos](#exemplos-completos)

## 🔐 Autenticação

Antes de usar qualquer endpoint da API, você precisa fazer login e obter um token de autenticação.

### Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "seu_usuario",
    "password": "sua_senha"
  }'
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "seu_usuario",
    "email": "usuario@exemplo.com",
    "is_admin": false,
    "is_active": true
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Guarde o `token` e o `user.id` para usar nos próximos requests.

## 🔄 Executar Comparações via API

### Endpoint: `POST /api/comparisons/project/<project_id>`

Executa uma comparação entre as tabelas origem e destino de um projeto.

#### Headers Obrigatórios

```
Authorization: Bearer {token}
X-User-Id: {user_id}
Content-Type: application/json
```

#### Request Body

```json
{
  "key_mappings": {
    "id": "user_id",
    "email": "email_address"
  },
  "ignored_columns": ["created_at", "updated_at"]
}
```

**Parâmetros:**
- `key_mappings` (obrigatório): Mapeamento de colunas origem -> destino para chaves primárias
- `ignored_columns` (opcional): Lista de colunas a ignorar durante a comparação

#### Exemplo Completo com cURL

```bash
TOKEN="seu_token_aqui"
USER_ID=1
PROJECT_ID=1

curl -X POST "http://localhost:5000/api/comparisons/project/$PROJECT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "key_mappings": {
      "id": "user_id",
      "email": "email_address"
    },
    "ignored_columns": ["created_at", "updated_at"]
  }'
```

#### Exemplo Completo com Python

```python
import requests

# Configuração
BASE_URL = "http://localhost:5000"
TOKEN = "seu_token_aqui"
USER_ID = 1
PROJECT_ID = 1

# Headers
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-User-Id": str(USER_ID),
    "Content-Type": "application/json"
}

# Dados da comparação
data = {
    "key_mappings": {
        "id": "user_id",
        "email": "email_address"
    },
    "ignored_columns": ["created_at", "updated_at"]
}

# Executar comparação
url = f"{BASE_URL}/api/comparisons/project/{PROJECT_ID}"
response = requests.post(url, json=data, headers=headers)

if response.status_code == 200:
    result = response.json()
    print(f"Comparação ID: {result['comparison']['id']}")
    print(f"Total de diferenças: {result['total_differences']}")
    print(f"Status: {result['comparison']['status']}")
else:
    print(f"Erro: {response.status_code}")
    print(response.json())
```

#### Response (200 OK)

```json
{
  "message": "Comparison completed",
  "comparison": {
    "id": 5,
    "project_id": 1,
    "executed_at": "2024-01-15T10:30:00",
    "status": "completed",
    "total_differences": 10
  },
  "total_differences": 10
}
```

## 📊 Obter Resultados de Comparação

### Endpoint: `GET /api/comparisons/<comparison_id>/results`

Obtém todos os resultados detalhados de uma comparação executada.

#### Exemplo com cURL

```bash
TOKEN="seu_token_aqui"
USER_ID=1
COMPARISON_ID=5

curl -X GET "http://localhost:5000/api/comparisons/$COMPARISON_ID/results" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID"
```

#### Exemplo com Python

```python
import requests

BASE_URL = "http://localhost:5000"
TOKEN = "seu_token_aqui"
USER_ID = 1
COMPARISON_ID = 5

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-User-Id": str(USER_ID)
}

url = f"{BASE_URL}/api/comparisons/{COMPARISON_ID}/results"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    result = response.json()
    print(f"Comparação ID: {result['comparison_id']}")
    print(f"Total de diferenças: {len(result['results'])}")
    
    # Processar cada diferença
    for diff in result['results']:
        print(f"\nCampo: {diff['field_name']}")
        print(f"  Origem: {diff['source_value']}")
        print(f"  Destino: {diff['target_value']}")
        print(f"  Tipo: {diff['change_type']}")
        print(f"  Record ID: {diff['record_id']}")
        
        # Acessar dados completos do registro destino (json_raw)
        if diff.get('target_record_json'):
            print(f"  Dados completos do destino: {diff['target_record_json']}")
else:
    print(f"Erro: {response.status_code}")
    print(response.json())
```

#### Response (200 OK)

```json
{
  "comparison_id": 5,
  "stats": {
    "total_records": 100,
    "added": 5,
    "modified": 10,
    "deleted": 2
  },
  "results": [
    {
      "id": 1,
      "comparison_id": 5,
      "record_id": "usuario@exemplo.com",
      "field_name": "nome",
      "source_value": "João Silva",
      "target_value": "João da Silva",
      "target_record_json": {
        "id": 123,
        "email": "usuario@exemplo.com",
        "nome": "João da Silva",
        "ativo": true
      },
      "change_type": "modified",
      "detected_at": "2024-01-15T10:30:00"
    }
  ]
}
```

## 📤 Enviar Webhooks via API

### Endpoint: `POST /api/webhooks/send`

Envia uma requisição HTTP manualmente através do cliente HTTP integrado.

#### Exemplo Básico com cURL

```bash
TOKEN="seu_token_aqui"
USER_ID=1

curl -X POST "http://localhost:5000/api/webhooks/send" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: $USER_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://api.exemplo.com/webhook",
    "method": "POST",
    "headers": {
      "Content-Type": "application/json",
      "Authorization": "Bearer token123"
    },
    "payload": {
      "event": "test",
      "data": "valor_teste"
    }
  }'
```

#### Exemplo com Python

```python
import requests

BASE_URL = "http://localhost:5000"
TOKEN = "seu_token_aqui"
USER_ID = 1

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-User-Id": str(USER_ID),
    "Content-Type": "application/json"
}

data = {
    "url": "https://api.exemplo.com/webhook",
    "method": "POST",
    "headers": {
        "Content-Type": "application/json",
        "Authorization": "Bearer token123"
    },
    "payload": {
        "event": "test",
        "data": "valor_teste"
    }
}

url = f"{BASE_URL}/api/webhooks/send"
response = requests.post(url, json=data, headers=headers)

if response.status_code == 200:
    result = response.json()
    print(f"Status Code: {result['status_code']}")
    print(f"Response: {result['response']}")
else:
    print(f"Erro: {response.status_code}")
    print(response.json())
```

#### Response (200 OK)

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

## 🔧 Processar Templates de Payload

### Endpoint: `POST /api/webhooks/process-template`

Processa um template de payload substituindo os placeholders pelos valores fornecidos.

#### Namespaces Disponíveis

- `{{comparison.id}}` - ID da comparação
- `{{comparison.project_id}}` - ID do projeto
- `{{comparison.executed_at}}` - Data/hora de execução
- `{{comparison.status}}` - Status da comparação
- `{{comparison.total_differences}}` - Total de diferenças
- `{{difference.id}}` - ID da diferença
- `{{difference.record_id}}` - ID do registro
- `{{difference.field_name}}` - Nome do campo
- `{{difference.source_value}}` - Valor origem
- `{{difference.target_value}}` - Valor destino
- `{{difference.change_type}}` - Tipo de mudança
- `{{json_raw.campo}}` - Acessa qualquer campo do registro destino completo
- `{{project.id}}` - ID do projeto
- `{{project.name}}` - Nome do projeto

#### Exemplo com Template

```python
import requests

BASE_URL = "http://localhost:5000"
TOKEN = "seu_token_aqui"
USER_ID = 1

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-User-Id": str(USER_ID),
    "Content-Type": "application/json"
}

# Template com placeholders
template = """{
  "leader": {{json_raw.reportsto}},
  "cost_center": {{json_raw.customcostcenter}},
  "action": "update",
  "leader_email": {{json_raw.supervisoremail}},
  "employee_email": {{json_raw.workemail}}
}"""

# Dados para substituir os placeholders
data = {
    "template": template,
    "comparison": {
        "id": 5,
        "project_id": 1,
        "executed_at": "2024-01-15T10:30:00",
        "status": "completed",
        "total_differences": 10
    },
    "difference": {
        "id": 1,
        "record_id": "usuario@exemplo.com",
        "field_name": "customcostcenter",
        "source_value": "420",
        "target_value": "999",
        "change_type": "modified"
    },
    "json_raw": {
        "id": 123,
        "reportsto": "João Silva (1234)",
        "customcostcenter": 999,
        "supervisoremail": "joao.silva@exemplo.com",
        "workemail": "usuario@exemplo.com"
    }
}

url = f"{BASE_URL}/api/webhooks/process-template"
response = requests.post(url, json=data, headers=headers)

if response.status_code == 200:
    result = response.json()
    print("Template processado:")
    print(result['processed'])
else:
    print(f"Erro: {response.status_code}")
    print(response.json())
```

#### Response (200 OK)

```json
{
  "processed": {
    "leader": "João Silva (1234)",
    "cost_center": 999,
    "action": "update",
    "leader_email": "joao.silva@exemplo.com",
    "employee_email": "usuario@exemplo.com"
  }
}
```

**Nota:** Valores de string são automaticamente envolvidos em aspas duplas. Valores numéricos não recebem aspas.

## 🎯 Exemplos Completos

### Fluxo Completo: Executar Comparação e Enviar Webhook

```python
import requests
import time

BASE_URL = "http://localhost:5000"
TOKEN = "seu_token_aqui"
USER_ID = 1
PROJECT_ID = 1

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-User-Id": str(USER_ID),
    "Content-Type": "application/json"
}

# 1. Executar comparação
print("1. Executando comparação...")
comparison_data = {
    "key_mappings": {
        "id": "user_id",
        "email": "email_address"
    },
    "ignored_columns": ["created_at", "updated_at"]
}

comparison_url = f"{BASE_URL}/api/comparisons/project/{PROJECT_ID}"
comparison_response = requests.post(comparison_url, json=comparison_data, headers=headers)

if comparison_response.status_code != 200:
    print(f"Erro ao executar comparação: {comparison_response.status_code}")
    exit(1)

comparison_result = comparison_response.json()
comparison_id = comparison_result['comparison']['id']
print(f"   Comparação ID: {comparison_id}")
print(f"   Total de diferenças: {comparison_result['total_differences']}")

# Aguardar um pouco para garantir que a comparação foi processada
time.sleep(2)

# 2. Obter resultados
print("\n2. Obtendo resultados...")
results_url = f"{BASE_URL}/api/comparisons/{comparison_id}/results"
results_response = requests.get(results_url, headers=headers)

if results_response.status_code != 200:
    print(f"Erro ao obter resultados: {results_response.status_code}")
    exit(1)

results_data = results_response.json()
print(f"   Total de resultados: {len(results_data['results'])}")

# 3. Processar cada diferença e enviar webhook
print("\n3. Enviando webhooks para cada diferença...")
webhook_url = f"{BASE_URL}/api/webhooks/send"

template = """{
  "leader": {{json_raw.reportsto}},
  "cost_center": {{json_raw.customcostcenter}},
  "action": "update",
  "leader_email": {{json_raw.supervisoremail}},
  "employee_email": {{json_raw.workemail}}
}"""

for diff in results_data['results']:
    # Processar template com os dados da diferença
    template_data = {
        "template": template,
        "comparison": {
            "id": comparison_id,
            "project_id": PROJECT_ID,
            "executed_at": comparison_result['comparison']['executed_at'],
            "status": comparison_result['comparison']['status'],
            "total_differences": comparison_result['total_differences']
        },
        "difference": diff,
        "json_raw": diff.get('target_record_json', {})
    }
    
    # Processar template
    process_url = f"{BASE_URL}/api/webhooks/process-template"
    process_response = requests.post(process_url, json=template_data, headers=headers)
    
    if process_response.status_code == 200:
        processed_payload = process_response.json()['processed']
        
        # Enviar webhook
        webhook_data = {
            "url": "https://api.exemplo.com/webhook",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": "Bearer seu_token_webhook"
            },
            "payload": processed_payload
        }
        
        webhook_response = requests.post(webhook_url, json=webhook_data, headers=headers)
        
        if webhook_response.status_code == 200:
            print(f"   ✓ Webhook enviado para {diff['field_name']} (Record ID: {diff['record_id']})")
        else:
            print(f"   ✗ Erro ao enviar webhook: {webhook_response.status_code}")
    else:
        print(f"   ✗ Erro ao processar template: {process_response.status_code}")

print("\n✓ Processo concluído!")
```

### Usar Webhook Config Salvo

Se você já tem uma configuração de webhook salva no sistema:

```python
import requests

BASE_URL = "http://localhost:5000"
TOKEN = "seu_token_aqui"
USER_ID = 1
WEBHOOK_CONFIG_ID = 1

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "X-User-Id": str(USER_ID)
}

# 1. Obter configuração do webhook
config_url = f"{BASE_URL}/api/webhooks/configs/{WEBHOOK_CONFIG_ID}"
config_response = requests.get(config_url, headers=headers)

if config_response.status_code == 200:
    config = config_response.json()
    
    # 2. Usar a configuração para enviar webhook
    webhook_data = {
        "url": config['url'],
        "method": config['method'],
        "headers": config['headers'],
        "payload": {
            "event": "test",
            "data": "valor_teste"
        }
    }
    
    send_url = f"{BASE_URL}/api/webhooks/send"
    send_response = requests.post(send_url, json=webhook_data, headers=headers)
    
    print(send_response.json())
```

## 📝 Notas Importantes

1. **Autenticação:** Sempre inclua os headers `Authorization` e `X-User-Id` em todas as requisições.

2. **Aspas Duplas:** Valores de string em templates são automaticamente envolvidos em aspas duplas. Não adicione aspas manualmente nos templates.

3. **json_raw:** Use o nome exato da coluna como aparece no banco de dados ao acessar campos via `{{json_raw.campo}}`.

4. **Rate Limiting:** Ao enviar múltiplos webhooks, considere adicionar delays entre as requisições para evitar sobrecarregar o servidor de destino.

5. **Tratamento de Erros:** Sempre verifique o `status_code` da resposta antes de processar os dados.

6. **Logs:** Os logs do servidor Flask podem ajudar a debugar problemas com comparações e webhooks.

## 🔗 Links Relacionados

- [README Principal](../README.md) - Documentação completa do projeto
- [Documentação da API HTML](../templates/api_docs.html) - Documentação interativa da API

---

**Última atualização:** 2024

