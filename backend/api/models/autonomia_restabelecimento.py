import logging
from datetime import datetime, UTC
from api.extensions import db


logger = logging.getLogger(__name__)


class AutonomiaRestabelecimento(db.Model):
    __tablename__ = 'tb_autonomia_restabelecimento'
    
    id = db.Column(db.Integer, primary_key=True)
    estacao = db.Column(db.String(255), nullable=False, index=True)
    autonomia_media_horas = db.Column(db.Numeric(10, 2), nullable=True)
    restabelecimento_medio_horas = db.Column(db.Numeric(10, 2), nullable=True)
    tipo_autonomia = db.Column(db.String(50), nullable=True)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))

    def __repr__(self):
        return f'<AutonomiaRestabelecimento {self.estacao}>'