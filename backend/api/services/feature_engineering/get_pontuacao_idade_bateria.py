import logging
from datetime import datetime, UTC
from typing import Optional, Any
from dateutil.relativedelta import relativedelta
import pandas as pd


logger = logging.getLogger(__name__)


def get_idade_bateria(row: Any) -> Optional[int]:
    '''
    Calcula a idade da bateria em anos com base na data atual.

    Args:
        row (Any): Data de fabricação da bateria.

    Returns:
        Optional[int]: Idade em anos ou None em caso de erro.
    '''
    now = datetime.now()
    try:
        return relativedelta(now, row).years
    except Exception:
        return None


def clear_idade_bateria(row: Optional[int], cutoff: int=20) -> Optional[int]:
    '''
    Filtra a idade da bateria dentro de um intervalo de corte aceitável.

    Args:
        row (Optional[int]): Idade calculada da bateria.
        cutoff (int): Limite máximo de idade aceitável.

    Returns:
        Optional[int]: Idade filtrada ou None se fora do intervalo.
    '''
    if row is None:
        return None
    elif 0 <= row <= cutoff:
        return row
    else:
        return None


def get_pontuacao_idade_bateria(row: pd.Series) -> Optional[int]:
    '''
    Calcula o pontuação da bateria baseado na tecnologia, tensão e idade.

    Args:
        row (pd.Series): Linha do DataFrame contendo tipo, tensão e idade da bateria.

    Returns:
        Optional[int]: Pontuação atribuída.
    '''
    pontuacao = None
    if row['idade_bateria'] is not None:
        if row['tipo_bateria'] == 'LITIO' and row['idade_bateria'] > 8:
            pontuacao = 5
        elif 'VRLA' in row['tipo_bateria'] and row['tensao'] == '12V' and row['idade_bateria'] > 4:
            pontuacao = 5
        elif 'VRLA' in row['tipo_bateria'] and row['tensao'] == '2V' and row['idade_bateria'] > 5:
            pontuacao = 5
        elif 'VENTILADA' in row['tipo_bateria'] and row['tensao'] == '2V' and row['idade_bateria'] > 12:
            pontuacao = 5
        elif row['idade_bateria'] >= 1:
            pontuacao = 1
        elif row['idade_bateria'] == 0:
            pontuacao = 0
    return pontuacao


def filter_bateria(row: pd.Series) -> bool:
    '''
    Avalia se um registro de bateria deve ser desconsiderado.

    Args:
        row (pd.Series): Linha do DataFrame contendo dados de tensão, quantidade e hierarquia.

    Returns:
        bool: True se o registro deve ser ignorado, False caso contrário.
    '''
    if row['tensao'] == '12V':
        if row['quantidade_total'] > 20:
            if row['pontuacao_hierarquia'] in [60.0, 70.0]:
                return True
            else:
                return False
        else:
            return False
    elif row['tensao'] == '2V':
        if row['quantidade_total'] < 6:
            return True
        elif row['quantidade_total'] % 6 != 0:
            return True
        else:
            return False
    elif row['tensao'] == '48V':
        if row['quantidade_total'] > 10:
            if row['pontuacao_hierarquia'] in [60.0, 70.0]:
                return True
            else:
                return False
        else:
            return False
    elif 'V' in str(row['quantidade']):  
        return True
    else:
        return False


def run_pontuacao_idade_bateria() -> None:
    '''
    Executa o pipeline de cálculo da pontuação de hierarquia da idade das baterias, persistindo
    o resultado em um arquivo pickle.
    '''
    df_idade_bateria: pd.DataFrame = pd.read_pickle('data/raw/idade_bateria.pkl')
    df_hierarquia: pd.DataFrame = pd.read_pickle('data/aggregated/pontuacao_hierarquia.pkl')[['estacao', 'pontuacao_hierarquia']]

    for col in ['data_fabricacao', 'data_instalacao']:
        df_idade_bateria[col] = df_idade_bateria[col].replace('9999-09-09', None)

    df_idade_bateria['idade_bateria'] = df_idade_bateria['data_instalacao'].apply(get_idade_bateria)
    df_idade_bateria['idade_bateria'] = df_idade_bateria['idade_bateria'].apply(clear_idade_bateria)
    df_idade_bateria['pontuacao_idade_bateria'] = df_idade_bateria.apply(get_pontuacao_idade_bateria, axis=1)

    df: pd.DataFrame = df_idade_bateria.merge(df_hierarquia, on='estacao', how='left')
    df['quantidade_total'] = df.groupby('estacao')['quantidade'].transform('sum')
    
    df['desconsiderar'] = df.apply(filter_bateria, axis=1)
    df = df[df['desconsiderar'] == False]

    #exportação
    df[['estacao', 'capacidade', 'pontuacao_idade_bateria']].to_pickle('data/aggregated/pontuacao_idade_bateria.pkl')


if __name__ == '__main__':
    run_pontuacao_idade_bateria()