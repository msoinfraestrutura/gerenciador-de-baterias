import logging
from datetime import datetime, UTC
from api.extensions import db


logger = logging.getLogger(__name__)


class Pontuacoes(db.Model):
    '''Modelo para armazenar as pontuações das estações.'''
    __tablename__ = 'tb_pontuacoes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estacao = db.Column(db.String(255), nullable=True)
    pontuacao_autonomia = db.Column(db.Numeric(10, 2), nullable=True)
    pontuacao_trafego_dados = db.Column(db.Numeric(10, 2), nullable=True)
    pontuacao_hierarquia = db.Column(db.Numeric(10, 2), nullable=True)
    pontuacao_tmr = db.Column(db.Numeric(10, 2), nullable=True)
    pontuacao_idade_bateria = db.Column(db.Numeric(10, 2), nullable=True)
    pontuacao_faturamento = db.Column(db.Numeric(10, 2), nullable=True)
    pontuacao_cliente = db.Column(db.Numeric(10, 2), nullable=True)
    pontuacao = db.Column(db.Numeric(10, 2), nullable=True)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))

    def __repr__(self):
        return f'<Pontuacoes {self.estacao} -> Final: {self.score_final}>'