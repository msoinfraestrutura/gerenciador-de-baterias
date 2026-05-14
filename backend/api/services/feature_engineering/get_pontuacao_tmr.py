import logging
from typing import Optional
import pandas as pd


logger = logging.getLogger(__name__)


def get_pontuacao_tmr(row: Optional[float], q1: float, q3: float) -> Optional[int]:
    '''
    Calcula o pontuação de TMR com base nos quartis de distribuição.

    Args:
        row (Optional[float]): Valor do MTTR para uma estação.
        q1 (float): Limite do primeiro quartil.
        q3 (float): Limite do terceiro quartil.

    Returns:
        Optional[int]: Pontuação atribuída ou None se o valor for inválido.
    '''
    if row is not None:
        if row < q1:
            return 1
        elif row < q3:
            return 3
        elif row >= q3:
            return 5
    return None


def run_pontuacao_tmr() -> None:
    '''
    Executa o pipeline de cálculo da pontuação do TMR, persistindo
    o resultado em um arquivo pickle.
    '''
    df = pd.read_pickle('data/raw/indisponibilidade.pkl')
    
    df['mttr'] = df['mttr'].abs() / 3600
    
    df = df.rename(columns={'site_ci': 'estacao'})
    df = df.groupby('estacao', as_index=False)['mttr'].mean()
    
    q1 = df['mttr'].quantile(0.25)
    q3 = df['mttr'].quantile(0.75)
    
    df['pontuacao_tmr'] = df['mttr'].apply(lambda x: get_pontuacao_tmr(x, q1, q3))
    df = df.dropna(how='any')
    
    df = df[['estacao', 'pontuacao_tmr']]
    
    df.to_pickle('data/aggregated/pontuacao_tmr.pkl')
    

if __name__ == '__main__':
    run_pontuacao_tmr()