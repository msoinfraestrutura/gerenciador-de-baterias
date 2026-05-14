import logging
from datetime import datetime, UTC
from api.extensions import db


logger = logging.getLogger(__name__)


class Disponibilidade(db.Model):
    '''Modelo para armazenar os dados calculados de disponibilidade.'''
    __tablename__ = 'tb_disponibilidade'

    id = db.Column(db.Integer, primary_key=True)
    ano = db.Column(db.String(4), nullable=False, index=True)
    estacao = db.Column(db.String(255), nullable=False, index=True)
    disponibilidade = db.Column(db.Numeric(10, 2), nullable=True)
    disponibilidade_parcial = db.Column(db.Numeric(10, 2), nullable=True)
    disponibilidade_energia = db.Column(db.Numeric(10, 2), nullable=True)
    indisponibilidade_horas = db.Column(db.Numeric(10, 2), nullable=True)
    indisponibilidade_parcial_horas = db.Column(db.Numeric(10, 2), nullable=True)
    indisponibilidade_energia_horas = db.Column(db.Numeric(10, 2), nullable=True)
    indisponibilidade_energia = db.Column(db.Numeric(10, 2), nullable=True)
    diferenca_meta_disponibilidade = db.Column(db.Numeric(10, 2), nullable=True)
    diferenca_meta_disponibilidade_parcial = db.Column(db.Numeric(10, 2), nullable=True)
    diferenca_meta_disponibilidade_energia = db.Column(db.Numeric(10, 2), nullable=True)
    incidentes = db.Column(db.Integer, nullable=True)
    incidentes_parcial = db.Column(db.Integer, nullable=True)
    incidentes_energia = db.Column(db.Integer, nullable=True)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))

    def __repr__(self):
        return f'<Disponibilidade {self.ano} - {self.estacao}>'