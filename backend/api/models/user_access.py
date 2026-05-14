import logging
from datetime import datetime, UTC
from api.extensions import db


logger = logging.getLogger('api.models.user_access')


class UserAccess(db.Model):
    '''Modelo de dados para a tabela user_access.'''
    __tablename__ = 'tb_user_access'
    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username   = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))

    def __repr__(self):
        return f'<Username {self.username}>'