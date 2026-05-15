from typing import Tuple
import pandas as pd
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
def load_data():
    '''
    Consolida dados para visão operacional.

    Returns:
        tuple: (df consolidado, df disponibilidade)
    '''
    df_estacoes = pd.DataFrame(get_estacoes())
    df_autonomia_restabelecimento = pd.DataFrame(get_autonomia_restabelecimento())
    df_autonomia_restabelecimento_2023, df_autonomia_restabelecimento_2024, df_autonomia_restabelecimento_2025 = pd.DataFrame(get_historico_autonomia_restabelecimento())
    gdf_autonomia_inventario = pd.DataFrame(get_autonomia_inventario())
    df_pontuacoes = pd.DataFrame(get_pontuacoes())
    df_disponibilidade = pd.DataFrame(get_disponibilidade())



def label_autonomia_restabelecimento(time: float) -> str:
    '''
    Atribui um rótulo com base em faixas.

    Args:
        time (float): Valor numérico representando o tempo em horas.

    Raises:
        Exception: Caso ocorra um erro inesperado no processamento do valor.
    '''
    if time <= 1:
        rotulo = '0-1h'
    elif time <= 2:
        rotulo = '1-2h'
    elif time <= 3:
        rotulo = '2-3h'
    elif time <= 4:
        rotulo = '3-4h'
    elif time > 4:
        rotulo = '>4h'
    else:
        rotulo = 'Sem dados de incidentes'
    return rotulo


def label_eficiencia_autonomia(autonomia: float, restabelecimento: float, tipologia: str) -> str:
    '''
    Calcula a eficiência (autonomia - restabelecimento) e atribui um rótulo 
    com base em faixas e tipologias.

    Args:
        autonomia (float): Valor de autonomia em horas.
        restabelecimento (float): Valor de restabelecimento em horas.
        tipologia (str): Descrição da tipologia da estação.

    Raises:
        Exception: Caso ocorra um erro no cálculo aritmético ou na comparação.
    '''
    delta = autonomia - restabelecimento
    EXCEPTION_TOPOLOGIES = ['Concentradores', 'GPON', 'RQUAL/Monosites', 'Sites de Ponta Estratégicos']
    if delta < 0:
        rotulo = 'Insuficiente'
    elif 0 <= delta <= 4 or tipologia in EXCEPTION_TOPOLOGIES:
        return 'Suficiente'
    elif delta > 4:
        rotulo = 'Excedente'
    else:
        rotulo = 'Sem dados de incidentes'
    return rotulo


def transform(
        df_autonomia_restabelecimento: pd.DataFrame,
        df_autonomia_inventario: pd.DataFrame,
        df_otimizador_de_baterias: pd.DataFrame, 
        df_scores: pd.DataFrame,
        df_estacoes: pd.DataFrame, 
        df_disponibilidade: pd.DataFrame,
        df_autonomia_restabelecimento_2023: pd.DataFrame, 
        df_autonomia_restabelecimento_2024: pd.DataFrame, 
        df_autonomia_restabelecimento_2025: pd.DataFrame,
        df_tipologia_estacoes: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    '''
    Realiza a transformação, limpeza, categorização e junção de dados de diversas fontes.

    Args:
        df_autonomia_restabelecimento (pd.DataFrame): Dados atuais (2026).
        df_autonomia_inventario (pd.DataFrame): Dados de inventário de autonomia.
        df_otimizador_de_baterias (pd.DataFrame): Dados do otimizador.
        df_scores (pd.DataFrame): Dados de pontuação (scores).
        df_estacoes (pd.DataFrame): Cadastro de estações.
        df_disponibilidade (pd.DataFrame): Dados de disponibilidade histórica.
        df_autonomia_restabelecimento_2023 (pd.DataFrame): Dados de 2023.
        df_autonomia_restabelecimento_2024 (pd.DataFrame): Dados de 2024.
        df_autonomia_restabelecimento_2025 (pd.DataFrame): Dados de 2025.
        df_coordenadas_uf (pd.DataFrame): Latitude e longitude por UF.
    '''
    #tratando df
    #concatenando dataframes
    df_autonomia_restabelecimento_2023['ano'] = '2023'
    df_autonomia_restabelecimento_2024['ano'] = '2024'
    df_autonomia_restabelecimento_2025['ano'] = '2025'
    df_autonomia_restabelecimento['ano'] = '2026'
    df_autonomia_restabelecimento = pd.concat([df_autonomia_restabelecimento_2023, df_autonomia_restabelecimento_2024, df_autonomia_restabelecimento_2025, df_autonomia_restabelecimento])
    df_autonomia_restabelecimento = df_autonomia_restabelecimento[['ano', 'estacao', 'autonomia_media_horas', 'restabelecimento_medio_horas', 'tipo_autonomia']]
    #excluindo registros sem dados de incidentes
    df_autonomia_restabelecimento = df_autonomia_restabelecimento.dropna(subset='autonomia_media_horas')
    #categorizando autonomia
    df_autonomia_restabelecimento['rotulo_autonomia_media_horas'] = df_autonomia_restabelecimento['autonomia_media_horas'].apply(label_autonomia_restabelecimento)
    #categorizando restabelecimento
    df_autonomia_restabelecimento['rotulo_restabelecimento_medio_horas'] = df_autonomia_restabelecimento['restabelecimento_medio_horas'].apply(label_autonomia_restabelecimento)
    
    #mesclando dados
    df_temp = df_temp.merge(df_autonomia_inventario, on='estacao', how='left')
    df_temp = df_temp.drop_duplicates(subset=['estacao'])
    df_autonomia_restabelecimento = df_autonomia_restabelecimento.merge(df_temp, on='estacao', how='left')
    df_autonomia_restabelecimento['tipologia'] = df_autonomia_restabelecimento['tipologia'].fillna('Tipologia não informada') #substituindo valores nulos
    #categorizando eficiencia de autonomia
    df_autonomia_restabelecimento['rotulo_eficiencia_media_horas'] = df_autonomia_restabelecimento.apply(lambda x: label_eficiencia_autonomia(x['autonomia_media_horas'], x['restabelecimento_medio_horas'], x['tipologia']), axis=1)
    #obtendo delta
    df_autonomia_restabelecimento['delta'] = df_autonomia_restabelecimento['autonomia_media_horas'] - df_autonomia_restabelecimento['restabelecimento_medio_horas'] 
    #ordenando dataframe
    df_autonomia_restabelecimento = df_autonomia_restabelecimento.sort_values('restabelecimento_medio_horas')
    #filtrando dataframe
    df_autonomia_restabelecimento = df_autonomia_restabelecimento.merge(df_disponibilidade, on=['ano', 'estacao'], how='left')
    #df_otimizador_de_baterias
    #mesclando dados
    columns = [
        'estacao', 'tipologia', 'cluster', 'uf', 'estado', 'municipio', 'latitude_estacao', 'longitude_estacao',
        'autonomia_media_horas', 'restabelecimento_medio_horas', 'autonomia_inventario_horas', 'delta', 'tipo_autonomia'
    ]
    df_temp = df_autonomia_restabelecimento[df_autonomia_restabelecimento['ano'] == '2026'][columns]
    df_otimizador_de_baterias = df_otimizador_de_baterias.merge(df_temp, on='estacao', how='left')
    df_otimizador_de_baterias = df_otimizador_de_baterias.merge(df_scores, on='estacao', how='left')
    df_scores = df_scores.merge(df_temp, on='estacao', how='left')

    return df_autonomia_restabelecimento, df_otimizador_de_baterias, df_scores