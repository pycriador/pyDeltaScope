import requests
import pandas as pd
from .logger_config import logger
import time

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Procura o .env na pasta bamboohr primeiro, depois na raiz do projeto
bamboohr_dir = Path(__file__).parent.parent
env_path_bamboohr = bamboohr_dir / '.env'
env_path_root = bamboohr_dir.parent / '.env'

# Tenta carregar do .env da pasta bamboohr primeiro, depois da raiz
if env_path_bamboohr.exists():
    load_dotenv(dotenv_path=env_path_bamboohr)
elif env_path_root.exists():
    load_dotenv(dotenv_path=env_path_root)
else:
    # Se não encontrar, tenta carregar do diretório atual
    load_dotenv()

api_key = os.environ.get('BAMBOOHR_KEY')
subdomain = "loft"

# Função para obter todos os campos de um funcionário
def get_employee_details(employee_id=None, filter=None):
    BASE_URL = f"https://{subdomain}.bamboohr.com/api/gateway.php/{subdomain}/v1"

    auth = (api_key, "x")
    headers = {"accept": "application/json"}
    #headers = {}
    url = f"{BASE_URL}/employees/{employee_id}"
    params = {"fields": filter}
    response = requests.get(url, auth=auth, params=params, headers=headers)

    #print(response.text)
    response.raise_for_status()
    #time.sleep(3)
    return response.json()


def get_available_fields():

    url = f"https://api.bamboohr.com/api/gateway.php/{subdomain}/v1/meta/fields"

    auth = (api_key, "x")
    headers = {"accept": "application/json"}
    response = requests.get(url, auth=auth, headers=headers)
    response.raise_for_status()  # Levanta erros de HTTP
    return response.json()

def get_employees(filter=None):
    BASE_URL = f"https://api.bamboohr.com/api/gateway.php/{subdomain}/v1"

    auth = (api_key, "x")
    headers = {"accept": "application/json"}
    url = f"{BASE_URL}/employees/directory"
    params = {"fields": filter}
    response = requests.get(url, auth=auth, headers=headers, params=params)

    #response = requests.Request("GET", url, params=params, auth=auth, headers=headers)
    #prepared = response.prepare()
    #print(prepared.url)

    response.raise_for_status()  # Levanta erros de HTTP
    return response.json()["employees"]

def bamboorh_get_all_users():

    url = f"https://api.bamboohr.com/api/gateway.php/{subdomain}/v1/employees/directory"

    #Autenticação básica
    auth = (api_key, "x")
    headers = {
        "accept": "application/json"
    }
    params = {"fields": 'id,employeeNumber,status,employmentStatus,displayName,firstName,lastName,customCPF,customRG,address1,address2,city,preferredName,jobTitle,workPhone,mobilePhone,workEmail,department,location,division,pronouns,workPhoneExtension,supervisor,hiredate'}
    
    try:
        # Fazendo a requisição GET
        response = requests.get(url, auth=auth, headers=headers, params=params)
        
        # Verifica o status da resposta
        if response.status_code == 200:
            #return response.json()
            result = response.json().get('employees')
            return pd.DataFrame.from_dict(result)
        else:
            logger.error(f"Erro: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Ocorreu um erro: {e}")


def bamboorh_get_table_info(table=None):
    url = f'https://api.bamboohr.com/api/gateway.php/{subdomain}/v1/employees/changed/tables/{table}'
        #Autenticação básica
    auth = (api_key, "x")
    headers = {
        "accept": "application/json"
    }

    try:
        # Fazendo a requisição GET
        response = requests.get(url, auth=auth, headers=headers)
        
        # Verifica o status da resposta
        if response.status_code == 200:
            return response.json()
            #result = response.json().get('employees')
            #return pd.DataFrame.from_dict(result)
        else:
            logger.error(f"Erro: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Ocorreu um erro: {e}") 

def bamboorh_get_user_table_info(table=None, userid=None):

    url = f'https://api.bamboohr.com/api/gateway.php/{subdomain}/v1/employees/{userid}/tables/{table}'
    #Autenticação básica
    auth = (api_key, "x")
    headers = {
        "accept": "application/json"
    }

    try:
        # Fazendo a requisição GET
        response = requests.get(url, auth=auth, headers=headers)
        
        # Verifica o status da resposta
        if response.status_code == 200:
            return response.json()
            #result = response.json().get('employees')
            #return pd.DataFrame.from_dict(result)
        else:
            logger.error(f"Erro: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Ocorreu um erro: {e}") 

def bamboohr_list_reports():
    url = f'https://api.bamboohr.com/api/gateway.php/{subdomain}/v1/custom-reports/'
    
    auth = (api_key, "x")
    headers = {
        "accept": "application/json"
    }

    try:
        # Fazendo a requisição GET
        response = requests.get(url, auth=auth, headers=headers)
        
        # Verifica o status da resposta
        if response.status_code == 200:
            return response.json()
            #result = response.json().get('employees')
            #return pd.DataFrame.from_dict(result)
        else:
            logger.error(f"Erro: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Ocorreu um erro: {e}") 


def bamboohr_get_report_by_name(report_name=None):

    url = f'https://api.bamboohr.com/api/gateway.php/{subdomain}/v1/reports?name={report_name}'
    
    auth = (api_key, "x")
    headers = {
    }

    try:
        # Fazendo a requisição GET
        response = requests.get(url, auth=auth, headers=headers)
        
        # Verifica o status da resposta
        if response.status_code == 200:
            return response.json()
            #result = response.json().get('employees')
            #return pd.DataFrame.from_dict(result)
        else:
            logger.error(f"Erro: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Ocorreu um erro: {e}") 

def bamboohr_get_report(report_id=None):
    url = f'https://api.bamboohr.com/api/gateway.php/{subdomain}/v1/reports/{report_id}?format=json&onlyCurrent=true'
    
    auth = (api_key, "x")
    headers = {
    }

    try:
        # Fazendo a requisição GET
        response = requests.get(url, auth=auth, headers=headers)
        
        # Verifica o status da resposta
        if response.status_code == 200:
            return response.json()
            #result = response.json().get('employees')
            #return pd.DataFrame.from_dict(result)
        else:
            logger.error(f"Erro: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Ocorreu um erro: {e}") 

#Emprego ou Job - Job Information - Reports to (Infomração do líder)
#Informação do trabalho - 
#Afastamentos e férias ficam em TimeOff - Afastamentos - Tabela Histórico