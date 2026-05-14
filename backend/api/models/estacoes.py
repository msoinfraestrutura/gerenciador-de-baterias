import logging
from datetime import datetime, UTC
from api.extensions import db


logger = logging.getLogger(__name__)


class Estacoes(db.Model):
    '''Modelo para armazenar os dados das estações.'''
    __tablename__ = 'tb_estacoes'

    id = db.Column(db.Integer, primary_key=True)
    estacao = db.Column(db.String(255), nullable=False, index=True)
    cluster = db.Column(db.String(255), nullable=True, index=True)
    uf = db.Column(db.String(2), nullable=True, index=True)
    municipio = db.Column(db.String(255), nullable=True)
    ibge = db.Column(db.String(20), nullable=True)
    latitude = db.Column(db.Numeric(11, 8), nullable=True)
    longitude = db.Column(db.Numeric(11, 8), nullable=True)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))

    def __repr__(self):
        return f'<Estacoes {self.estacao}>'