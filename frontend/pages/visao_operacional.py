from typing import List
import streamlit as st
import pandas as pd
import datetime
from services.visao_operacional_service import load_data
from charts.visao_operacional import (
    create_scatter_map,
    create_radar,
    create_risk_heatmap,
)
from utils.helpers import create_excel


def filtra_dataframe(
    df: pd.DataFrame,
    ano: List,
    cluster: List,
    uf: List,
    municipio: List,
    rotulo_eficiencia_media_horas: List,
    hierarquia: List,
    estacao: List
) -> List:
    query='''
        `ano` in @ano and \
        `cluster` in @cluster and \
        `uf` in @uf and \
        `municipio` in @municipio and \
        `rotulo_eficiencia_media_horas` in @rotulo_eficiencia_media_horas and \
        `hierarquia` in @hierarquia and \
        `estacao` in @estacao                                                                                                                
    '''
    df_filtrado = df.query(query)
    return df_filtrado


def show() -> None:
    st.image('img/logo.svg', width=75)
    st.title('Visões - Executivo')

    st.divider()

    #dados
    df = load_data()

    #filtros
    st.subheader('Filtros')
    df_filtro = df.sort_values(by=['ano', 'cluster', 'uf', 'municipio', 'hierarquia', 'estacao']).copy()
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    with col1:
        with st.expander('Ano'):
            todos_ano = st.checkbox(label='Todos', key='todos_ano', value=True)
            if todos_ano:
                ano = df_filtro['ano'].unique().tolist()
            else:
                ano = st.multiselect(
                    label='Selecione o ano',
                    label_visibility='collapsed',
                    placeholder='Selecione',
                    options=df_filtro['ano'].unique(),
                    default=None
                )
    df_filtro = df_filtro[df_filtro['ano'].isin(ano)]
    with col2:
        with st.expander('Cluster'):
            todos_cluster = st.checkbox(label='Todos', key='todos_cluster', value=True)
            if todos_cluster:
                cluster = df_filtro['cluster'].unique()
            else:
                cluster = st.multiselect(
                    label='Selecione o cluster', 
                    label_visibility='collapsed', 
                    placeholder='Selecione',
                    options=df_filtro['cluster'].unique(), 
                    default=None
                )
    df_filtro = df_filtro[df_filtro['cluster'].isin(cluster)]
    with col3:
        with st.expander('UF'):
            todos_uf = st.checkbox(label='Todos', key='todos_uf', value=True)
            if todos_uf:
                uf = df_filtro['uf'].unique()
            else:
                uf = st.multiselect(
                    label='Selecione o uf', 
                    label_visibility='collapsed', 
                    placeholder='Selecione',
                    options=df_filtro['uf'].unique(), 
                    default=None
                )
    df_filtro = df_filtro[df_filtro['uf'].isin(uf)]
    with col4:
        with st.expander('Município'):
            todos_municipio = st.checkbox(label='Todos', key='todos_municipio', value=True)
            if todos_municipio:
                municipio = df_filtro['municipio'].unique()
            else:
                municipio = st.multiselect(
                    label='Selecione o município', 
                    label_visibility='collapsed', 
                    placeholder='Selecione', 
                    options=df_filtro['municipio'].unique(), 
                    default=None
                )
    df_filtro = df_filtro[df_filtro['municipio'].isin(municipio)]
    with col5:
        with st.expander('Situação'):
            todos_rotulo_eficiencia_media_horas = st.checkbox(label='Todos', key='todos_rotulo_eficiencia_media_horas', value=True)
            if todos_rotulo_eficiencia_media_horas:
                rotulo_eficiencia_media_horas = df_filtro['rotulo_eficiencia_media_horas'].sort_values().unique().tolist()
            else:
                rotulo_eficiencia_media_horas = st.multiselect(
                    label='Selecione a situação', 
                    label_visibility='collapsed', 
                    placeholder='Selecione', 
                    options=df_filtro['rotulo_eficiencia_media_horas'].sort_values().unique().tolist(), 
                    default=None
                )
    df_filtro = df_filtro[df_filtro['rotulo_eficiencia_media_horas'].isin(rotulo_eficiencia_media_horas)]
    with col6:
        with st.expander('hierarquia'):
            todos_hierarquia = st.checkbox(label='Todos', key='todos_hierarquia', value=True)
            if todos_hierarquia:
                hierarquia = df_filtro['hierarquia'].unique()
            else:
                hierarquia = st.multiselect(
                    label='Selecione a hierarquia', 
                    label_visibility='collapsed', 
                    placeholder='Selecione', 
                    options=df_filtro['hierarquia'].unique(),
                    default=None
                )
    df_filtro = df_filtro[df_filtro['hierarquia'].isin(hierarquia)]
    with col7:
        with st.expander('Estação'):
            todos_estacao = st.checkbox(label='Todos', key='todos_estacao', value=True)
            if todos_estacao:
                estacao = df_filtro['estacao'].unique()
            else:
                estacao = st.multiselect(
                    label='Selecione a estação',
                    label_visibility='collapsed',
                    placeholder='Selecione', 
                    options=df_filtro['estacao'].unique(), 
                    default=None
                )
    df_filtro = df_filtro[df_filtro['estacao'].isin(estacao)]

    #filtra dataframe
    df_filtrado = filtra_dataframe(df, ano, cluster, uf, municipio, rotulo_eficiencia_media_horas, hierarquia, estacao)
    
    try:
        if df_filtro.empty == False:
            #cartões
            media_autonomia = df_filtrado['autonomia_media_horas'].mean().round(2)
            media_restabelecimento = df_filtrado['restabelecimento_medio_horas'].mean().round(2)
            qtde_estacao = df_filtrado['estacao'].nunique()
            participacao_energia_indisponibilidade = ((df_filtrado['indisponibilidade_energia_horas'].mean() / df_filtrado['indisponibilidade_total_horas'].mean()) * 100).round(2)
            
            #tabelas
            df_qtde_estacao_situacao = df_filtrado.groupby('rotulo_eficiencia_media_horas')['estacao'].agg(quantidade='count').reset_index().sort_values('quantidade', ascending=False)
            df_qtde_estacao_situacao['participacao'] = (df_qtde_estacao_situacao['quantidade'] / df_qtde_estacao_situacao['quantidade'].sum() * 100).round(2)

            df_qtde_estacao_situacao = df_filtrado.groupby('rotulo_eficiencia_media_horas')['estacao'].agg(quantidade='count').reset_index().sort_values('quantidade', ascending=False)
            df_qtde_estacao_situacao['participacao'] = (df_qtde_estacao_situacao['quantidade'] / df_qtde_estacao_situacao['quantidade'].sum() * 100).round(2)
            
            df_qtde_estacao_ano_autonomia_situacao = df_filtrado.groupby(['ano', 'rotulo_eficiencia_media_horas'])['estacao'].agg(quantidade='count').reset_index().sort_values('ano', ascending=False)
            df_qtde_estacao_ano_autonomia_situacao_temp = df_qtde_estacao_ano_autonomia_situacao.groupby('ano')['quantidade'].agg(total='sum').reset_index()
            df_qtde_estacao_ano_autonomia_situacao = pd.merge(df_qtde_estacao_ano_autonomia_situacao, df_qtde_estacao_ano_autonomia_situacao_temp, on='ano')
            df_qtde_estacao_ano_autonomia_situacao['participacao'] = (df_qtde_estacao_ano_autonomia_situacao['quantidade'] / df_qtde_estacao_ano_autonomia_situacao['total'] * 100).round(2)
            df_qtde_estacao_ano_autonomia_situacao = df_qtde_estacao_ano_autonomia_situacao.sort_values(by=['ano', 'participacao'], ascending=[True, False])
            
            df_qtde_estacao_ano_autonomia_faixa = df_filtrado.groupby(['ano', 'rotulo_autonomia_media_horas'])['estacao'].agg(quantidade='count').reset_index().sort_values('ano', ascending=False)
            df_qtde_estacao_ano_autonomia_faixa_temp = df_qtde_estacao_ano_autonomia_faixa.groupby('ano')['quantidade'].agg(total='sum').reset_index()
            df_qtde_estacao_ano_autonomia_faixa = pd.merge(df_qtde_estacao_ano_autonomia_faixa, df_qtde_estacao_ano_autonomia_faixa_temp, on='ano')
            df_qtde_estacao_ano_autonomia_faixa['participacao'] = (df_qtde_estacao_ano_autonomia_faixa['quantidade'] / df_qtde_estacao_ano_autonomia_faixa['total'] * 100).round(2)
            df_qtde_estacao_ano_autonomia_faixa = df_qtde_estacao_ano_autonomia_faixa.sort_values(by=['ano', 'participacao'], ascending=[True, False])
            
            df_disponibilidade_ano_situacao = df_filtrado.groupby('ano').agg({ #'rotulo_eficiencia_media_horas'
                'disponibilidade': 'mean', 
                'disponibilidade_parcial': 'mean',
                'disponibilidade_energia': 'mean'
            }).reset_index().sort_values('ano')
            df_disponibilidade_ano_situacao['diferenca_meta_disponibilidade'] = df_disponibilidade_ano_situacao['disponibilidade'] - 99.65
            df_disponibilidade_ano_situacao['diferenca_meta_disponibilidade_parcial'] = df_disponibilidade_ano_situacao['disponibilidade_parcial'] - 99.65
            df_disponibilidade_ano_situacao['diferenca_meta_disponibilidade_energia'] = df_disponibilidade_ano_situacao['disponibilidade_energia'] - 99.65
            
            df_qtde_estacao_cluster_situacao = df_filtrado.groupby(['cluster', 'rotulo_eficiencia_media_horas']).agg(
                quantidade=('estacao', 'count'), 
                disponibilidade=('disponibilidade', 'mean'),
                participacao_energia_indisponibilidade=('participacao_energia_indisponibilidade', 'mean')
            ).reset_index().sort_values('cluster', ascending=False)
            df_qtde_estacao_cluster_situacao_temp = df_qtde_estacao_cluster_situacao.groupby('cluster')['quantidade'].agg(total='sum').reset_index()
            df_qtde_estacao_cluster_situacao = pd.merge(df_qtde_estacao_cluster_situacao, df_qtde_estacao_cluster_situacao_temp, on='cluster')
            df_qtde_estacao_cluster_situacao['participacao'] = (df_qtde_estacao_cluster_situacao['quantidade'] / df_qtde_estacao_cluster_situacao['total'] * 100).round(2)
            
            df_qtde_estacao_faixa_autonomia =  df_filtrado.groupby('rotulo_autonomia_media_horas')['estacao'].agg(quantidade='count').reset_index().sort_values('rotulo_autonomia_media_horas', ascending=False)
            df_qtde_estacao_faixa_autonomia['total'] = df_qtde_estacao_faixa_autonomia['quantidade'].sum()
            df_qtde_estacao_faixa_autonomia['participacao'] = ((df_qtde_estacao_faixa_autonomia['quantidade'] / df_qtde_estacao_faixa_autonomia['total']) * 100).round(2)
            
            df_qtde_estacao_faixa_restabelecimento =  df_filtrado.groupby('rotulo_restabelecimento_medio_horas')['estacao'].agg(quantidade='count').reset_index().sort_values('rotulo_restabelecimento_medio_horas', ascending=False)
            df_qtde_estacao_faixa_restabelecimento['total'] = df_qtde_estacao_faixa_restabelecimento['quantidade'].sum()
            df_qtde_estacao_faixa_restabelecimento['participacao'] = ((df_qtde_estacao_faixa_restabelecimento['quantidade'] / df_qtde_estacao_faixa_restabelecimento['total']) * 100).round(2)

            df = df_filtrado.copy()
            prob_labels = ['Pouco Provável', 'Provável', 'Muito Provável', 'Quase Certo']
            imp_labels = ['Moderado', 'Severo', 'Crítico', 'Muito Crítico']
            ordered_imp_labels = imp_labels[::-1]
            df['probabilidade'] = df[['pontuacao_autonomia', 'pontuacao_idade_bateria', 'pontuacao_tmr']].prod(axis=1)
            df['impacto'] = df[['pontuacao_trafego_dados', 'pontuacao_faturamento', 'pontuacao_hierarquia', 'pontuacao_cliente']].prod(axis=1)
            df['prob_cat'] = pd.cut(df['probabilidade'], bins=4, labels=prob_labels)
            df['imp_cat'] = pd.cut(df['impacto'], bins=4, labels=imp_labels)
            
            df_mapa_risco = (pd.crosstab(df['imp_cat'], df['prob_cat']).reindex(index=ordered_imp_labels, columns=prob_labels, fill_value=0))

            df_analitico_mapa_risco = df.copy()
            imp_pesos = {'Moderado': 1, 'Severo': 2, 'Crítico': 3, 'Muito Crítico': 4}
            prob_pesos = {'Pouco Provável': 1, 'Provável': 2, 'Muito Provável': 3, 'Quase Certo': 4}
            df_analitico_mapa_risco['imp_n'] = df_analitico_mapa_risco['imp_cat'].map(imp_pesos)
            df_analitico_mapa_risco['prob_n'] = df_analitico_mapa_risco['prob_cat'].map(prob_pesos)
            ranking_map = {
                ('Muito Crítico', 'Pouco Provável'): 1, 
                ('Muito Crítico', 'Provável'): 2, 
                ('Muito Crítico', 'Muito Provável'): 3, 
                ('Muito Crítico', 'Quase Certo'): 3,
                ('Crítico', 'Pouco Provável'): 0,       
                ('Crítico', 'Provável'): 2,       
                ('Crítico', 'Muito Provável'): 3,       
                ('Crítico', 'Quase Certo'): 3,
                ('Severo', 'Pouco Provável'): 0,        
                ('Severo', 'Provável'): 1,        
                ('Severo', 'Muito Provável'): 2,        
                ('Severo', 'Quase Certo'): 2,
                ('Moderado', 'Pouco Provável'): 0,      
                ('Moderado', 'Provável'): 0,      
                ('Moderado', 'Muito Provável'): 1,      
                ('Moderado', 'Quase Certo'): 2,
            }
            df_analitico_mapa_risco['ranking'] = df_analitico_mapa_risco.apply(
                lambda row: ranking_map.get((row['imp_cat'], row['prob_cat']), 0), axis=1
            )
            df_analitico_mapa_risco = df_analitico_mapa_risco.sort_values(
                by=['ranking', 'imp_n', 'prob_n', 'impacto', 'probabilidade'], 
                ascending=[False, False, False, False, False]
            ).reset_index(drop=True)
            columns = {'estacao': 'Estação', 'imp_cat': 'Impacto', 'prob_cat': 'Probabilidade'}
            df_analitico_mapa_risco = df_analitico_mapa_risco[['estacao', 'imp_cat', 'prob_cat']].rename(columns=columns)

            col1, col2, col3, _ = st.columns(4)
            with col1:
                st.metric('Qtde de Estações', f'{qtde_estacao}', border=True)
            with col2:
                st.metric('Autonomia Bateria (hrs)', f'{media_autonomia}', border=True)
            with col3:
                st.metric('Restabelecimento Energia (hrs)', f'{media_restabelecimento}', border=True)
            option = st.radio(label='option', options=['Autonomia Vs. Restabelecimento', 'Mapa de Estações', 'Mapa de Risco'], label_visibility='collapsed', horizontal=True, key='option_geral_mapa')
            if option == 'Autonomia Vs. Restabelecimento':
                st.plotly_chart(create_radar(
                    df_1=df_qtde_estacao_faixa_autonomia,                      
                    df_2=df_qtde_estacao_faixa_restabelecimento,                                 
                    r_col='participacao',                      
                    theta_col_1='rotulo_autonomia_media_horas', 
                    theta_col_2='rotulo_restabelecimento_medio_horas',
                    name_1='Autonomia Bateria',            
                    name_2='Restabelecimento Energia',    
                    title='Autonomia de Bateria Vs. Restabelecimento Energia por Faixa' 
                ))
            elif option == 'Mapa de Estações':     
                if len(uf) == 1:
                    lat = df_filtrado['latitude_uf'].unique()[0]
                    lon = df_filtrado['longitude_uf'].unique()[0]
                    st.plotly_chart(
                        create_scatter_map(
                            df_filtrado, 
                            'rotulo_eficiencia_media_horas', 
                            ['autonomia_media_horas', 'restabelecimento_medio_horas'],
                            'Autonomia de Bateria por Estação',
                            lat, 
                            lon, 
                            4.5
                        ), 
                        config={'scrollZoom': True}
                    )
                else:
                    st.plotly_chart(
                        create_scatter_map(
                            df_filtrado, 
                            'rotulo_eficiencia_media_horas',
                            ['autonomia_media_horas', 'restabelecimento_medio_horas'],
                            'Autonomia de Bateria por Estação'
                        ),
                        config={'scrollZoom': True}
                    )
            else:
                col1, col2 = st.columns([.8, .2])
                with col1:
                    st.plotly_chart(create_risk_heatmap(df_mapa_risco, prob_labels=prob_labels, imp_labels=ordered_imp_labels, title='Mapa de Estações Fora do Draft'))
                with col2:            
                    st.dataframe(df_analitico_mapa_risco, hide_index=True, height=502)
                    file_name = f'mapa_de_risco{datetime.now().strftime("%Y-%m-%d")}'
                    st.download_button(
                        label='Download Excel',
                        data=create_excel(df_analitico_mapa_risco),
                        file_name=f'{file_name}.xlsx',
                        width='stretch'
                    )
        else:
            fields = []
            checks = {
                'Ano': (todos_ano, ano),
                'Cluster': (todos_cluster, cluster),
                'UF': (todos_uf, uf),
                'Município': (todos_municipio, municipio),
                'Situação': (todos_rotulo_eficiencia_media_horas, rotulo_eficiencia_media_horas),
                'Hierarquia': (todos_hierarquia, hierarquia),
                'Estação': (todos_estacao, estacao)
            }
            for field, (all_checked, selected_values) in checks.items():
                if not all_checked and (selected_values is None or selected_values == []):
                    fields.append(field)
            if fields: 
                st.warning(f'Para exibir o relatório, selecione dados nos campos: {", ".join(fields)}')
        except Exception as e:
        st.warning(f'Error: {e}')