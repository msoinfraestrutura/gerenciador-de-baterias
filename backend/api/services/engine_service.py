import logging

from sshtunnel import SSHTunnelForwarder
import pymysql
import psycopg2
import pandas as pd
import numpy as np
from sqlalchemy import text

from . import (
    SSH_HOST,
    SSH_USER,
    SSH_PASSWORD,
    MYSQL_DB_HOST,
    MYSQL_DB_PORT,
    MYSQL_DB_NAME_1,
    MYSQL_DB_USER,
    MYSQL_DB_PASSWORD,
    MYSQL_LOCAL_PORT_TUNNEL,
    PG_DB_HOST,
    PG_DB_PORT,
    PG_DB_USER,
    PG_DB_PASSWORD,
    PG_LOCAL_PORT_TUNNEL,
    PG_DB_NAME_1,
    PG_DB_NAME_2,
    MYSQL_SQL_QUERY_1,
    MYSQL_SQL_QUERY_2,
    MYSQL_SQL_QUERY_3,
    MYSQL_SQL_QUERY_4,
    PG_SQL_QUERY_1,
    PG_SQL_QUERY_2,
    PG_SQL_QUERY_3,
    PG_SQL_QUERY_4
)
from .feature_engineering.get_autonomia_restabelecimento import run_autonomia_restabelecimento
from .feature_engineering.get_fontes import run_fontes
from .feature_engineering.get_pontuacao_autonomia import run_pontuacao_autonomia
from .feature_engineering.get_pontuacao_cliente import run_pontuacao_cliente
from .feature_engineering.get_pontuacao_hierarquia import run_pontuacao_hierarquia
from .feature_engineering.get_pontuacao_idade_bateria import run_pontuacao_idade_bateria
from .feature_engineering.get_pontuacao_tmr import run_pontuacao_tmr
from .feature_engineering.get_pontuacao_trafego_faturamento import run_pontuacao_trafego_faturamento
from .feature_engineering.get_features import run_features
from .engine.allocation_engine import run_allocation_engine

from api.extensions import db
from api.models.indisponibilidades import Indisponibilidades
from api.models.disponibilidade import Disponibilidade
from api.models.estacoes import Estacoes
from api.models.autonomia_inventario import AutonomiaInventario
from api.models.autonomia_restabelecimento import AutonomiaRestabelecimento
from api.models.trafego_faturamento import TrafegoFaturamento
from api.models.pontuacoes import Pontuacoes
from api.models.alocacoes import Alocacoes
from api.models.features import Features


logger = logging.getLogger(__name__)


def insert_data(
    df: pd.DataFrame,
    model: str,
    truncate: bool = True
) -> None:
    '''
    Insere dados no banco a partir de um DataFrame usando bulk insert.

    Args:
        df (pd.DataFrame): DataFrame com os dados.
        model (Type): Model SQLAlchemy.
        truncate (bool): Se True, remove os registros existentes antes da inserção.
    '''
    if df is None or df.empty:
        logger.warning(f'DataFrame vazio para {model.__tablename__}, nada a inserir.')
        return
    try:
        if truncate:
            db.session.query(model).delete()
        db.session.bulk_insert_mappings(model, df.to_dict(orient='records'))
        db.session.commit()
    except Exception as e:
        raise RuntimeError(f'Erro ao inserir dados em {model.__tablename__}: {e}')


