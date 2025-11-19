"""
Modelo SQLAlchemy gerado automaticamente para a tabela report_all_users.

Gerado em: 2025-11-19 14:37:27
Este arquivo é gerado automaticamente e pode ser sobrescrito.
"""

from datetime import datetime, timezone
import sys
from sqlalchemy.inspection import inspect

# Importar do Flask app o db
# Tenta importar de diferentes formas para compatibilidade
# Se todos os imports falharem, usa o db injetado externamente
try:
    # Tenta import relativo primeiro
    from .flask_models import db
except ImportError:
    try:
        # Tenta import absoluto
        from flask_models import db
    except ImportError:
        try:
            # Tenta import do módulo modules
            from modules.flask_models import db
        except ImportError:
            # Se tudo falhar, usa o db injetado externamente
            # Isso acontece quando o modelo é carregado dinamicamente
            # O db será injetado antes da execução do módulo
            try:
                # Tenta pegar do módulo atual usando __name__
                import sys
                if __name__ in sys.modules:
                    _current_module = sys.modules[__name__]
                    if hasattr(_current_module, 'db'):
                        db = _current_module.db
                    else:
                        db = globals().get('db')
                else:
                    db = globals().get('db')
            except (KeyError, NameError):
                # Se __name__ não estiver disponível, usa globals
                db = globals().get('db')


def get_utcnow():
    """Retorna datetime UTC atual de forma compatível com diferentes versões do Python"""
    python_version = sys.version_info
    if python_version >= (3, 12):
        return datetime.now(timezone.utc)
    else:
        return datetime.utcnow()


class Serializer(object):
    """Classe auxiliar para serialização de objetos"""
    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(list):
        return [info.serialize() for info in list]


class ReportAllUsers(db.Model, Serializer):
    """Modelo SQLAlchemy para a tabela report_all_users"""
    __tablename__ = 'report_all_users'

    # Chave primária automática
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Coluna original: id
    column_id = db.Column(db.String(500), nullable=True, index=True)

    customnomecompleto = db.Column(db.String(500), nullable=True)

    customnomesocial = db.Column(db.String(500), nullable=True)

    address1 = db.Column(db.String(500), nullable=True)

    mobilephone = db.Column(db.String(500), nullable=True)

    city = db.Column(db.String(500), nullable=True)

    workemail = db.Column(db.String(500), nullable=True, index=True)

    homeemail = db.Column(db.String(500), nullable=True, index=True)

    employeenumber = db.Column(db.String(500), nullable=True)

    employmenthistorystatus = db.Column(db.String(500), nullable=True)

    status = db.Column(db.String(500), nullable=True)

    jobtitle = db.Column(db.String(500), nullable=True)

    reportsto = db.Column(db.String(500), nullable=True)

    customarea1 = db.Column(db.String(500), nullable=True)

    customsubarea = db.Column(db.String(500), nullable=True)

    customcostcenter = db.Column(db.String(500), nullable=True)

    supervisoremail = db.Column(db.String(500), nullable=True, index=True)

    customrazaosocialfilial = db.Column(db.String(500), nullable=True)

    hiredate = db.Column(db.DateTime, nullable=False)

    terminationdate = db.Column(db.DateTime, nullable=False)

    customjoblevel = db.Column(db.String(500), nullable=True)

    customcpf = db.Column(db.String(500), nullable=True)

    # Coluna para armazenar JSON completo dos dados (backup/auditoria)
    raw_data = db.Column(db.JSON, nullable=True)

    # Coluna de auditoria - data/hora da gravação
    created_at = db.Column(db.DateTime, default=get_utcnow, nullable=False)

    def __repr__(self):
        """Representação string do objeto"""
        return f'<ReportAllUsers {self.id}>'

    def serialize(self):
        """Converte o objeto para dicionário"""
        data = Serializer.serialize(self)
        return data
