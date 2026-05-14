import logging
from datetime import datetime, UTC
from api.extensions import db


logger = logging.getLogger(__name__)


class AutonomiaInventario(db.Model):
    __tablename__ = 'tb_autonomia_inventario'
    
    id = db.Column(db.Integer, primary_key=True)
    estacao = db.Column(db.String(255), nullable=False, index=True)
    tecnologia = db.Column(db.String(255), nullable=True)
    fabricante = db.Column(db.String(255), nullable=True)
    tensao = db.Column(db.String(255), nullable=True)
    quantidade = db.Column(db.Integer(), nullable=True)
    capacidade = db.Column(db.Numeric(10, 2), nullable=True)
    autonomia_horas = db.Column(db.Numeric(10, 2), nullable=True)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))

    def __repr__(self):
        return f'<AutonomiaInventario {self.estacao}>'