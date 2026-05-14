import streamlit as st
import pandas as pd
from services.data_service import executivo
from charts.executivo import create_line_chart
from utils.helpers import format_number
from . import TRAFEGO_DADOS_MEDIO_MOVEL

def show() -> None:
    st.image('img/logo.svg', width=75)
    st.title('Visões - Executivo')

    st.divider()

    #dados
    df, df_disponibilidade = executivo()

    #métricas
    custo_total = df['custo_acumulado'].iloc[-1]
    ganho_total = df['ganho_acumulado'].iloc[-1]

    faturamento_impactado = df['faturamento_ewma'].sum()
    clientes_impactados = df['trafego_dados_ewma'].sum() / TRAFEGO_DADOS_MEDIO_MOVEL

    indisponibilidade_total = df_disponibilidade['indisponibilidade_horas'].sum()
    disponibilidade_media = df_disponibilidade['disponibilidade'].mean()

    tempo_total_operacao = indisponibilidade_total / (1 - (disponibilidade_media / 100))
    ganho_disponibilidade = 1 - ((indisponibilidade_total - ganho_total) / tempo_total_operacao) * 100

    #tabelas
    df_eficiencia_alocacoes=  pd.DataFrame({
        'pct_custo': [0] + ((df['custo_acumulado'] / custo_total) * 100).tolist(),
        'pct_ganho': [0] + ((df['ganho_acumulado'] / ganho_total) * 100).tolist(),
        'custo': [0] + df['custo_acumulado'].tolist(),
        'ganho': [0] + df['ganho_acumulado'].tolist()
    })

    #figuras
    fig_eficiencia_alocacoes = create_line_chart(df_eficiencia_alocacoes)

    #cartões
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        'Investimento (R$)',
        format_number(custo_total),
        border=True
    )
    col2.metric(
        'Ganho (Hrs)',
        format_number(ganho_total),
        border=True
    )
    col3.metric(
        'Faturamento Impactado (R$)',
        format_number(faturamento_impactado),
        border=True
    )
    col4.metric(
        'Clientes Impactados',
        format_number(clientes_impactados),
        border=True
    )

    st.divider()

    st.subheader('Eficiência')
    st.write(
        'O modelo prioriza estações com maior ganho por custo, '
        'ponderado por sua pontuação.'
    )

    st.plotly_chart(fig_eficiencia_alocacoes, width='stretch')

    try:
        p_80 = df_eficiencia_alocacoes[df_eficiencia_alocacoes['pct_ganho'] >= 80].iloc[0]
        st.success(
            f'**Eficiência:** O modelo atingiu **80%** do **ganho** '
            f'com **{p_80["pct_custo"]:.2f}%** do **investimento** total simulado.'
        )
    except Exception:
        pass

    #st.subheader('Ganho de Disponibilidade')
    #st.metric(
    #    'Nova Disponibilidade Projetada (%)',
    #    f'{ganho_disponibilidade:.2f}%'
    #)