import logging
from typing import Any
import pandas as pd


logger = logging.getLogger(__name__)


def get_pontuacao(row: pd.Series) -> float:
    '''
    Calcula a pontuação final da estação por meio de uma média ponderada
    dos scores individuais, considerando critérios operacionais,
    estratégicos e financeiros.

    Args:
        row (pd.Series): Linha do DataFrame consolidado contendo todos
        os scores individuais da estação.

    Returns:
        float: Valor da pontuação final ponderada da estação.
    '''
    return (
        0.19 * row['pontuacao_autonomia'] + 
        0.03 * row['pontuacao_trafego_dados'] + 
        0.265 * row['pontuacao_hierarquia'] + 
        0.095 * row['pontuacao_tmr'] + 
        0.16 * row['pontuacao_idade_bateria'] + 
        0.12 * row['pontuacao_faturamento'] + 
        0.14 * row['pontuacao_cliente']
    )


def run_features() -> tuple[pd.DataFrame, pd.DataFrame]:
    '''
    Executa o pipeline de consolidação de scores e geração de features
    das estações.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]:
        DataFrame contendo as pontuações finais por estação e
        DataFrame contendo a base consolidada de features utilizada
        em etapas posteriores do modelo.
    '''
    df_pontuacao_autonomia = pd.read_pickle(f'data/aggregated/pontuacao_autonomia.pkl')
    df_pontuacao_trafego_faturamento = pd.read_pickle(f'data/aggregated/pontuacao_trafego_faturamento.pkl')
    df_pontuacao_hierarquia = pd.read_pickle(f'data/aggregated/pontuacao_hierarquia.pkl')
    df_pontuacao_tmr = pd.read_pickle(f'data/aggregated/pontuacao_tmr.pkl')
    df_pontuacao_idade_bateria = pd.read_pickle(f'data/aggregated/pontuacao_idade_bateria.pkl')
    df_pontuacao_cliente = pd.read_pickle(f'data/aggregated/pontuacao_cliente.pkl')
    df_fontes = pd.read_pickle(f'data/aggregated/fontes.pkl')
    #df_autonomia_projetada = pd.read_pickle(f'data/aggregated/autonomia_projetada.pkl')

    df = df_pontuacao_hierarquia.merge(df_pontuacao_idade_bateria, on='estacao', how='left')
    df = df.merge(df_pontuacao_tmr, on='estacao', how='left')
    df = df.merge(df_pontuacao_cliente, on='estacao', how='left')
    df = df.merge(df_pontuacao_trafego_faturamento, on='estacao', how='left')
    df = df.merge(df_pontuacao_autonomia, on='estacao', how='left')
    #df = df.merge(df_autonomia_projetada, on='estacao', how='left')

    fill_values: dict[str, Any] = {
        'pontuacao_tmr': 1, 
        'pontuacao_hierarquia': 60, 
        'pontuacao_cliente': 1,
        'pontuacao_idade_bateria': 5, 
        'pontuacao_trafego_dados': 3,
        'pontuacao_faturamento': 3, 
        'pontuacao_autonomia': 1, 
        'autonomia_projetada': 4
    }
    df = df.fillna(value=fill_values)
    df['pontuacao'] = df.apply(get_pontuacao, axis=1)

    df_pontuacoes = df.groupby('estacao', as_index=False).agg({
        'pontuacao_autonomia': 'first', 'pontuacao_trafego_dados': 'first',
        'pontuacao_hierarquia': 'first', 'pontuacao_tmr': 'first',
        'pontuacao_idade_bateria': 'max', 'pontuacao_faturamento': 'first',
        'pontuacao_cliente': 'first', 'pontuacao': 'max'
    })
    df_pontuacoes.to_pickle(f'data/aggregated/pontuacoes.pkl')

    df_features = df.merge(df_fontes, on='estacao', how='left')
    df_features['capacidade'] = df_features['capacidade'].astype(float)

    df_features = df_features.groupby('estacao', as_index=False).agg(
        carga=('carga', 'first'),
        pontuacao_hierarquia=('pontuacao_hierarquia', 'first'),
        pontuacao=('pontuacao', 'first'),
        autonomia_projetada=('autonomia_projetada', 'first'),
    )
    df_features['carga'] = df_features['carga'].fillna(df_features['carga'].median())
    df_features['carga'] = df_features['carga'].replace(0, df_features['carga'].median())
    df_features = df_features[df_features['autonomia_projetada'] > 0]
    
    df_features.to_pickle(f'data/aggregated/features.pkl')

    return df_pontuacoes, df_features


if __name__ == '__main__':
    run_features()