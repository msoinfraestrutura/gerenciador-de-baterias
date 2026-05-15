import logging
from datetime import datetime, UTC
from api.extensions import db


logger = logging.getLogger(__name__)


class Alocacoes(db.Model):
    __tablename__ = 'tb_alocacoes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    estacao = db.Column(db.String(255), nullable=True)
    autonomia_projetada = db.Column(db.Numeric(10, 2), nullable=True)
    rodada_alocacao = db.Column(db.Integer, nullable=True)
    tecnologia = db.Column(db.String(50), nullable=True)
    tensao = db.Column(db.Integer, nullable=True)
    capacidade = db.Column(db.Integer, nullable=True)
    custo = db.Column(db.Numeric(10, 2), nullable=True)
    ganho = db.Column(db.Numeric(10, 2), nullable=True)
    ganho_por_custo = db.Column(db.Numeric(10, 4), nullable=True)
    investimento_restante = db.Column(db.Numeric(15, 2), nullable=True)
    indisponibilidade_restante = db.Column(db.Numeric(10, 2), nullable=True)
    custo_acumulado = db.Column(db.Numeric(15, 2), nullable=True)
    ganho_acumulado = db.Column(db.Numeric(15, 2), nullable=True)
    ganho_por_milhao_investido = db.Column(db.Numeric(10, 2), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))

    def __repr__(self):
        return f'<Alocacoes {self.id} - {self.estacao}>'
