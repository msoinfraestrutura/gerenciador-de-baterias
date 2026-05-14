import streamlit as st
import pandas as pd


def show() -> None:
    st.image('img/logo.svg', width=70)
    st.title('Glossário')

    df_glossario = pd.DataFrame([
        {'Campo': 'Estação', 'Descrição': 'Nome estação'},
        {'Campo': 'UF', 'Descrição': 'Unidade da federação onde a estação está localizada'},
        {'Campo': 'Cluster', 'Descrição': 'Agrupamento regional da estação'},
        {'Campo': 'Tipologia', 'Descrição': 'Hierarquia da estação oriunda do campo "severidade_omr" do smartplan'},
        {'Campo': 'Tecnologia', 'Descrição': 'Tecnologia do banco de baterias (ex.: Ventilada, Lítio)'},
        {'Campo': 'Tensão', 'Descrição': 'Tensão nominal do banco de baterias (em volts)'},
        {'Campo': 'Capacidade (Ah)', 'Descrição': 'Capacidade do banco de baterias em ampère-hora (Ah)'},
        {'Campo': 'Aut. de Inventário (Hrs)', 'Descrição': 'Autonomia de bateria registrada Infratel'},
        {'Campo': 'Aut. Calculada (Hrs)', 'Descrição': 'Autonomia média calculada a partir dos incidentes da estação'},
        {'Campo': 'Restab. Calculado (Hrs)', 'Descrição': 'Tempo médio de restabelecimento de energia pela concessionária calculado a partir dos incidentes da estação'},
        {'Campo': 'Delta (Hrs)', 'Descrição': 'Diferença entre a autonomia calculada e o tempo de restabelecimento calculado. Valores negativos indicam déficit de autonomia'},
        {'Campo': 'Ganho (Hrs)', 'Descrição': 'Incremento de autonomia obtido por alocação de baterias'},
        {'Campo': 'Custo (R$)', 'Descrição': 'Custo estimado para aquisição do banco de baterias'},
        {'Campo': 'Qtde. Alocações', 'Descrição': 'Número de vezes que a estação foi priorizada pelo algoritmo'},
        {'Campo': 'Pontuação', 'Descrição': 'Pontuação da estação considerando a nova matriz de priorização'},
        {'Campo': 'Distância (km)', 'Descrição': 'Distância estimada entre estação doadora e receptora'}
    ])

    st.table(df_glossario, width='content')