import logging

from flask import request
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from api.services.data_service import (
    get_estacoes, 
    get_autonomia_restabelecimento, 
    get_autonomia_inventario,
    get_trafego_faturamento,
    get_indisponibilidades,
    get_features, 
    get_pontuacoes, 
    get_alocacoes,
    get_disponibilidade,
    get_baterias
)


logger = logging.getLogger('__name__')
data_bp = Blueprint('data', __name__)


@data_bp.route('/estacoes', methods=['GET'])
@jwt_required()
def estacoes():
    '''
    Lista as estações cadastradas.
    ---
    tags:
        - Data
    summary: Listagem de estações.
    description: |
        Endpoint responsável por retornar todas as estações cadastradas,
        incluindo localização, cluster e informações administrativas.
    security:
        - Bearer: []
    responses:
        200:
            description: Lista de estações carregada com sucesso.
            schema:
                type: array
                items:
                    type: object
                    properties:
                        id:
                            type: integer
                        estacao:
                            type: string
                        cluster:
                            type: string
                        ibge:
                            type: string
                        uf:
                            type: string
                        municipio:
                            type: string
                        latitude:
                            type: number
                            format: float
                        longitude:
                            type: number
                            format: float
                        updated_at:
                            type: string
                            format: date-time
            examples:
                application/json:
                    - id: 1
                      estacao: 'ACABL01'
                      ibge: '3550308'
                      uf: 'SP'
                      municipio: 'São Paulo'
                      cluster: 'Capital'
                      latitude: -23.550520
                      longitude: -46.633308
                      updated_at: '2025-12-19T16:05:41.123456'
        401:
            description: Erro de autenticação JWT.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro de autenticação.
            examples:
                application/json:
                    error: '<erro de autenticação>'
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
        results = get_estacoes()
        return jsonify(results), 200

    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500


@data_bp.route('/autonomia-restabelecimento', methods=['GET'])
@jwt_required()
def autonomia_restabelecimento():
    '''
    Lista registros de autonomia e restabelecimento.
    ---
    tags:
        - Data
    summary: Listagem de autonomia e tempo médio de restabelecimento.
    description: |
        Endpoint responsável por listar os dados de autonomia média e
        tempo médio de restabelecimento por estação.
    security:
        - Bearer: []
    responses:
        200:
            description: Lista carregada com sucesso.
            schema:
                type: array
                items:
                    type: object
                    properties:
                        id:
                            type: integer
                        ano:
                            type: string
                        estacao:
                            type: string
                        autonomia_media_horas:
                            type: number
                            format: float
                        restabelecimento_medio_horas:
                            type: number
                            format: float
                        tipo_autonomia:
                            type: string
                        updated_at:
                            type: string
                            format: date-time
            examples:
                application/json:
                    - id: 1
                      ano: '2026'
                      estacao: 'ACABL01'
                      autonomia_media_horas: 2.75
                      restabelecimento_medio_horas: 2.75
                      tipo_autonomia: 'Real'
                      updated_at: '2025-12-19T16:05:41.123456'
        401:
            description: Erro de autenticação JWT.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro de autenticação.
            examples:
                application/json:
                    error: '<erro de autenticação>'
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
        results = get_autonomia_restabelecimento()
        return jsonify(results), 200

    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500