def run_load_data() -> None:
    '''
    Executa as consultas, converte os resultados para DataFrames
    e persiste os dados em formato pickle e no banco de dados.
    '''
    logger.info('Executando extração de dados')

    mysql_db_infra_am_conn = None
    try:
        logger.info('Iniciando conexão com base do MySQL')
        with SSHTunnelForwarder(
            (SSH_HOST, 3128),
            ssh_username=SSH_USER,
            ssh_password=SSH_PASSWORD,
            remote_bind_address=(MYSQL_DB_HOST, MYSQL_DB_PORT),
            local_bind_address=('127.0.0.1', MYSQL_LOCAL_PORT_TUNNEL)
        ):
            mysql_db_infra_am_conn = pymysql.connect(
                host='127.0.0.1',
                port=MYSQL_LOCAL_PORT_TUNNEL,
                database=MYSQL_DB_NAME_1,
                user=MYSQL_DB_USER,
                password=MYSQL_DB_PASSWORD
            )

            logger.info('Extraindo dados de fontes e baterias')
            df_fontes = pd.read_sql(MYSQL_SQL_QUERY_1, mysql_db_infra_am_conn)
            df_idade_bateria = pd.read_sql(MYSQL_SQL_QUERY_2, mysql_db_infra_am_conn)
            df_autonomia_inventario = pd.read_sql(MYSQL_SQL_QUERY_3, mysql_db_infra_am_conn)
            df_geradores = pd.read_sql(MYSQL_SQL_QUERY_4, mysql_db_infra_am_conn)

            df_idade_bateria['data_fabricacao'] = pd.to_datetime(
                df_idade_bateria['data_fabricacao'], errors='coerce'
            )
            df_idade_bateria['data_instalacao'] = pd.to_datetime(
                df_idade_bateria['data_instalacao'], errors='coerce'
            )

            df_fontes.to_pickle('data/raw/fontes.pkl')
            df_idade_bateria.to_pickle('data/raw/idade_bateria.pkl')
            df_geradores.to_pickle('data/raw/geradores.pkl')

    except Exception as e:
        logger.error(f'Erro ao extrair dados do MySQL: {e}')
        raise Exception(f'Erro ao extrair dados do MySQL: {e}')

    finally:
        if mysql_db_infra_am_conn:
            mysql_db_infra_am_conn.close()
            logger.info('Conexão MySQL encerrada')

    pg_db_smartplan_conn = None
    pg_db_qliksense_conn = None
    try:
        logger.info('Iniciando conexão com bases do PostgreSQL')
        with SSHTunnelForwarder(
            (SSH_HOST, 3128),
            ssh_username=SSH_USER,
            ssh_password=SSH_PASSWORD,
            remote_bind_address=(PG_DB_HOST, PG_DB_PORT),
            local_bind_address=('127.0.0.1', PG_LOCAL_PORT_TUNNEL)
        ):
            logger.info('Extraindo dados de estações')
            pg_db_smartplan_conn = psycopg2.connect(
                host='127.0.0.1',
                port=PG_LOCAL_PORT_TUNNEL,
                database=PG_DB_NAME_1,
                user=PG_DB_USER,
                password=PG_DB_PASSWORD
            )
            df_estacoes = pd.read_sql(PG_SQL_QUERY_1, pg_db_smartplan_conn)
            df_estacoes.to_pickle('data/raw/estacoes.pkl')

            logger.info('Extraindo dados de incidentes')
            pg_db_qliksense_conn = psycopg2.connect(
                host='127.0.0.1',
                port=PG_LOCAL_PORT_TUNNEL,
                database=PG_DB_NAME_2,
                user=PG_DB_USER,
                password=PG_DB_PASSWORD
            )
            df_indisponibilidade = pd.read_sql(PG_SQL_QUERY_2, pg_db_qliksense_conn)
            df_alarmes = pd.read_sql(PG_SQL_QUERY_3, pg_db_qliksense_conn)
            df_disponibilidade = pd.read_sql(PG_SQL_QUERY_4, pg_db_qliksense_conn)

            df_indisponibilidade.to_pickle('data/raw/indisponibilidade.pkl')
            df_alarmes.to_pickle('data/raw/alarmes.pkl')
            df_disponibilidade.to_pickle('data/raw/disponibilidade.pkl')
    except Exception as e:
        logger.error(f'Erro ao extrair dados do PostgreSQL: {e}')
        raise Exception(f'Erro ao extrair dados do PostgreSQL: {e}')
    finally:
        if pg_db_smartplan_conn:
            pg_db_smartplan_conn.close()
        if pg_db_qliksense_conn:
            pg_db_qliksense_conn.close()
        logger.info('Conexões PostgreSQL encerradas')
        
    try:
        logger.info('Persistindo tabelas no banco de dados')

        insert_data(df=df_estacoes[['estacao', 'cluster', 'uf', 'municipio', 'ibge', 'latitude', 'longitude']], model=Estacoes)
        insert_data(df=df_disponibilidade, model=Disponibilidade)
        insert_data(df=df_autonomia_inventario, model=AutonomiaInventario)

        logger.info('Tabelas persistidas com sucesso')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Erro ao persistir tabelas no banco de dados: {e}')
        raise

    logger.info('Extração de dados councluída com sucesso')


def run_feature_engineering() -> None:
    '''
    Executa o pipeline de engenharia de features e persiste os resultados no banco de dados.
    
    Returns:
        dict: Dicionário contendo lista de dicionários com as pontuações calculadas e features consolidadas.
    '''
    logger.info('Executando engenharia de features')

    tasks = [
        ('get_autonomia_restabelecimento', run_autonomia_restabelecimento),
        ('get_fontes', run_fontes),
        ('get_pontuacao_autonomia', run_pontuacao_autonomia),
        ('get_pontuacao_cliente', run_pontuacao_cliente),
        ('get_pontuacao_hierarquia', run_pontuacao_hierarquia),
        ('get_pontuacao_idade_bateria', run_pontuacao_idade_bateria),
        ('get_pontuacao_tmr', run_pontuacao_tmr),
        ('get_pontuacao_trafego_faturamento', run_pontuacao_trafego_faturamento)
    ]

    for name, task in tasks:
        logger.info(f'Executando script: {name}')
        try:
            if name == 'get_autonomia_restabelecimento':
                df_autonomia_restabelecimento, df_indisponibilidades = task()
            elif name == 'get_pontuacao_trafego_faturamento':
                df_trafego_faturamento = task()
            else:
                task()
        except Exception as e:
            logger.error(f'Falha ao executar {name}: {e}')
            raise Exception(f'Falha ao executar {name}: {e}')
    logger.info('Consolidando features')
    try:
        df_pontuacoes, df_features = run_features()
    except Exception as e:
        logger.error(f'Falha ao consolidar features: {e}')
        raise Exception(f'Falha ao consolidar features: {e}')
    try:
        logger.info('Persistindo tabelas no banco de dados')

        insert_data(df=df_autonomia_restabelecimento, model=AutonomiaRestabelecimento)
        insert_data(df=df_indisponibilidades, model=Indisponibilidades)
        insert_data(df=df_trafego_faturamento, model=TrafegoFaturamento)
        insert_data(df=df_pontuacoes, model=Pontuacoes)
        insert_data(df=df_features, model=Features)
        
        logger.info('Engenharia de features concluída com sucesso')
        return {
            'scores': df_pontuacoes.to_dict(orient='records'),
            'features': df_features.to_dict(orient='records')
        }
    
    except Exception as e:
        db.session.rollback()
        logger.error(f'Falha ao persistir tabelas no banco de dados: {e}')
        raise Exception(f'Falha ao persistir tabelas no banco de dados: {e}')


