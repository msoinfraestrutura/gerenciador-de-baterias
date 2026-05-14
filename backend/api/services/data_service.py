import logging
from api.models.estacoes import Estacoes
from api.models.autonomia_restabelecimento import AutonomiaRestabelecimento
from api.models.autonomia_inventario import AutonomiaInventario
from api.models.trafego_faturamento import TrafegoFaturamento
from api.models.indisponibilidades import Indisponibilidades
from api.models.pontuacoes import Pontuacoes
from api.models.features import Features
from api.models.alocacoes import Alocacoes
from api.models.disponibilidade import Disponibilidade
from api.models.baterias import Baterias


logger = logging.getLogger(__name__)


def get_estacoes():
    '''
    Realiza a consulta completa e ordenada da tabela tb_estacoes,
    retornando os dados cadastrais e geográficos das estações.

    Returns:
        List[Dict[str, Any]]: Lista de registros contendo as informações
        das estações.
    '''
    try:
        data = Estacoes.query.order_by(Estacoes.id.asc()).all()
        logger.info(f'Consulta realizada com sucesso: {len(data)} registros')

        return [
            {
                'id': r.id,
                'estacao': r.estacao,
                'cluster': r.cluster,
                'uf': r.uf,
                'municipio': r.municipio,
                'ibge': r.ibge,
                'latitude': float(r.latitude) if r.latitude is not None else None,
                'longitude': float(r.longitude) if r.longitude is not None else None,
                'updated_at': r.updated_at.isoformat() if r.updated_at else None
            }
            for r in data
        ]

    except Exception:
        logger.exception('Erro ao executar consulta')
        raise


def get_autonomia_restabelecimento():
    '''
    Realiza a consulta completa e ordenada da tabela tb_autonomia_restabelecimento,
    retornando métricas de autonomia e tempo médio de restabelecimento por estação.

    Returns:
        List[Dict[str, Any]]: Lista de registros contendo informações de autonomia,
        tempo médio de restabelecimento e metadados das estações.
    '''
    try:
        data = AutonomiaRestabelecimento.query.order_by(AutonomiaRestabelecimento.id.asc()).all()
        logger.info(f'Consulta realizada com sucesso: {len(data)} registros')
        return [
            {
                'id': r.id,
                'estacao': r.estacao,
                'autonomia_media_horas': float(r.autonomia_media_horas) if r.autonomia_media_horas is not None else None,
                'restabelecimento_medio_horas': float(r.restabelecimento_medio_horas) if r.restabelecimento_medio_horas is not None else None,
                'tipo_autonomia': r.tipo_autonomia,
                'updated_at': r.updated_at.isoformat() if r.updated_at else None
            }
            for r in data
        ]
    except Exception:
        logger.exception('Erro ao executar consulta')
        raise


def get_autonomia_inventario():
    """
    Consulta completa da tabela tb_autonomia_inventario,
    retornando as combinações válidas de baterias e dados
    de autonomia por estação.
    """
    try:
        data = (
            AutonomiaInventario
            .query
            .order_by(
                AutonomiaInventario.tecnologia.asc(),
                AutonomiaInventario.fabricante.asc(),
                AutonomiaInventario.capacidade.asc()
            )
            .all()
        )

        logger.info(f'Consulta realizada com sucesso: {len(data)} registros')

        return [
            {
                'id': r.id,
                'estacao': r.estacao,
                'tecnologia': r.tecnologia,
                'fabricante': r.fabricante,
                'tensao': r.tensao,
                'quantidade': r.quantidade,
                'capacidade': float(r.capacidade) if r.capacidade is not None else None,
                'autonomia_horas': float(r.autonomia_horas) if r.autonomia_horas is not None else None,
                'updated_at': r.updated_at.isoformat() if r.updated_at else None
            }
            for r in data
        ]

    except Exception:
        logger.exception(
            'Erro ao executar consulta em tb_autonomia_inventario'
        )
        raise
    

def get_trafego_faturamento():
    '''
    Realiza a consulta completa e ordenada da tabela tb_trafego_faturamento,
    retornando as métricas de tráfego e faturamento EWMA por estação.

    Returns:
        List[Dict[str, Any]]: Lista de registros contendo informações de tráfego,
        faturamento e metadados de atualização.
    '''
    try:
        data = TrafegoFaturamento.query.order_by(TrafegoFaturamento.id.asc()).all()
        logger.info(f'Consulta realizada com sucesso: {len(data)} registros em trafego_faturamento')
        
        return [
            {
                'id': r.id,
                'estacao': r.estacao,
                'trafego_dados_ewma': float(r.trafego_dados_ewma) if r.trafego_dados_ewma is not None else None,
                'faturamento_ewma': float(r.faturamento_ewma) if r.faturamento_ewma is not None else None,
                'updated_at': r.updated_at.isoformat() if r.updated_at else None
            }
            for r in data
        ]
    except Exception:
        logger.exception('Erro ao executar consulta')
        raise


