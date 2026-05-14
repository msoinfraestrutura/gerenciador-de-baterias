from pathlib import Path
import pandas as pd


BASE_PATH = Path(__file__).resolve().parents[2] / 'backend' / 'data' /'raw'

def get_historico_autonomia_restabelecimento():
    df_autonomia_restabelecimento_2023 = pd.read_pickle(BASE_PATH / "autonomia_restabelecimento_2023.pkl")
    df_autonomia_restabelecimento_2024 = pd.read_pickle(BASE_PATH / "autonomia_restabelecimento_2024.pkl")
    df_autonomia_restabelecimento_2025 = pd.read_pickle(BASE_PATH / "autonomia_restabelecimento_2025.pkl")

    return (
        df_autonomia_restabelecimento_2023, 
        df_autonomia_restabelecimento_2024, 
        df_autonomia_restabelecimento_2025
    )