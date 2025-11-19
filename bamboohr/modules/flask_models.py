#Imports Flask
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

from dotenv import load_dotenv
from pathlib import Path

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

app = Flask('write_app')
#Configuração do Banco de dados
#basedir = os.path.abspath(os.path.dirname(__file__))
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')

#Base remota
# Access environment variables
username = os.environ.get('db_username')
password = os.environ.get('db_password')
host = os.environ.get('db_host')
#dbname = os.environ.get('db_dbname')
dbname = 'DeltaScope'


app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@{host}/{dbname}'
#app.config['SQLALCHEMY_BINDS'] = {
#    "dbusers" : f'mysql+pymysql://{username}:{password}@{host}/{dbusers}',
#    "dbms" : f'mysql+pymysql://{username}:{password}@{host}/{dbms}'
#}

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 1200
}

db = SQLAlchemy(app)
migrate = Migrate(app, db)
