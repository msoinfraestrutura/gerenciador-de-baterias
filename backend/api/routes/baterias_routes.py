import logging

from flask import request
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from api.services.baterias_service import post_baterias, put_baterias


logger = logging.getLogger('__name__')
baterias_bp = Blueprint('baterias', __name__)


@baterias_bp.route('/baterias', methods=['POST'])
@jwt_required()
def cadastra_baterias():

    '''
    Cadastra uma nova bateria.
    ---
    tags:
        - Data
    summary: Cadastro de bateria.
    description: |
        Endpoint responsável por cadastrar uma nova bateria no sistema,
        considerando as regras de unicidade baseadas em tecnologia,
        fabricante, tensão e capacidade.
    security:
        - Bearer: []
    responses:
        201:
            description: Bateria cadastrada com sucesso.
            schema:
                type: object
                properties:
                    id:
                        type: integer
                    tecnologia:
                        type: string
                    fabricante:
                        type: string
                    tensao:
                        type: string
                    capacidade:
                        type: number
                        format: float
                    custo:
                        type: number
                        format: float
                    updated_at:
                        type: string
                        format: date-time
            examples:
                application/json:
                    id: 2
                    tecnologia: 'LÍTIO'
                    fabricante: 'NEWMAX'
                    tensao: 48V
                    capacidade: 100.0
                    custo: 3226.56
                    updated_at: '2026-04-11T09:15:44.987654'
        409:
            description: Registro duplicado de bateria.
        500:
            description: Erro interno do servidor.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro interno do servidor.
            examples:
                application/json:
                    error: '<erro interno do servidor>'
    '''
    try:
        payload = request.get_json()
        result = post_baterias(payload)
        return jsonify(result), 201

    except IntegrityError:
        return jsonify({'error': 'Bateria já cadastrada'}), 409

    except Exception as e:
        logger.exception('Erro ao cadastrar bateria')
        return jsonify({'error': str(e)}), 500


@baterias_bp.route('/baterias/<int:id>', methods=['PUT'])
@jwt_required()
def atualiza_baterias(id):

    '''
    Atualiza o cadastro de uma bateria existente.
    ---
    tags:
        - Data
    summary: Atualização de cadastro de bateria.
    description: |
        Endpoint responsável por atualizar os dados de uma bateria
        previamente cadastrada no sistema.
    security:
        - Bearer: []
    responses:
        200:
            description: Cadastro da bateria atualizado com sucesso.
            schema:
                type: object
                properties:
                    id:
                        type: integer
                    tecnologia:
                        type: string
                    fabricante:
                        type: string
                    tensao:
                        type: string
                    capacidade:
                        type: number
                        format: float
                    custo:
                        type: number
                        format: float
                    updated_at:
                        type: string
                        format: date-time
            examples:
                application/json:
                    id: 1
                    tecnologia: 'VRLA'
                    fabricante: 'NEWMAX'
                    tensao: 12V
                    capacidade: 180.0
                    custo: 7800.00
                    updated_at: '2026-04-12T16:08:59.456321'
        404:
            description: Bateria não encontrada.
        409:
            description: Registro duplicado de bateria.
        500:
            description: Erro interno do servidor.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro interno do servidor.
            examples:
                application/json:
                    error: '<erro interno do servidor>'
    '''

    try:
        payload = request.get_json()
        result = put_baterias(id, payload)
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 404

    except IntegrityError:
        return jsonify({'error': 'Bateria já cadastrada'}), 409

    except Exception as e:
        logger.exception('Erro ao atualizar bateria')
        return jsonify({'error': str(e)}), 500