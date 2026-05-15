import streamlit as st
import pandas as pd
from services.api_client import (
    get_estacoes, 
    get_pontuacoes,
    get_alocacoes,
    get_autonomia_restabelecimento,
    get_autonomia_inventario,
    get_disponibilidade,
    get_trafego_faturamento
)
from data.loaders import (
    get_historico_autonomia_restabelecimento
)


@st.cache_data(ttl=3000, show_spinner=False)
def executivo():
    '''
    Consolida dados para visão executiva.

    Returns:
        tuple: (df consolidado, df disponibilidade)
    '''
    df_estacoes = pd.DataFrame(get_estacoes())
    df_alocacoes = pd.DataFrame(get_alocacoes())
    df_disponibilidade = pd.DataFrame(get_disponibilidade())
    df_trafego_faturamento = pd.DataFrame(get_trafego_faturamento())

    df = (
        df_estacoes[['estacao', 'cluster', 'latitude', 'longitude']]
        .merge(df_alocacoes, on='estacao', how='inner')
        .merge(df_trafego_faturamento[['estacao', 'trafego_dados_ewma', 'faturamento_ewma']], on='estacao', how='inner')
    )
    df = df.sort_values('id')

    df_disponibilidade = df_disponibilidade[['estacao', 'ano', 'disponibilidade', 'indisponibilidade_horas', 'indisponibilidade_energia_horas']]

    return df, df_disponibilidade


@st.cache_data(ttl=3000, show_spinner=False)
def gerenciador():
    '''
    Consolida dados para visão gerencial.

    Returns:
        tuple: (df consolidado, df autonomia inventário)
    '''
    df_estacoes = pd.DataFrame(get_estacoes())
    df_pontuacoes = pd.DataFrame(get_pontuacoes())
    df_autonomia_restabelecimento = pd.DataFrame(get_autonomia_restabelecimento())
    df_autonomia_inventario = pd.DataFrame(get_autonomia_inventario())

    df = df_estacoes.merge(df_pontuacoes[['estacao', 'pontuacao_hierarquia', 'pontuacao']], on='estacao', how='inner')
    df = df.merge(df_autonomia_restabelecimento[['estacao', 'autonomia_media_horas', 'restabelecimento_medio_horas']], on='estacao', how='inner')

    numeric_cols = [
        'autonomia_media_horas',
        'restabelecimento_medio_horas',
        'pontuacao_hierarquia',
        'pontuacao',
        'latitude',
        'longitude'
    ]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)
    df['delta'] = df['autonomia_media_horas'] - df['restabelecimento_medio_horas']

    return df, df_autonomia_inventario


@st.cache_data(ttl=3000, show_spinner=False)
def otimizador():
    '''
    Consolida dados para visão de otimização.

    Returns:
        pd.DataFrame: DataFrame final com dados de alocação.
    '''
    df_estacoes = pd.DataFrame(get_estacoes())
    df_autonomia_restabelecimento = pd.DataFrame(get_autonomia_restabelecimento())
    df_pontuacoes = pd.DataFrame(get_pontuacoes())
    df_alocacoes = pd.DataFrame(get_alocacoes())

    df = df_alocacoes.merge(df_estacoes[['estacao', 'cluster', 'latitude', 'longitude']], on='estacao', how='inner')
    df = df.merge(df_autonomia_restabelecimento[['estacao', 'autonomia_media_horas', 'restabelecimento_medio_horas']], on='estacao', how='inner')
    df = df.merge(df_pontuacoes[['estacao', 'pontuacao_hierarquia']], on='estacao', how='inner')

    df['tipologia'] = df['pontuacao_hierarquia'].map(MAPA_TIPOLOGIA)
    df = df.sort_values('id')

    return df


MAPA_TIPOLOGIA = {
    100: '100 - Centrais, BSC e RNC remotas e GPON',
    90: '90 - Com roteadores IPRAN ou repetidores MW >= 20 sites',
    80: '80 - Concentradoras com repetidores MW < 20 sites',
    70: '70 - Estratégicas e monosites',
    60: '60 - Ponta ou repetidores RF'
}