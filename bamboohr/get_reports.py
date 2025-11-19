from datetime import datetime
from datetime import timedelta
import json, os
import pandas as pd
#Imports sqlalchemy
from sqlalchemy.types import Integer, String, Date, DateTime
import sqlalchemy

#Importar módulo de log personalizado
from modules.logger_config import logger
#Importar módulo do app flask
from modules.flask_models import app
#Importar o modelo de DB
from modules.db_models import *

#Importar módulo BambooHR
from modules.bamboohr import *

import locale
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR')
    #locale.setlocale(locale.LC_ALL, 'en_US')
except Exception as e:
    logger.error("Erro ao carregar localização em Português do Brasil")

def replace_tags(text, variables):
    for tag, value in variables.items():
        tag_to_replace = f'{{{{{tag}}}}}'
        text = text.replace(tag_to_replace, str(value))
    return text


def registro_db(msg=None, app=None, name=None, email=None):
    #Registro genérico de log - Pode ser utilizado para qualquer função
    record_db = InsertLog(name=name,
                          email=email,
                          msg=msg,
                          app=app,
                          date=datetime.now())
    db.session.add(record_db)

def gravar_df(table=None, df=None, mode=None):
    app.logger.info(f"Gravar dataframe na tabela {table}")
    engine = db.engine

    #df = df.replace({np.nan: None})
    #df.fillna('', inplace=True)

    dtype = {}
    #dtype={'created_at': DateTime,
    #       'created': String,
    #       'lastContact': String
    #       }
    #df['created_at'] = datetime.now()
    #df['creator'] = 'willian.jesus@loft.com.br'
    df.to_sql(table, engine, if_exists=mode, index=False, dtype=dtype)

def gravar_relatorio(df=None, reportname=None):
    engine = db.engine
    dtype={'created_at': DateTime, 'lastContact': DateTime}
    df['id'] = df.index
    df.to_sql(f'report_{reportname}', engine, if_exists='replace', index=False, dtype=dtype)

def gravar_todos_usuarios():

    report = bamboohr_get_report(report_id='184')
    df = pd.DataFrame.from_dict(report['employees'])

    gravar_relatorio(df=df, reportname='all_users')


if __name__ == '__main__':

    logger.info(f"<BAMBOORH> Iniciando o script em: {datetime.now()}")
    inicio = datetime.now()

    with app.app_context():
        #db.create_all()
        logger.info('Gravar o relatório de todos os usuários')
        gravar_todos_usuarios()

    logger.info(f"<BAMBOORH> Finalizando o script em: {datetime.now()}")
    fim = datetime.now()
    logger.info(f"<BAMBOORH> O script rodou em: {fim - inicio}")
