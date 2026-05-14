import logging
from typing import Optional
import pandas as pd


logger = logging.getLogger(__name__)


def get_ewma(df: pd.DataFrame, col: str, alpha: float = 0.1) -> pd.DataFrame:
    '''
    Calcula a EWMA (Média Móvel Exponencialmente Ponderada) da coluna especificada
    para cada estação, ordenada por mês.

    Args:
        df (pd.DataFrame): DataFrame contendo os dados de tráfego/faturamento.
        col (str): Nome da coluna para realizar o cálculo da média.
        alpha (float): Parâmetro de suavização (0 < alpha <= 1).

    Returns:
        pd.DataFrame: DataFrame original com a coluna de média móvel adicionada.
    '''
    df = df.sort_values(['estacao', 'mes'])
    df[f'{col} EWMA'] = df.groupby('estacao', group_keys=False)[col].apply(
        lambda x: x.ewm(alpha=alpha, adjust=False).mean()
    )
    return df


def get_pontuacao(row: float, q1: float, q3: float) -> Optional[int]:
    '''
    Calcula o pontuação de uma métrica baseado nos quartis de distribuição.

    Args:
        row (float): Valor da métrica a ser pontuada.
        q1 (float): Valor do primeiro quartil (limite inferior).
        q3 (float): Valor do terceiro quartil (limite superior).

    Returns:
        Optional[int]: Pontuação atribuída ou None se o valor for nulo.
    '''
    if pd.isna(row):
        return None
    if row < q1:
        return 1
    elif row < q3:
        return 3
    else:
        return 5


def run_pontuacao_trafego_faturamento() -> pd.DataFrame:
    '''
    Executa o pipeline de cálculo das pontuações de tráfego e faturamento, persistindo
    o resultado em um arquivo pickle.
    '''
    #leitura e concatenação
    xls = pd.ExcelFile('data/raw/trafego_faturamento.xlsx')
    df_list = [pd.read_excel('data/raw/trafego_faturamento.xlsx', sheet_name=s).assign(sheet_name=s) for s in xls.sheet_names]
    df = pd.concat(df_list, ignore_index=True)

    #preparação de datas
    d = {name: i for i, name in enumerate(xls.sheet_names)}
    df['mes'] = df['sheet_name'].map(d)
    df.rename(columns={'Site ': 'estacao'}, inplace=True)
    df['estacao'] = df['estacao'].str.strip()

    #cálculos de tendência (EWMA)
    df = get_ewma(df, 'Trafego Dados')
    df = get_ewma(df, 'Receita Total')
    
    #filtragem para o mês mais recente (assumindo o último índice)
    df = df.groupby('estacao', as_index=False).last()

    #cálculo dos quartis e pontuacaos
    q1_dados, q3_dados = df['Trafego Dados EWMA'].quantile([0.25, 0.75])
    q1_fat, q3_fat = df['Receita Total EWMA'].quantile([0.25, 0.75])

    df['pontuacao_trafego_dados'] = df['Trafego Dados EWMA'].apply(lambda x: get_pontuacao(x, q1_dados, q3_dados))
    df['pontuacao_faturamento'] = df['Receita Total EWMA'].apply(lambda x: get_pontuacao(x, q1_fat, q3_fat))

    df[['estacao', 'pontuacao_faturamento', 'pontuacao_trafego_dados']].to_pickle('data/aggregated/pontuacao_trafego_faturamento.pkl')
    
    df = df[['estacao', 'Trafego Dados EWMA', 'Receita Total EWMA']]
    df = df.rename(columns={'Trafego Dados EWMA': 'trafego_dados_ewma', 'Receita Total EWMA': 'faturamento_ewma'})
    
    return df


if __name__ == '__main__':
    run_pontuacao_trafego_faturamento()