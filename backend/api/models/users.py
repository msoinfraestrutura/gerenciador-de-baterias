import logging
from datetime import datetime, UTC
from api.extensions import db


logger = logging.getLogger('api.models.user')


class User(db.Model):
    '''Modelo de dados para a tabela de usuários.'''
    __tablename__ = 'tb_users'
    id = db.Column(db.Integer, primary_key=True)
    username =   db.Column(db.String(80), unique=True, nullable=False)
    password =   db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))

    def __repr__(self):
        return f'<User {self.username}>'