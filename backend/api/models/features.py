import logging
from datetime import datetime, UTC
from api.extensions import db


logger = logging.getLogger(__name__)


class Features(db.Model):
    '''Modelo para armazenar as features consolidadas por estação.'''
    __tablename__ = 'tb_features'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estacao = db.Column(db.String(255), nullable=False)
    autonomia_projetada = db.Column(db.Numeric(10, 2), nullable=True)
    carga = db.Column(db.Numeric(15, 2), nullable=True)
    pontuacao_hierarquia = db.Column(db.Numeric(10, 2), nullable=True)
    pontuacao = db.Column(db.Numeric(10, 2), nullable=True)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))

    def __repr__(self):
        return f'<Features {self.estacao}>'