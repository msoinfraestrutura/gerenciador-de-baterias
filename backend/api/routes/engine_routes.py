import logging

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from api.services.engine_service import run_load_data, run_feature_engineering, run_training_data


logger = logging.getLogger('__name__')
engine_bp = Blueprint('engine', __name__)


@engine_bp.route('/load-data', methods=['POST'])
@jwt_required()
def load_data():
    '''
    Executa a extração de dados brutos dos bancos.
    ---
    tags:
        - Engine
    summary: Carga e extração de dados.
    description: |
        Executa a extração dos bancos de dados infra_am e smartplan através de túnel SSH,
        convertendo os resultados para arquivos .pkl na camada raw.
    security:
        - Bearer: []
    responses:
        200:
            description: Extração de dados concluída com sucesso.
            schema:
                type: object
                properties:
                    msg:
                        type: string
            examples:
                application/json:
                    msg: 'Extração concluída com sucesso'
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
                    error: 'Erro de autenticação'
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
        run_load_data()
        return jsonify({'msg': 'Extração de dados concluída com sucesso'}), 200
    
    except Exception as e:
        logger.error(f'Erro ao realizar extração de dados: {e}')
        return jsonify({'error': str(e)}), 500


@engine_bp.route('/feature-engineering', methods=['POST'])
@jwt_required()
def feature_engineering():
    '''
    Executa a engenharia de features e retorna os scores processados.
    ---
    tags:
        - Engine
    summary: Engenharia de features.
    description: |
        Consolida as pontuações (scores) e gera a base de features,
        persistindo no banco de dados e retornando os dados em formato JSON.
    security:
        - Bearer: []
    responses:
        200:
            description: Engenharia de features concluída e persistida com sucesso.
            schema:
                type: object
                properties:
                    scores:
                        type: array
                        items:
                            type: object
                    features:
                        type: array
                        items:
                            type: object
            examples:
                application/json:
                    features:
                        - estacao: 'ACABL01'
                          capacidade_baterias: 400
                          carga: 162
                          indisponibilidade_media_horas: 0.84
                          pontuacao: 19.96
                          pontuacao_hierarquia: 70
                    scores:
                        - estacao: 'SIVIN10'
                          pontuacao_autonomia: 5
                          pontuacao_trafego_dados: 5
                          pontuacao_hierarquia: 70
                          pontuacao_tmr: 3
                          pontuacao_idade_bateria: 5
                          pontuacao_faturamento: 5
                          pontuacao_cliente: 1
                          pontuacao: 21.47
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
                    error: 'Erro de autenticação'
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
        data = run_feature_engineering()
        return jsonify(data), 200
    
    except Exception as e:
        logger.error(f'Erro ao realizar engenharia de features: {e}')
        return jsonify({'error': str(e)}), 500


@engine_bp.route('/training-data', methods=['POST'])
@jwt_required()
def training_data():
    '''
    Executa o otimizador de alocação de baterias.
    ---
    tags:
        - Engine
    summary: Otimização de alocação com parâmetros dinâmicos.
    description: |
        Executa a lógica de alocação baseada em prioridades e custos. 
        Permite definir dinamicamente os valores de custo/capacidade das 
        baterias e o orçamento total para a simulação.
    parameters:
        - name: body
          in: body
          required: true
          schema:
            type: object
            properties:
                baterias:
                    type: object
                investimento:
                    type: number
    security:
        - Bearer: []
    responses:
        200:
            description: Alocações concluídas e persistidas com sucesso.
            schema:
                type: array
                items:
                    type: object
                    properties:
                        estacao:
                            type: string
                        rodada_alocacao:
                            type: integer
                        bateria:
                            type: string
                        capacidade:
                            type: number
                        custo:
                            type: number
                            format: float
                        ganho:
                            type: number
                            format: float
                        investimento_restante:
                            type: number
                            format: float
                        indisponibilidade_restante:
                            type: number
                            format: floata.
                        ganho_acumulado:
                            type: number
                            format: float
                        custo_acumulado:
                            type: number
                            format: float
                        ganho_por_milhao_investido:
                            type: number
                            format: float
            examples:
                application/json:
                    - estacao: ACABL01
                      rodada_alocacao: 1
                      bateria: LITIO_48V
                      capacidade: 100
                      custo: 8383.2
                      ganho: 120.5
                      investimento_restante: 991616.8
                      indisponibilidade_restante: 23.4
                      ganho_acumulado: 120.5
                      custo_acumulado: 8383.2
                      ganho_por_milhao_investido: 14379.21
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
                    error: 'Erro de autenticação'
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
        config = request.get_json() or {}
        data = run_training_data(config=config)
        return jsonify(data), 200
    
    except Exception as e:
        logger.error(f'Falha ao executar motor de alocações: {e}')
        return jsonify({'error': str(e)}), 500


@engine_bp.route('/full-pipeline', methods=['POST'])
@jwt_required()
def full_pipeline():
    '''
    Executa o pipeline completo: Carga, Feature Engineering e Treinamento.
    ---
    tags:
        - Engine
    summary: Pipeline completo de ponta a ponta.
    description: |
        Executa sequencialmente a extração de dados brutos, a geração de features 
        e o motor de alocação (otimizador). Aceita os mesmos parâmetros de orçamento 
        e baterias da rota de training-data.
    parameters:
        - name: body
          in: body
          required: true
          schema:
            type: object
            properties:
                baterias:
                    type: object
                investimento:
                    type: number
    security:
        - Bearer: []
    responses:
        200:
            description: Pipeline finalizado com sucesso.
            schema:
                type: object
                properties:
                    status:
                        type: string
                    results:
                        type: array
                        items:
                            type: object
                            properties:
                                estacao:
                                    type: string
                                rodada_alocacao:
                                    type: integer
                                bateria:
                                    type: string
                                capacidade:
                                    type: number
                                custo:
                                    type: number
                                    format: float
                                ganho:
                                    type: number
                                    format: float
                                investimento_restante:
                                    type: number
                                    format: float
                                indisponibilidade_restante:
                                    type: number
                                    format: float
                                ganho_acumulado:
                                    type: number
                                    format: float
                                custo_acumulado:
                                    type: number
                                    format: float
                                ganho_por_milhao_investido:
                                    type: number
                                    format: float
            examples:
                application/json:
                    status: Pipeline executado com sucesso
                    results:
                        - estacao: ACABL01
                          rodada_alocacao: 1
                          bateria: LITIO_48V
                          capacidade: 100
                          custo: 8383.2
                          ganho: 120.5
                          investimento_restante: 991616.8
                          indisponibilidade_restante: 23.4
                          ganho_acumulado: 120.5
                          custo_acumulado: 8383.2
                          ganho_por_milhao_investido: 14379.21
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
        config = request.get_json() or {}
        
        logger.info('Executando pipeline completo')

        logger.info('Etapa 1/3: Executando extração de dados')
        run_load_data()

        logger.info('Etapa 2/3: Executando engenharia de features')
        run_feature_engineering()

        logger.info('Etapa 3/3: Executando motor de alocação')
        results = run_training_data(config=config)

        return jsonify({
            'status': 'Pipeline executado com sucesso',
            'results': results
        }), 200
    
    except Exception as e:
        logger.error(f'Falha na execução do pipeline: {e}')
        return jsonify({'error': str(e)}), 500