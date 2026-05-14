import logging
from datetime import datetime, UTC
from api.extensions import db


logger = logging.getLogger('api.models.refresh_token_manager')


class RefreshTokenManager(db.Model):
    '''Modelo de dados para a tabela refresh_token_manager.'''
    __tablename__ = 'tb_refresh_token_manager'
    id                      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username                = db.Column(db.String(80), nullable=False)
    refresh_token           = db.Column(db.Text, nullable=True)
    refresh_token_expire_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at              = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))

    def __repr__(self):
        return f'<Username {self.username}>'