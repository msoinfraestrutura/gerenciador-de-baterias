import logging
from typing import Optional
import pandas as pd


logger = logging.getLogger(__name__)


def get_pontuacao_hierarquia(row: str) -> Optional[int]:
    '''
    Calcula o pontuação de hierarquia com base na severidade.

    Args:
        row (str): A severidade da estação (ex: '02 - LEVE').

    Returns:
        Optional[int]: Pontuação atribuída ou None se não encontrado.
    '''
    if row == '02 - LEVE': #Estações de ponta ou repetidores RF
        return 60
    elif row == '04 - MODERADO': #Estações estratégicas e Monosites
        return 70
    elif row == '08 - SEVERO': #Estações concentradores com repetidores MW<20sites
        return 80
    elif row == '16 - CRITICO': #Estações com roteadores IpRAN ou com repetidores MW>=20 sites
        return 90
    elif row == '32 - MUITO CRITICO': #Predios de centrais, BSC e RNC Remotas e GPON
        return 100
    else:
        return None


def run_pontuacao_hierarquia() -> None:
    '''
    Executa o pipeline de cálculo da pontuação de hierarquia das estações, persistindo
    o resultado em um arquivo pickle.
    '''
    df = pd.read_pickle('data/raw/estacoes.pkl')
    
    df['pontuacao_hierarquia'] = df['severidade_omr'].apply(get_pontuacao_hierarquia)

    df = df[['estacao', 'pontuacao_hierarquia']]

    df.to_pickle('data/aggregated/pontuacao_hierarquia.pkl')


if __name__ == '__main__':
    run_pontuacao_hierarquia()