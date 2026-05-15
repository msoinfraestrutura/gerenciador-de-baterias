import logging
import warnings
from datetime import datetime, timedelta
from typing import Optional, Any
import pandas as pd
import numpy as np
from unidecode import unidecode


logger = logging.getLogger(__name__)
warnings.filterwarnings(action='ignore')


def get_estacao(row: str) -> Optional[str]:
    try:
        return row.split()[1].strip()
    except Exception:
        return None


def get_horas(row: Any) -> Any:
    try:
        return row.total_seconds() / 3600
    except Exception:
        return row


def get_duracao_indisponibilidade(row: pd.Series) -> timedelta:
    return row['clear_date'] - row['submit_date']


def corrige_clear_date(row: pd.Series, cutoff: Any, td: timedelta) -> Any:
    intervalo = row['intervalo']
    if (intervalo >= cutoff) or (intervalo < timedelta(seconds=0)):
        return row['submit_date'] + td
    else:
        return row['clear_date']
    

def transform_indisponibilidade(df_indisponibilidades: pd.DataFrame, ano: int=False) -> pd.DataFrame:
    df = df_indisponibilidades.copy()
    df['generic_categorization_tier_1'] = df['generic_categorization_tier_1'].str.lower().str.strip().apply(unidecode)
    df = df[df['generic_categorization_tier_1'] == 'energia concessionaria']
    df = df[df['filtro_classificacoes_1'] == 'ALARMES SITE INDISPONIVEL']
    df = df[df['estacao'].notna()]
    df = df[df['clear_date'].notna()]
    df = df[df['submit_date'].notna()]
    df = df[df['submit_date'] < df['clear_date']]
    
    df['submit_date'] = pd.to_datetime(df['submit_date'])
    df['clear_date'] = pd.to_datetime(df['clear_date'])
    
    if ano:
        df = df[df['submit_date'].dt.year == ano]

    df['ic'] = df['ic'].apply(get_estacao)
    df['manter'] = df.apply(lambda row: str(row['estacao']) in str(row['ic']), axis=1)
    df = df[df['manter'] == True]
    
    df['intervalo'] = df['clear_date'] - df['submit_date']
    td_clear = df['intervalo'].median()
    cutoff_clear = np.percentile(df['intervalo'], 97) 
    df['clear_date'] = df.apply(lambda row: corrige_clear_date(row, cutoff_clear, td_clear), axis=1)

    df = df.groupby(['incident_number', 'estacao'], as_index=False).agg({
        'submit_date': 'min',
        'clear_date': 'max'
    })
    
    df = df.sort_values(by=['estacao', 'submit_date'], ascending=[True, True])
    df['last_clear'] = df.groupby('estacao')['clear_date'].shift()
    df['is_overlap'] = df.apply(lambda row: True if row['submit_date'] <= row['last_clear'] else False, axis=1) 
    df['group_id'] = (df['is_overlap'] == False).cumsum()
    
    df = df.groupby('group_id', as_index=False).agg({
        'estacao': 'first', 
        'clear_date': 'max', 
        'submit_date': 'min'
    })
    
    df['date'] = df['submit_date'].dt.date
    
    return df


def transform_alarmes(df_alarmes: pd.DataFrame, ano: int=False) -> pd.DataFrame:
    df = df_alarmes.copy()
    df = df[df['categorization_tier_3'] == 'FALHA ENERGIA AC']
    df = df[df['clear_date'].notna()]
    df = df[df['submit_date'].notna()]
    df = df[df['estacao'].notna()]
    
    df['submit_date'] = pd.to_datetime(df['submit_date']) 
    df['clear_date'] = pd.to_datetime(df['clear_date']) 
    df = df[df['submit_date'] < df['clear_date']]
    
    if ano:
        df = df[df['submit_date'].dt.year == ano]
    
    df['intervalo'] = df['clear_date'] - df['submit_date']
    td_clear = df['intervalo'].median()
    cutoff_clear = np.percentile(df['intervalo'], 99) 
    df['clear_date'] = df.apply(lambda row: corrige_clear_date(row, cutoff_clear, td_clear), axis=1)
    
    df = df.sort_values(by=['estacao', 'submit_date'], ascending=[True, True])
    df['last_clear'] = df.groupby('estacao')['clear_date'].shift()
    df['is_overlap'] = df.apply(lambda row: True if row['submit_date'] <= row['last_clear'] else False, axis=1) 
    df['group_id'] = (df['is_overlap'] == False).cumsum()
    
    df = df.groupby('group_id', as_index=False).agg({
        'estacao': 'first', 
        'clear_date': 'max', 
        'submit_date': 'min'
    })

    df['date'] = df['submit_date'].dt.date
    df['tempo_restabelecimento_energia'] = df['clear_date'] - df['submit_date']

    return df


