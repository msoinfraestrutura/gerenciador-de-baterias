import logging
from datetime import datetime, UTC
from api.extensions import db


logger = logging.getLogger(__name__)


class Indisponibilidades(db.Model):
    '''Modelo para armazenar os dados calculados de indisponibilidade.'''
    __tablename__ = 'tb_indisponibilidades'
    
    id = db.Column(db.Integer, primary_key=True)
    estacao = db.Column(db.String(255), nullable=False, index=True)
    submit_date = db.Column(db.DateTime, nullable=False)
    clear_date = db.Column(db.DateTime, nullable=False)
    indisponibilidade_horas = db.Column(db.Numeric(10, 2), nullable=True)
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(UTC))
        
    def __repr__(self):
        return f'<Indisponibilidades {self.estacao}>'