import logging
import pandas as pd
from unidecode import unidecode


logger = logging.getLogger(__name__)


def get_pontuacao_cliente(row: pd.Series) -> int:
    '''
    Calcula a pontuação do cliente.
    
    Uma estação recebe pontuacao 5 se a referência da estação for um local como ('aeroporto',
    'shopping', 'estadio', 'lojas proprias', etc). O pontuacao é 3 se houver finalidade 
    residencial ou empresarial. Por fim, qualquer estação que não se enquadre nas regras 5 
    ou 3 recebe pontuacao 1.

    Args:
        row (pd.Series): Linha do DataFrame contendo as informações da estação.

    Returns:
        int: Pontuação atribuída.
    '''
    finalidade_movel = row['finalidade_movel']
    nome_ref_estacao = row['nome_ref_estacao']
    finalidade_empresarial = row['finalidade_empresarial']
    finalidade_residencial = row['finalidade_residencial']
    
    keys_ref_estacao = [
        'estadio', 'eventos', 'cliente corporativo', 'lojas proprias', 
        'aeroporto', 'shopping', 'centro de convencoes', 'loja claro', 'rodoviaria'
    ]
    
    #regra 1: pontuacao 5
    is_estacao_vip = any(keyword in nome_ref_estacao for keyword in keys_ref_estacao)
    if is_estacao_vip:
        return 5
    
    #regra 2: pontuacao 3 (Se não caiu na Regra 1)
    is_empresarial_filled = finalidade_empresarial not in ('nan', '')
    is_residencial_filled = finalidade_residencial not in ('nan', '')
    
    if is_empresarial_filled or is_residencial_filled:
        return 3
    
    #regra 3: pontuacao 1 (se não caiu nas Regras 1 ou 2)
    return 1


def run_pontuacao_cliente() -> None:
    '''
    Executa o pipeline de cálculo da pontuação de cliente das estações, persistindo 
    o resultado em um arquivo pickle.
    '''
    df: pd.DataFrame = pd.read_pickle('data/raw/hierarquia_cliente.pkl')
    
    df = df.dropna(subset=['finalidade_movel', 'finalidade_empresarial', 'finalidade_residencial'], how='all')
    
    cols_to_normalize = ['nome_ref_estacao', 'finalidade_movel', 'finalidade_empresarial', 'finalidade_residencial']
    for col in cols_to_normalize:
        df[col] = df[col].astype(str).str.lower().apply(unidecode)
        
    df['pontuacao_cliente'] = df.apply(get_pontuacao_cliente, axis=1)
    
    df_result: pd.DataFrame = df[['estacao', 'pontuacao_cliente']]
    df_result.to_pickle('data/aggregated/pontuacao_cliente.pkl')


if __name__ == '__main__':
    run_pontuacao_cliente()