def get_indisponibilidades():
    '''
    Realiza a consulta completa e ordenada da tabela tb_indisponibilidades,
    retornando os períodos de indisponibilidade registrados por estação.

    Returns:
        List[Dict[str, Any]]: Lista de registros contendo datas de início e término
        das indisponibilidades, duração em horas e metadados das estações.
    '''
    try:
        data = Indisponibilidades.query.order_by(Indisponibilidades.id.asc()).all()
        logger.info(f'Consulta realizada com sucesso: {len(data)} registros')
        return [
            {
                'id': r.id,
                'estacao': r.estacao,
                'submit_date': r.submit_date.isoformat() if r.submit_date else None,
                'clear_date': r.clear_date.isoformat() if r.clear_date else None,
                'indisponibilidade_horas': float(r.indisponibilidade_horas) if r.indisponibilidade_horas is not None else None,
                'updated_at': r.updated_at.isoformat() if r.updated_at else None
            }
            for r in data
        ]
    except Exception:
        logger.exception('Erro ao executar consulta')
        raise
    

def get_pontuacoes():
    '''
    Realiza a consulta completa e ordenada da tabela tb_pontuacoes,
    retornando as pontuações calculadas para cada estação com base
    em múltiplos critérios operacionais e estratégicos.

    Returns:
        List[Dict[str, Any]]: Lista de registros contendo as pontuações
        individuais por critério e a pontuação total de cada estação.

    '''
    try:
        data =  Pontuacoes.query.order_by(Pontuacoes.id.asc()).all()
        logger.info(f'Consulta realizada com sucesso: {len(data)} registros')
        return [
            {
                'id': r.id,
                'estacao': r.estacao,
                'pontuacao_autonomia': float(r.pontuacao_autonomia) if r.pontuacao_autonomia is not None else None,
                'pontuacao_trafego_dados': float(r.pontuacao_trafego_dados) if r.pontuacao_trafego_dados is not None else None,
                'pontuacao_hierarquia': float(r.pontuacao_hierarquia) if r.pontuacao_hierarquia is not None else None,
                'pontuacao_tmr': float(r.pontuacao_tmr) if r.pontuacao_tmr is not None else None,
                'pontuacao_idade_bateria': float(r.pontuacao_idade_bateria) if r.pontuacao_idade_bateria is not None else None,
                'pontuacao_faturamento': float(r.pontuacao_faturamento) if r.pontuacao_faturamento is not None else None,
                'pontuacao_cliente': float(r.pontuacao_cliente) if r.pontuacao_cliente is not None else None,
                'pontuacao': float(r.pontuacao) if r.pontuacao is not None else None,
                'updated_at': r.updated_at.isoformat() if r.updated_at else None
            }
            for r in data
        ]
    except Exception:
        logger.exception('Erro ao executar consulta')
        raise

def get_features():
    '''
    Realiza a consulta completa e ordenada da tabela tb_features,
    retornando características operacionais e indicadores derivados
    relacionados às estações.

    Returns:
        List[Dict[str, Any]]: Lista de registros contendo capacidades,
        cargas, métricas de indisponibilidade e pontuações associadas
        a cada estação.
    '''
    try:
        data = Features.query.order_by(Features.id.asc()).all()
        logger.info(f'Consulta realizada com sucesso: {len(data)} registros')
        return [
            {
                'id': r.id,
                'estacao': r.estacao,
                'capacidade_baterias': float(r.capacidade_baterias) if r.capacidade_baterias is not None else None,
                'carga': float(r.carga) if r.carga is not None else None,
                'indisponibilidade_media_horas': float(r.indisponibilidade_media_horas) if r.indisponibilidade_media_horas is not None else None,
                'pontuacao_hierarquia': float(r.pontuacao_hierarquia) if r.pontuacao_hierarquia is not None else None,
                'pontuacao': float(r.pontuacao) if r.pontuacao is not None else None,
                'updated_at': r.updated_at.isoformat() if r.updated_at else None
            }
            for r in data
        ]
    except Exception:
        logger.exception('Erro ao executar consulta')
        raise

