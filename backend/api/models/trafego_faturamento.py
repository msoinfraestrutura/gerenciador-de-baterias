import logging
from datetime import datetime, UTC
from api.extensions import db


logger = logging.getLogger(__name__)


class TrafegoFaturamento(db.Model):
    __tablename__ = 'tb_trafego_faturamento'
    
    id = db.Column(db.Integer, primary_key=True)
    estacao = db.Column(db.String(255), nullable=False, index=True)
    trafego_dados_ewma = db.Column(db.Numeric(10, 4), nullable=True)
    faturamento_ewma = db.Column(db.Numeric(10, 4), nullable=True)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))

    def __repr__(self):
        return f'<AutonomiaRestabelecimento {self.estacao}>'