@data_bp.route('/autonomia-inventario', methods=['GET'])
@jwt_required()
def autonomia_inventario():
    '''
    Lista registros de autonomia de inventário.
    ---
    tags:
        - Data
    summary: Listagem de autonomia de inventário.
    description: |
        Endpoint responsável por listar os dados de autonomia de inventário.
    security:
        - Bearer: []
    responses:
        200:
            description: Lista de registros retornada com sucesso.
            schema:
                type: array
                items:
                    type: object
                    properties:
                        id:
                            type: integer
                        estacao:
                            type: string
                        tecnologia:
                            type: string
                        fabricante:
                            type: string
                        tensao:
                            type: string
                        quantidade:
                            type: integer
                        capacidade:
                            type: number
                            format: float
                        autonomia_horas:
                            type: number
                            format: float
                        updated_at:
                            type: string
                            format: date-time
            examples:
                application/json:
                    - id: 1
                      estacao: 'ESTAÇÃO SP-001'
                      tecnologia: 'LÍTIO'
                      fabricante: 'Moura'
                      tensao: '48'
                      quantidade: 24
                      capacidade: 100.0
                      autonomia_horas: 8.5
                      updated_at: '2026-04-13T15:32:10Z'
                    - id: 2
                      estacao: 'ESTAÇÃO RJ-010'
                      tecnologia: 'SELADA (VRLA)'
                      fabricante: 'Heliar'
                      tensao: '24'
                      quantidade: 16
                      capacidade: 150.0
                      autonomia_horas: 6.0
                      updated_at: '2026-04-12T09:18:42Z'
        401:
            description: Erro de autenticação JWT.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro de autenticação.
            examples:
                application/json:
                    error: '<erro de autenticação>'
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
        results = get_autonomia_inventario()
        return jsonify(results), 200

    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500
    

@data_bp.route('/trafego-faturamento', methods=['GET'])
@jwt_required()
def trafego_faturamento():
    '''
    Lista registros de tráfego de dados e faturamento (EWMA).
    ---
    tags:
        - Data
    summary: Listagem de métricas de tráfego e faturamento por estação.
    description: |
        Endpoint responsável por listar os dados consolidados de tráfego de dados 
        e faturamento médio (EWMA) por estação para análise de impacto.
    security:
        - Bearer: []
    responses:
        200:
            description: Lista carregada com sucesso.
            schema:
                type: array
                items:
                    type: object
                    properties:
                        id:
                            type: integer
                        estacao:
                            type: string
                        trafego_dados_ewma:
                            type: number
                            format: float
                        faturamento_ewma:
                            type: number
                            format: float
                        updated_at:
                            type: string
                            format: date-time
        401:
            description: Erro de autenticação JWT.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro de autenticação.
            examples:
                application/json:
                    error: '<erro de autenticação>'
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
        results = get_trafego_faturamento()
        return jsonify(results), 200

    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500
    

@data_bp.route('/indisponibilidades', methods=['GET'])
@jwt_required()
def indisponibilidades():
    '''
    Lista os registros de indisponibilidade calculados.
    ---
    tags:
        - Data
    summary: Listagem de indisponibilidades por estação.
    description: |
        Endpoint responsável por listar todos os registros calculados
        de indisponibilidade por estação, contendo datas de início,
        término e duração da indisponibilidade.
    security:
        - Bearer: []
    responses:
        200:
            description: Lista de indisponibilidades carregada com sucesso.
            schema:
                type: array
                items:
                    type: object
                    properties:
                        id:
                            type: integer
                        estacao:
                            type: string
                        submit_date:
                            type: string
                            format: date-time
                        clear_date:
                            type: string
                            format: date-time
                        indisponibilidade_horas:
                            type: number
                            format: float
                        updated_at:
                            type: string
                            format: date-time
            examples:
                application/json:
                    - id: 20
                      estacao: 'ACABL01'
                      submit_date: '2025-12-18T08:30:00'
                      clear_date: '2025-12-18T11:15:00'
                      indisponibilidade_horas: 2.7500
                      updated_at: '2025-12-19T10:45:22.123456'
        401:
            description: Erro de autenticação JWT.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro de autenticação.
            examples:
                application/json:
                    error: '<erro de autenticação>'
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
        results = get_indisponibilidades()
        return jsonify(results), 200

    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500
    

@data_bp.route('/pontuacoes', methods=['GET'])
@jwt_required()
def pontuacoes():
    '''
    Lista as pontuações das estações.
    ---
    tags:
        - Data
    summary: Listagem de pontuações consolidadas.
    description: |
        Endpoint responsável por retornar todas as pontuações calculadas
        para as estações, incluindo critérios de autonomia, tráfego,
        hierarquia, TMR, idade da bateria, faturamento e cliente.
    security:
        - Bearer: []
    responses:
        200:
            description: Lista de pontuações carregada com sucesso.
            schema:
                type: array
                items:
                    type: object
                    properties:
                        id:
                            type: integer
                        estacao:
                            type: string
                        pontuacao_autonomia:
                            type: number
                            format: float
                        pontuacao_trafego_dados:
                            type: number
                            format: float
                        pontuacao_hierarquia:
                            type: number
                            format: float
                        pontuacao_tmr:
                            type: number
                            format: float
                        pontuacao_idade_bateria:
                            type: number
                            format: float
                        pontuacao_faturamento:
                            type: number
                            format: float
                        pontuacao_cliente:
                            type: number
                            format: float
                        pontuacao:
                            type: number
                            format: float
                        updated_at:
                            type: string
                            format: date-time
            examples:
                application/json:
                    - id: 3
                      estacao: 'ACABL01'
                      pontuacao_autonomia: 8.50
                      pontuacao_trafego_dados: 9.20
                      pontuacao_hierarquia: 9.80
                      pontuacao_tmr: 7.40
                      pontuacao_idade_bateria: 6.30
                      pontuacao_faturamento: 8.90
                      pontuacao_cliente: 9.00
                      pontuacao: 8.55
                      updated_at: '2025-12-19T16:05:41.123456'
        401:
            description: Erro de autenticação JWT.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro de autenticação.
            examples:
                application/json:
                    error: '<erro de autenticação>'
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
        results = get_pontuacoes()
        return jsonify(results), 200

    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500


