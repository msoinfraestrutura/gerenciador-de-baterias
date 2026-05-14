import io
from datetime import timedelta
import pandas as pd
import numpy as np


def format_number(value: float, prefix: str = '') -> str:
    '''
    Formata número para representação legível com unidade.

    Params:
        value (float): Valor numérico.
        prefix (str): Prefixo (ex: R$, US$).

    Returns:
        str: Valor formatado.
    '''
    for unit in ['', 'Mil']:
        if value < 1000:
            return f'{prefix} {value:.2f} {unit}'
        value /= 1000

    return f'{prefix} {value:.2f} Mi'


def format_seconds(seconds):
    '''
    Converte segundos para HH:MM:SS.

    Params:
        seconds (int | float): Tempo em segundos.

    Returns:
        str: Tempo formatado.
    '''
    if seconds is None:
        return '00:00:00'
    return str(timedelta(seconds=int(seconds)))


def create_excel(df: pd.DataFrame) -> io.BytesIO:
    '''
    Converte DataFrame para arquivo Excel em memória.

    Params:
        df (pd.DataFrame): DataFrame de entrada.

    Returns:
        io.BytesIO: Buffer com arquivo Excel.
    '''
    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)

    buffer.seek(0)

    return buffer


def get_distance(lat1, lon1, lat2, lon2):
    '''
    Calcula distância geodésica entre dois pontos (km).

    Params:
        lat1, lon1 (float): Coordenadas ponto 1.
        lat2, lon2 (float): Coordenadas ponto 2.

    Returns:
        float: Distância em quilômetros.
    '''
    R = 6371
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp, dl = np.radians(lat2 - lat1), np.radians(lon2 - lon1)
    a = np.sin(dp / 2)**2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2)**2
    return 2 * R * np.arctan2(np.sqrt(a), np.sqrt(1 - a))