def get_alocacoes():
    '''
    Realiza a consulta completa e ordenada da tabela tb_alocacoes,
    retornando o histórico detalhado das rodadas de alocação de recursos.

    Returns:
        List[Dict[str, Any]]: Lista de registros contendo informações
        de ganho, custo, orçamento restante, métricas acumuladas e
        dados temporais de cada rodada de alocação por estação.
    '''
    try:
        data =  Alocacoes.query.order_by(Alocacoes.id.asc()).all()
        logger.info(f'Consulta realizada com sucesso: {len(data)} registros')
        return [
            {
                'id': r.id,
                'estacao': r.estacao,
                'rodada_alocacao': r.rodada_alocacao,
                'ganho': float(r.ganho) if r.ganho is not None else None,
                'custo': float(r.custo) if r.custo is not None else None,
                'investimento_restante': float(r.investimento_restante) if r.investimento_restante is not None else None,
                'indisponibilidade_restante': float(r.indisponibilidade_restante) if r.indisponibilidade_restante is not None else None,
                'ganho_acumulado': float(r.ganho_acumulado) if r.ganho_acumulado is not None else None,
                'custo_acumulado': float(r.custo_acumulado) if r.custo_acumulado is not None else None,
                'ganho_por_milhao_investido': float(r.ganho_por_milhao_investido) if r.ganho_por_milhao_investido is not None else None,
                'created_at': r.created_at.isoformat() if r.created_at else None
            }
            for r in data
        ]
    except Exception:
        logger.exception('Erro ao executar consulta')
        raise


def get_disponibilidade():
    '''
    Realiza a consulta completa e ordenada da tabela tb_disponibilidade,
    retornando os indicadores de disponibilidade das estações.

    Returns:
        List[Dict[str, Any]]: Lista de registros contendo os dados
        de disponibilidade, indisponibilidade e incidentes por estação.
    '''
    try:
        data = Disponibilidade.query.order_by(Disponibilidade.id.asc()).all()
        logger.info(f'Consulta realizada com sucesso: {len(data)} registros')

        return [
            {
                'id': r.id,
                'ano': r.ano,
                'estacao': r.estacao,
                'disponibilidade': float(r.disponibilidade) if r.disponibilidade is not None else None,
                'disponibilidade_parcial': float(r.disponibilidade_parcial) if r.disponibilidade_parcial is not None else None,
                'disponibilidade_energia': float(r.disponibilidade_energia) if r.disponibilidade_energia is not None else None,
                'indisponibilidade_horas': float(r.indisponibilidade_horas) if r.indisponibilidade_horas is not None else None,
                'indisponibilidade_parcial_horas': float(r.indisponibilidade_parcial_horas) if r.indisponibilidade_parcial_horas is not None else None,
                'indisponibilidade_energia_horas': float(r.indisponibilidade_energia_horas) if r.indisponibilidade_energia_horas is not None else None,
                'indisponibilidade_energia': float(r.indisponibilidade_energia) if r.indisponibilidade_energia is not None else None,
                'diferenca_meta_disponibilidade': float(r.diferenca_meta_disponibilidade) if r.diferenca_meta_disponibilidade is not None else None,
                'diferenca_meta_disponibilidade_parcial': float(r.diferenca_meta_disponibilidade_parcial) if r.diferenca_meta_disponibilidade_parcial is not None else None,
                'diferenca_meta_disponibilidade_energia': float(r.diferenca_meta_disponibilidade_energia) if r.diferenca_meta_disponibilidade_energia is not None else None,
                'incidentes': r.incidentes,
                'incidentes_parcial': r.incidentes_parcial,
                'incidentes_energia': r.incidentes_energia,
                'updated_at': r.updated_at.isoformat() if r.updated_at else None
            }
            for r in data
        ]

    except Exception:
        logger.exception('Erro ao executar consulta')
        raise


def get_baterias():
    '''
    Realiza a consulta completa e ordenada da tabela tb_baterias.

    Returns:
        List[Dict[str, Any]]: Lista de registros contendo informações
        sobre tecnologia, fabricante, capacidade, preço e data de atualização.
    '''
    try:
        data = Baterias.query.order_by(Baterias.id.asc()).all()
        logger.info(f'Consulta realizada com sucesso: {len(data)} registros')

        return [
            {
                'id': r.id,
                'tecnologia': r.tecnologia,
                'fabricante': r.fabricante,
                'tensao': r.tensao,
                'capacidade': float(r.capacidade) if r.capacidade is not None else None,
                'preco': float(r.preco) if r.preco is not None else None,
                'updated_at': r.updated_at.isoformat() if r.updated_at else None
            }
            for r in data
        ]

    except Exception:
        logger.exception('Erro ao executar consulta de baterias')
        raise