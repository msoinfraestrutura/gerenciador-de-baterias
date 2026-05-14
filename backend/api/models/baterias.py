import logging
from datetime import datetime, UTC
from api.extensions import db


logger = logging.getLogger(__name__)


class Baterias(db.Model):
    __tablename__ = 'tb_baterias'
    
    id = db.Column(db.Integer, primary_key=True)
    tecnologia = db.Column(db.String(255), nullable=False)
    fabricante = db.Column(db.String(255), nullable=False)
    tensao = db.Column(db.String(255), nullable=True)
    capacidade = db.Column(db.Numeric(10, 2), nullable=False)
    custo = db.Column(db.Numeric(10, 2), nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )
    
    __table_args__ = (
        db.UniqueConstraint(
            'tecnologia',
            'fabricante',
            'tensao',
            'capacidade',
            name='uq_baterias_tecnologia_fabricante_tensao_capacidade'
        ),
    )

    def __repr__(self):
        return f'<Baterias {self.fabricante} {self.tecnologia} {self.capacidade}>'