def run_autonomia_restabelecimento() -> None:

    ano_inicial = 2023
    ano_atual = datetime.now().year

    df_estacoes = pd.read_pickle('data/raw/estacoes.pkl')
    df_indisponibilidades = pd.read_pickle('data/raw/indisponibilidade.pkl')
    df_alarmes = pd.read_pickle('data/raw/alarmes.pkl')

    dfs_autonomia_restabelecimento = []
    dfs_indisponibilidades = []

    for ano in range(ano_inicial, ano_atual + 1):

        df_indisponibilidades_temp = df_indisponibilidades.copy()
        df_alarmes_temp = df_alarmes.copy()

        df_indisponibilidades_temp['submit_date'] = pd.to_datetime(df_indisponibilidades_temp['submit_date'])
        df_alarmes_temp['submit_date'] = pd.to_datetime(df_alarmes_temp['submit_date'])

        df_indisponibilidades_temp = df_indisponibilidades_temp[df_indisponibilidades_temp['submit_date'].dt.year <= ano]
        df_alarmes_temp = df_alarmes_temp[df_alarmes_temp['submit_date'].dt.year <= ano]

        df_indisponibilidades_temp = transform_indisponibilidade(df_indisponibilidades_temp, False)
        df_alarmes_temp = transform_alarmes(df_alarmes_temp, False)
        
        df_grouped_indisponibilidades = df_indisponibilidades_temp.groupby(['estacao', 'date'], as_index=False).agg(
            submit_date_indisp=('submit_date', 'min'),
            clear_date_indisp=('clear_date', 'max')
        )

        df_grouped_alarmes = df_alarmes_temp.groupby(['estacao', 'date'], as_index=False).agg(
            submit_date_alarme=('submit_date', 'min'), 
            clear_date_alarme=('clear_date', 'max')
        )

        df_grouped_alarmes = df_grouped_alarmes.sort_values('submit_date_alarme')
        df_grouped_indisponibilidades = df_grouped_indisponibilidades.sort_values('submit_date_indisp')

        temp_df_1 = pd.merge_asof(
            df_grouped_alarmes, 
            df_grouped_indisponibilidades, 
            left_on='submit_date_alarme', 
            right_on='submit_date_indisp',
            by='estacao', 
            tolerance=pd.Timedelta(hours=24),
            direction='forward'
        )

        df_com_impacto = temp_df_1[temp_df_1['submit_date_indisp'].notnull()]
        df_com_impacto = df_com_impacto.assign(
            autonomia=df_com_impacto['submit_date_indisp'] - df_com_impacto['submit_date_alarme']
        )
        df_com_impacto = df_com_impacto.groupby('estacao', as_index=False).agg(
            autonomia_media=('autonomia', 'mean')
        )
        df_com_impacto['tipo_autonomia'] = 'Real'

        df_sem_impacto = temp_df_1[temp_df_1['submit_date_indisp'].isnull()]
        df_sem_impacto = df_sem_impacto.assign(
            autonomia=df_sem_impacto['clear_date_alarme'] - df_sem_impacto['submit_date_alarme']
        )
        df_sem_impacto = df_sem_impacto.groupby('estacao', as_index=False).agg(
            autonomia_media=('autonomia', 'mean')
        )
        df_sem_impacto['tipo_autonomia'] = 'Estimada'

        temp_df_2 = pd.merge_asof(
            df_grouped_indisponibilidades, 
            df_grouped_alarmes, 
            left_on='submit_date_indisp', 
            right_on='submit_date_alarme',
            by='estacao',
            tolerance=pd.Timedelta(hours=24),
            direction='backward'
        )

        df_indisponibilidades_temp_sem_autonomia = temp_df_2[temp_df_2['submit_date_alarme'].isnull()].copy()
        df_indisponibilidades_temp_sem_autonomia['tempo_restabelecimento_energia'] = (
            df_indisponibilidades_temp_sem_autonomia['clear_date_indisp'] - df_indisponibilidades_temp_sem_autonomia['submit_date_indisp']
        )

        lista_estacoes_sem_autonomia = set(df_indisponibilidades_temp_sem_autonomia['estacao'].unique()) \
            - set(df_com_impacto['estacao'].unique()) \
            - set(df_sem_impacto['estacao'].unique())
        
        df_sem_autonomia = pd.DataFrame(lista_estacoes_sem_autonomia, columns=['estacao'])
        df_sem_autonomia['autonomia_media'] = timedelta(0)
        df_sem_autonomia['tipo_autonomia'] = 'Sem autonomia'

        df_restabelecimento_energia = pd.concat([
            df_alarmes_temp[['estacao', 'tempo_restabelecimento_energia']], 
            df_indisponibilidades_temp_sem_autonomia[['estacao', 'tempo_restabelecimento_energia']]
        ]).groupby('estacao', as_index=False).agg(
            tempo_restabelecimento_medio=('tempo_restabelecimento_energia', 'mean')
        )

        df_sem_impacto = df_sem_impacto[
            ~df_sem_impacto['estacao'].isin(df_com_impacto['estacao'].unique())
        ]

        df_autonomia_restabelecimento = pd.concat([df_com_impacto, df_sem_impacto, df_sem_autonomia])

        df_autonomia_restabelecimento = df_estacoes[['estacao']].merge(
            df_autonomia_restabelecimento, how='left', on='estacao'
        )
        df_autonomia_restabelecimento = df_autonomia_restabelecimento.merge(
            df_restabelecimento_energia, on='estacao', how='left'
        )

        df_autonomia_restabelecimento['autonomia_media_horas'] = df_autonomia_restabelecimento['autonomia_media'].apply(get_horas)
        df_autonomia_restabelecimento['restabelecimento_medio_horas'] = df_autonomia_restabelecimento['tempo_restabelecimento_medio'].apply(get_horas)
        df_autonomia_restabelecimento['ano'] = ano
        df_autonomia_restabelecimento = df_autonomia_restabelecimento[
            ['ano', 'estacao', 'autonomia_media_horas', 'restabelecimento_medio_horas', 'tipo_autonomia']
        ]
        dfs_autonomia_restabelecimento.append(df_autonomia_restabelecimento)

        if ano == ano_atual:
            df_indisponibilidades_temp['tempo_indisponibilidade'] = df_indisponibilidades_temp.apply(get_duracao_indisponibilidade, axis=1)
            df_indisponibilidades_temp['indisponibilidade_horas'] = df_indisponibilidades_temp['tempo_indisponibilidade'].apply(get_horas)
            dfs_indisponibilidades.append(df_indisponibilidades_temp)
        else:
            pass

    df_autonomia_restabelecimento = pd.concat(dfs_autonomia_restabelecimento, ignore_index=True)
    df_indisponibilidades = pd.concat(dfs_indisponibilidades, ignore_index=True)

    df_autonomia_restabelecimento.to_pickle('data/aggregated/autonomia_restabelecimento.pkl')
    df_indisponibilidades.to_pickle('data/aggregated/indisponibilidades.pkl')

    return df_autonomia_restabelecimento, df_indisponibilidades


if __name__ == '__main__':
    run_autonomia_restabelecimento()