def get_tipo_bateria(pontuacao_hierarquia: float) -> str:
    '''
    Retorna o tipo de bateria com base na hierarquia.

    Args:
        pontuacao_hierarquia (float): Pontuação de hierarquia da estação.

    Returns:
        str: Tipo da bateria.
    '''
    if pontuacao_hierarquia == 90:
        return 'SELADA (VRLA) 12V'
    elif pontuacao_hierarquia == 100:
        return 'VENTILADA 2V'
    else:
        return 'LITIO 48V'


def run_training_data(config: dict = None) -> list:
    '''
    Executa o motor de alocação de baterias.

    Args:
        config (dict, optional): Dicionário contendo custo e capacidade de baterias 
        e orçamento disponível para alocação.

    Returns:
        list: Lista de dicionários com as alocações realizadas.
    '''
    logger.info('Executando motor de alocação de baterias')

    #default
    config = config or {}
    baterias = config.get('baterias', {
        'SELADA (VRLA) 12V': {'tipo_bateria': 'SELADA (VRLA)', 'tensao': 12, 'capacidade': 200, 'custo':  8575.12},
        'VENTILADA 2V': {'tipo_bateria': 'VENTILADA', 'tensao': 2, 'capacidade': 2000, 'custo': 141319.33},
        'LITIO 48V': {'tipo_bateria': 'LITIO', 'tensao': 48, 'capacidade': 100, 'custo':  8383.20},
    })
    investimento = config.get('investimento', 1000000) #capex de 2026: 93.634.178,16

    try:
        features = db.session.query(Features).statement
        indisponibilidades = db.session.query(Indisponibilidades).statement
        
        df_features = pd.read_sql(features, db.engine)
        df_indisponibilidades = pd.read_sql(indisponibilidades, db.engine)

        q75 = np.quantile(df_features['pontuacao'].dropna(), 0.75)
        
        df = df_features[df_features['pontuacao'] >= q75].copy() #apenas o terceiro quartil

        #dados da bateria
        df['bateria'] = df['pontuacao_hierarquia'].apply(get_tipo_bateria)
        df['tipo_bateria'] = df['bateria'].apply(lambda x: baterias[x]['tipo_bateria'])
        df['tensao'] = df['bateria'].apply(lambda x: baterias[x]['tensao'])
        df['capacidade'] = df['bateria'].apply(lambda x: baterias[x]['capacidade'])
        df['custo'] = df['bateria'].apply(lambda x: baterias[x]['custo'])

    except Exception as e:
        logger.error(f'Falha ao transformar dados para alocações: {e}')
        raise Exception(f'Falha ao transformar dados para alocações: {e}')

    try:
        df_alocacoes = run_allocation_engine(df, df_indisponibilidades, investimento)
        df_alocacoes['ganho_acumulado'] = df_alocacoes['ganho'].cumsum()
        df_alocacoes['custo_acumulado'] = df_alocacoes['custo'].cumsum()
        df_alocacoes['ganho_por_milhao_investido'] = df_alocacoes['ganho_acumulado'] * 1e6 / df_alocacoes['custo_acumulado']

    except Exception as e:
        logger.error(f'Falha ao executar motor de alocações: {e}')
        raise Exception(f'Falha ao executar motor de alocações: {e}')
    
    try:
        logger.info('Persistindo alocações no banco de dados')

        df_alocacoes.to_pickle('data/aggregated/alocacoes.pkl')
        insert_data(df_alocacoes, Alocacoes)

        logger.info('Alocações concluídas com sucesso')
        
        return df_alocacoes.to_dict(orient='records')
    
    except Exception as e:
        db.session.rollback()
        logger.error(f'Falha ao persistir alocações: {e}')
        raise Exception(f'Falha ao persistir alocações: {e}')