@data_bp.route('/features', methods=['GET'])
@jwt_required()
def features():
    '''
    Lista as features consolidadas por estação.
    ---
    tags:
        - Data
    summary: Listagem de features consolidadas.
    description: |
        Endpoint responsável por retornar todas as features consolidadas
        por estação utilizadas nos modelos de machine learning.
    security:
        - Bearer: []
    responses:
        200:
            description: Lista de features carregada com sucesso.
            schema:
                type: array
                items:
                    type: object
                    properties:
                        id:
                            type: integer
                        estacao:
                            type: string
                        autonomia_projetada:
                            type: number
                            format: float
                        carga:
                            type: number
                            format: float
                        pontuacao_hierarquia:
                            type: number
                            format: float
                        pontuacao:
                            type: number
                            format: float
                        updated_at:
                            type: string
                            format: date-time
            examples:
                application/json:
                    - id: 10
                      estacao: 'ACABL01'
                      autonomia_projetada: 2.75
                      carga: 80.25
                      pontuacao_hierarquia: 9.50
                      pontuacao: 87.30
                      updated_at: '2025-12-19T15:30:22.123456'
        401:
            description: Erro de autenticação JWT.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro de autenticação.
            examples:
                application/json:
                    error: '<erro de autenticação>'
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
        results = get_features()
        return jsonify(results), 200

    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500


@data_bp.route('/alocacoes', methods=['GET'])
@jwt_required()
def alocacoes():
    '''
    Lista o histórico de alocações do modelo.
    ---
    tags:
        - Data
    summary: Listagem do histórico de alocações.
    description: |
        Endpoint responsável por retornar todo o histórico de alocações calculadas pelo modelo de otimização, incluindo ganhos, custos, orçamento restante e métricas acumuladas por rodada.
    security:
        - Bearer: []
    responses:
        200:
            description: Lista de alocações carregada com sucesso.
            schema:
                type: array
                items:
                    type: object
                    properties:
                        id:
                            type: integer
                        estacao:
                            type: string
                        autonomia_projetada:
                            type: number
                            format: float
                        rodada_alocacao:
                            type: integer
                        tecnologia:
                            type: string
                        tensao:
                            type: integer
                        capacidade:
                            type: integer
                        custo:
                            type: number
                            format: float
                        ganho:
                            type: number
                            format: float
                        ganho_por_custo:
                            type: number
                            format: float
                        investimento_restante:
                            type: number
                            format: float
                        indisponibilidade_restante:
                            type: number
                            format: float
                        custo_acumulado:
                            type: number
                            format: float
                        ganho_acumulado:
                            type: number
                            format: float
                        ganho_por_milhao_investido:
                            type: number
                            format: float
                        created_at:
                            type: string
                            format: date-time
            examples:
                application/json:
                    - id: 15
                      estacao: 'ACACL01'
                      autonomia_projetada: 2.75
                      rodada_alocacao: 3
                      tecnologia: 'VENTILADA'
                      tensao: 12
                      capacidade: 100
                      custo: 4300.00
                      ganho: 12500.50
                      ganho_por_custo: 10.50
                      investimento_restante: 18500.00
                      indisponibilidade_restante: 4.75
                      custo_acumulado: 12900.00
                      ganho_acumulado: 35800.75
                      created_at: '2025-12-19T17:10:33.456789'
                      ganho_por_milhao_investido: 2.91
        401:
            description: Erro de autenticação JWT.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro de autenticação.
            examples:
                application/json:
                    error: '<erro de autenticação>'
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
        results = get_alocacoes()
        return jsonify(results), 200

    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500


