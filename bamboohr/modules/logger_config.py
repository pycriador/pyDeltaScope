#Logs do sistema
import logging
import logging.handlers
import json
import os
from datetime import datetime
from pathlib import Path

class DatadogJSONFormatter(logging.Formatter):
    """
    Formatter que converte logs para formato JSON compatível com Datadog.
    """
    def format(self, record):
        # Formata timestamp em ISO 8601 (formato que Datadog espera)
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        # Monta o objeto JSON no formato Datadog
        log_data = {
            'timestamp': timestamp,
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name,
            'service': 'bamboohr',
            'source': 'python',
            'thread': record.threadName,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Adiciona exception info se houver
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Adiciona campos extras se existirem
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        return json.dumps(log_data, ensure_ascii=False)


# Configuração do LOG
logFormatter = logging.Formatter("%(asctime)s [%(name)-0s] [%(levelname)-0s]  %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#logging.getLogger('boto').setLevel(logging.CRITICAL)
#logging.getLogger('boto3').setLevel(logging.CRITICAL)
#logging.getLogger('botocore').setLevel(logging.CRITICAL)
#logging.getLogger('s3transfer').setLevel(logging.CRITICAL)
#logging.getLogger('urllib3').setLevel(logging.CRITICAL)
logging.getLogger('googleapi').setLevel(logging.WARNING)
logging.getLogger("googleapiclient.discovery").setLevel(logging.WARNING)
logging.getLogger("googleapiclient").setLevel(logging.WARNING)

# Handler para arquivo JSON (formato Datadog)
log_dir = Path('/tmp/bamboohr_logs')
log_dir.mkdir(exist_ok=True, mode=0o755)

json_file_handler = logging.handlers.RotatingFileHandler(
    log_dir / 'bamboohr.json.log',
    maxBytes=20971520,  # 20MB
    backupCount=5,
    encoding='utf-8'
)
json_formatter = DatadogJSONFormatter()
json_file_handler.setFormatter(json_formatter)
logger.addHandler(json_file_handler)

# Handler para arquivo texto (formato legível)
fileHandler = logging.handlers.RotatingFileHandler(
    '/tmp/infosec_bamboorh.log',
    maxBytes=20971520,
    backupCount=5
)
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

# Handler para console (formato legível)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)