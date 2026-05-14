import logging

from api.extensions import db
from datetime import datetime, UTC
from sqlalchemy.exc import IntegrityError

from api.models.baterias import Baterias


logger = logging.getLogger(__name__)


def post_baterias(payload: dict) -> dict:
    '''
    Cadastra uma nova bateria.

    Returns:
        dict: Registro da bateria cadastrada, incluindo identificação,
        características técnicas, preço e data de atualização.

    Raises:
        IntegrityError: Caso a bateria já esteja cadastrada.
    '''
    bateria = Baterias(
        tecnologia=payload.get('tecnologia'),
        fabricante=payload.get('fabricante'),
        tensao=payload.get('tensao'),
        capacidade=payload.get('capacidade'),
        preco=payload.get('preco'),
        updated_at=datetime.now(UTC)
    )

    try:
        db.session.add(bateria)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise

    return {
        'id': bateria.id,
        'tecnologia': bateria.tecnologia,
        'fabricante': bateria.fabricante,
        'tensao': bateria.tensao,
        'capacidade': float(bateria.capacidade),
        'preco': float(bateria.preco),
        'updated_at': bateria.updated_at.isoformat()
    }


def put_baterias(id: int, payload: dict) -> dict:
    '''
    Atualiza o cadastro de uma bateria existente.

    Returns:
        dict: Registro da bateria atualizado, contendo identificação,
        características técnicas, preço e data de atualização.

    Raises:
        ValueError: Caso a bateria não seja encontrada.
        IntegrityError: Caso a atualização viole a regra de unicidade.
    '''
    bateria = db.session.get(Baterias, id)
    if not bateria:
        raise ValueError('Bateria não encontrada')

    bateria.tecnologia = payload.get('tecnologia', bateria.tecnologia)
    bateria.fabricante = payload.get('fabricante', bateria.fabricante)
    bateria.tensao = payload.get('tensao', bateria.tensao)
    bateria.capacidade = payload.get('capacidade', bateria.capacidade)
    bateria.preco = payload.get('preco', bateria.preco)
    bateria.updated_at = datetime.now(UTC)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise

    return {
        'id': bateria.id,
        'tecnologia': bateria.tecnologia,
        'fabricante': bateria.fabricante,
        'tensao': bateria.tensao,
        'capacidade': float(bateria.capacidade),
        'preco': float(bateria.preco),
        'updated_at': bateria.updated_at.isoformat()
    }