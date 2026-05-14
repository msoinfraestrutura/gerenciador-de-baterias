import logging
from typing import Optional
import pandas as pd


logger = logging.getLogger(__name__)


def get_pontuacao_autonomia(row: pd.Series) -> Optional[int]:
    '''
    Calcula o pontuação de autonomia com base na comparação entre a autonomia 
    média e o tempo médio de restabelecimento.

    Args:
        row (pd.Series): Linha do DataFrame contendo a autonomia media
        e tempo de restabelecimento médio em horas

    Returns:
        Optional[int]: Pontuação atribuída.
    '''
    #excedente
    epsilon = 4
    if row['autonomia_media_horas'] > row['restabelecimento_medio_horas'] + epsilon:
        return 1
    #suficiente: autonomia é maior ou igual o restabelecimento mas não excede em 4 horas
    elif row['autonomia_media_horas'] >= row['restabelecimento_medio_horas']:
        return 3
    #sem autonomia: autonomia é 0 ou autonomia é menor que o restabelecimento
    elif row['autonomia_media_horas'] == 0 or row['autonomia_media_horas'] < row['restabelecimento_medio_horas']:
        return 5
    return None


def run_pontuacao_autonomia() -> None:
    '''
    Executa o pipeline de cálculo da pontuação de autonomia das estações, persistindo 
    o resultado em um arquivo pickle.
    '''
    df = pd.read_pickle('data/aggregated/autonomia_restabelecimento.pkl')
    
    df['pontuacao_autonomia'] = df.apply(get_pontuacao_autonomia, axis=1)
    df['pontuacao_autonomia'] = df['pontuacao_autonomia'].fillna(1)
    
    df = df[['estacao', 'pontuacao_autonomia']]
    
    df.to_pickle('data/aggregated/pontuacao_autonomia.pkl')
    

if __name__ == '__main__':
    run_pontuacao_autonomia()