import logging
import pandas as pd


logger = logging.getLogger(__name__)


def run_fontes() -> None:
    '''
    Processa os dados de fontes de energia e calcula a carga consolidada por 
    estação, persistindo o resultado em um arquivo pickle.
    '''
    df = pd.read_pickle('data/raw/fontes.pkl')
    
    df = df[df['carga'] >= 0]
    df = df.groupby('estacao', as_index=False).agg(carga=('carga', 'sum'))
    
    df.to_pickle('data/aggregated/fontes.pkl')