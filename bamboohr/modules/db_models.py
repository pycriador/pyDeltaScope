#import jwt
#from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.inspection import inspect

#Importar do App.py o app Flask e configurações do DB
from .flask_models import db

class Serializer(object):
    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(list):
        return [info.serialize() for info in list]
    
class InsertLog(db.Model, Serializer):
    __bind_key__ = None
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    msg = db.Column(db.String(500))
    app = db.Column(db.String(50))
    date = db.Column(db.DateTime)
 
    def serialize(self):
        data = Serializer.serialize(self)
        return data