@data_bp.route('/disponibilidade', methods=['GET'])
@jwt_required()
def disponibilidade():
    '''
    Lista os dados de disponibilidade das estações.
    ---
    tags:
        - Data
    summary: Listagem de indicadores de disponibilidade.
    description: |
        Endpoint responsável por retornar os dados calculados de
        disponibilidade das estações por ano, incluindo indisponibilidades,
        diferenças em relação à meta e quantidade de incidentes.
    security:
        - Bearer: []
    responses:
        200:
            description: Lista de disponibilidade carregada com sucesso.
            schema:
                type: array
                items:
                    type: object
                    properties:
                        id:
                            type: integer
                        ano:
                            type: string
                        estacao:
                            type: string
                        disponibilidade:
                            type: number
                            format: float
                        disponibilidade_parcial:
                            type: number
                            format: float
                        disponibilidade_energia:
                            type: number
                            format: float
                        indisponibilidade_horas:
                            type: number
                            format: float
                        indisponibilidade_parcial_horas:
                            type: number
                            format: float
                        indisponibilidade_energia_horas:
                            type: number
                            format: float
                        indisponibilidade_energia:
                            type: number
                            format: float
                        diferenca_meta_disponibilidade:
                            type: number
                            format: float
                        diferenca_meta_disponibilidade_parcial:
                            type: number
                            format: float
                        diferenca_meta_disponibilidade_energia:
                            type: number
                            format: float
                        incidentes:
                            type: integer
                        incidentes_parcial:
                            type: integer
                        incidentes_energia:
                            type: integer
                        updated_at:
                            type: string
                            format: date-time
            examples:
                application/json:
                    - id: 10
                      ano: '2025'
                      estacao: 'ACABL01'
                      disponibilidade: 99.35
                      disponibilidade_parcial: 99.60
                      disponibilidade_energia: 98.90
                      indisponibilidade_horas: 12.3456
                      indisponibilidade_parcial_horas: 8.1234
                      indisponibilidade_energia_horas: 4.2222
                      indisponibilidade_energia: 1.10
                      diferenca_meta_disponibilidade: -0.15
                      diferenca_meta_disponibilidade_parcial: 0.10
                      diferenca_meta_disponibilidade_energia: -0.40
                      incidentes: 5
                      incidentes_parcial: 3
                      incidentes_energia: 2
                      updated_at: '2025-12-19T16:05:41.123456'
        401:
            description: Erro de autenticação JWT.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro de autenticação.
            examples:
                application/json:
                    error: '<erro de autenticação>'
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
        results = get_disponibilidade()
        return jsonify(results), 200

    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500


@data_bp.route('/baterias', methods=['GET'])
@jwt_required()
def busca_baterias():
    '''
    Lista as baterias cadastradas.
    ---
    tags:
        - Data
    summary: Listagem de baterias.
    description: |
        Endpoint responsável por retornar todas as baterias cadastradas,
        incluindo tecnologia, fabricante, capacidade e preço.
    security:
        - Bearer: []
    responses:
        200:
            description: Lista de baterias carregada com sucesso.
            schema:
                type: array
                items:
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
        401:
            description: Erro de autenticação JWT.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro de autenticação.
            examples:
                application/json:
                    error: '<erro de autenticação>'
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
        results = get_baterias()
        return jsonify(results), 200

    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500