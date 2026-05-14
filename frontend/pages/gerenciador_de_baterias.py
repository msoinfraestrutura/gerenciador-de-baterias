from datetime import datetime
import streamlit as st
import numpy as np

from services.data_service import gerenciador
from utils.helpers import get_distance, create_excel
from charts.gerenciador_de_baterias import (
    cretae_scatter_map,
    create_scatter_map_station,
    create_bar_chart
)


def show() -> None:
    st.image('img/logo.svg', width=70)
    st.title('Gerenciador de Baterias')
    st.divider()

    #dados
    df, df_autonomia_inventario = gerenciador()

    df_estacao_autonomia_inventario_elegivel = df_autonomia_inventario[
        df_autonomia_inventario['autonomia_horas'] > 4
    ]['estacao'].unique()

    #filtro
    col1, col2 = st.columns(2)
    with col1:
        cluster = st.selectbox(
            'Cluster',
            ['Todos'] + sorted(df['cluster'].unique())
        )

    df_filtrado = df.copy() if cluster == 'Todos' else df[df['cluster'] == cluster].copy()

    #receptoras/doadoras
    df_estacoes_receptoras = df_filtrado[df_filtrado['delta'] < 0].copy()

    df_estacoes_doadoras = df_filtrado[
        (df_filtrado['delta'] > 0) &
        (df_filtrado['pontuacao_hierarquia'] == 60) &
        (df_filtrado['estacao'].isin(df_estacao_autonomia_inventario_elegivel))
    ].copy()

    if df_estacoes_receptoras.empty:
        st.warning('Nenhuma estação receptora elegível encontrada.')
        st.stop()

    with col2:
        estacao_receptora = st.selectbox(
            'Estação Receptora',
            ['Todos'] + sorted(df_estacoes_receptoras['estacao'].unique())
        )

    #geral
    if estacao_receptora == 'Todos':
        col1, col2, col3, col4 = st.columns(4)
        col1.metric('Estações', len(df_filtrado), border=True)
        col2.metric('Estações Receptoras', len(df_estacoes_receptoras), border=True)
        col3.metric('Estações Doadoras', len(df_estacoes_doadoras), border=True)
        col4.metric('Delta (Hrs)', f'{df_filtrado["delta"].mean():.2f}', border=True)

        col1, col2 = st.columns([6, 4])
        with col1:
            st.subheader('Mapa de Estações')
            st.plotly_chart(
                cretae_scatter_map(
                    df_estacoes_doadoras,
                    df_estacoes_receptoras,
                    zoom=4 if cluster == 'Todos' else 5
                ),
                width='stretch',
                config={'scrollZoom': True}
            )

        with col2:
            st.subheader('Ranking Estações Receptoras')
            df_ranking = (
                df_estacoes_receptoras
                .sort_values(['pontuacao', 'delta'], ascending=[False, True])
                .head(20)
            )
            st.plotly_chart(
                create_bar_chart(df_ranking),
                width='stretch'
            )

        st.subheader('Oportunidades')

        df_estacao_receptora_temp = df_autonomia_inventario.merge(
            df_estacoes_receptoras[
                ['estacao', 'cluster', 'latitude_estacao', 'longitude_estacao', 'delta']
            ],
            on='estacao'
        )

        df_estacoes_doadoras_temp = (
            df_autonomia_inventario[df_autonomia_inventario['autonomia_horas'] > 4]
            .merge(
                df_estacoes_doadoras[df_estacoes_doadoras['delta'] > 4][[
                    'estacao', 'cluster', 'latitude_estacao', 'longitude_estacao',
                    'delta', 'autonomia_media_horas', 'restabelecimento_medio_horas'
                ]],
                on='estacao'
            )
        )

        df_estacoes_doadoras_detalhamento = df_estacao_receptora_temp.merge(
            df_estacoes_doadoras_temp,
            on=['cluster', 'tecnologia', 'tensao', 'capacidade'],
            suffixes=('_receptora', '')
        )

        if not df_estacoes_doadoras_detalhamento.empty:
            df_estacoes_doadoras_detalhamento['distancia'] = get_distance(
                df_estacoes_doadoras_detalhamento['latitude_estacao_receptora'],
                df_estacoes_doadoras_detalhamento['longitude_estacao_receptora'],
                df_estacoes_doadoras_detalhamento['latitude_estacao'],
                df_estacoes_doadoras_detalhamento['longitude_estacao']
            )

            df_estacoes_doadoras_detalhamento['pontuacao_recomendacao'] = (
                df_estacoes_doadoras_detalhamento['autonomia_media_horas'] * 0.7 +
                df_estacoes_doadoras_detalhamento['delta'] * 0.3 -
                np.sqrt(df_estacoes_doadoras_detalhamento['distancia']) * 0.5
            )

            st.dataframe(
                df_estacoes_doadoras_detalhamento.sort_values(
                    ['estacao_receptora', 'pontuacao_recomendacao'],
                    ascending=[True, False]
                ),
                column_order=[
                    'estacao_receptora', 'estacao', 'tecnologia', 'tensao', 'capacidade',
                    'autonomia_horas', 'autonomia_media_horas',
                    'restabelecimento_medio_horas', 'delta', 'distancia'
                ],
                column_config={
                    'estacao_receptora': 'Estação Receptora',
                    'estacao': 'Estação Doadora',
                    'tecnologia': 'Tecnologia',
                    'tensao': 'Tensão',
                    'capacidade': st.column_config.NumberColumn('Capacidade (Ah)', format='%d'),
                    'autonomia_horas': st.column_config.NumberColumn('Aut. Inventário (Hrs)', format='%.2f'),
                    'autonomia_media_horas': st.column_config.NumberColumn('Aut. Calculada (Hrs)', format='%.2f'),
                    'restabelecimento_medio_horas': st.column_config.NumberColumn('Restab. Calculado (Hrs)', format='%.2f'),
                    'delta': st.column_config.NumberColumn('Delta (Hrs)', format='%.2f'),
                    'distancia': st.column_config.NumberColumn('Distância (km)', format='%.2f'),
                },
                hide_index=True,
                width='stretch'
            )

            st.download_button(
                'Download Excel',
                create_excel(df_estacoes_doadoras_detalhamento),
                f'matriz_oportunidades_{datetime.now().strftime("%Y%m%d")}.xlsx',
                width='stretch'
            )
        else:
            st.warning('Nenhuma estação doadora encontrada para os critérios selecionados.')

    #receptora
    else:
        col1, col2 = st.columns(2)
        with col1:
            distancia_estacao_doadora = st.slider('Raio de Busca', 0, 5000, 5000, format='%d km')
        with col2:
            delta_estacao_doadora = st.slider('Delta', 0, 50, 4, format='%d h')

        df_estacao_receptora_filtrado = (
            df_estacoes_receptoras[df_estacoes_receptoras['estacao'] == estacao_receptora]
            .iloc[0]
        )

        df_estacao_doadora_filtrado = df_estacoes_doadoras[
            df_estacoes_doadoras['cluster'] == df_estacao_receptora_filtrado['cluster']
        ].copy()

        lat = df_estacao_receptora_filtrado['latitude_estacao']
        lon = df_estacao_receptora_filtrado['longitude_estacao']

        df_bancos_estacao_receptora = (
            df_autonomia_inventario[df_autonomia_inventario['estacao'] == estacao_receptora]
            [['tecnologia', 'tensao', 'capacidade']]
            .drop_duplicates()
        )

        bancos_comp = (
            df_autonomia_inventario[
                (df_autonomia_inventario['estacao'].isin(df_estacao_doadora_filtrado['estacao'])) &
                (df_autonomia_inventario['autonomia_horas'] > 4)
            ].merge(df_bancos_estacao_receptora, on=['tecnologia', 'tensao', 'capacidade'])
        )

        df_estacao_doadora_filtrado = df_estacao_doadora_filtrado[
            df_estacao_doadora_filtrado['estacao'].isin(bancos_comp['estacao'])
        ].copy()

        if not df_estacao_doadora_filtrado.empty:
            df_estacao_doadora_filtrado['distancia'] = get_distance(
                lat, lon,
                df_estacao_doadora_filtrado['latitude_estacao'],
                df_estacao_doadora_filtrado['longitude_estacao']
            )

            df_estacao_doadora_filtrado = df_estacao_doadora_filtrado[
                (df_estacao_doadora_filtrado['delta'] > delta_estacao_doadora) &
                (df_estacao_doadora_filtrado['distancia'] <= distancia_estacao_doadora)
            ].copy()

        if not df_estacao_doadora_filtrado.empty:
            df_estacao_doadora_filtrado['pontuacao_recomendacao'] = (
                df_estacao_doadora_filtrado['autonomia_media_horas'] * 0.7 +
                df_estacao_doadora_filtrado['delta'] * 0.3 -
                np.sqrt(df_estacao_doadora_filtrado['distancia']) * 0.5
            )

            estacao_recomendada = df_estacao_doadora_filtrado.sort_values(
                'pontuacao_recomendacao', ascending=False
            ).iloc[0]

            st.success(
                f'Recomendação: Realocar baterias da estação '
                f'**{estacao_recomendada["estacao"]}** ({estacao_recomendada["distancia"]:.2f} km).'
            )

            st.subheader('Mapa de Estações')
            st.plotly_chart(
                create_scatter_map_station(
                    df_estacao_doadora_filtrado,
                    df_estacao_receptora_filtrado,
                    estacao_recomendada['estacao']
                ),
                width='stretch',
                config={'scrollZoom': True}
            )

            st.subheader('Detalhamento')
            st.write('Estação Receptora')

            df_estacao_receptora_detalhamento = df_autonomia_inventario[
                df_autonomia_inventario['estacao'] == estacao_receptora
            ].merge(df_estacao_receptora_filtrado.to_frame().T, on='estacao')

            st.dataframe(
                df_estacao_receptora_detalhamento,
                column_order=[
                    'estacao', 'tecnologia', 'tensao', 'capacidade',
                    'autonomia_horas', 'autonomia_media_horas',
                    'restabelecimento_medio_horas', 'delta'
                ],
                column_config={
                    'estacao': 'Estação',
                    'tecnologia': 'Tecnologia',
                    'tensao': 'Tensão',
                    'capacidade': st.column_config.NumberColumn('Capacidade (Ah)', format='%d'),
                    'autonomia_horas': st.column_config.NumberColumn('Aut. Inventário (Hrs)', format='%.2f'),
                    'autonomia_media_horas': st.column_config.NumberColumn('Aut. Calculada (Hrs)', format='%.2f'),
                    'restabelecimento_medio_horas': st.column_config.NumberColumn('Restab. Calculado (Hrs)', format='%.2f'),
                    'delta': st.column_config.NumberColumn('Delta (Hrs)', format='%.2f'),
                },
                hide_index=True,
                width='stretch'
            )

            st.write('Oportunidades')

            df_estacoes_doadora_detalhamento = bancos_comp.merge(
                df_estacao_doadora_filtrado, on='estacao'
            )
            df_estacoes_doadora_detalhamento.insert(0, 'estacao_receptora', estacao_receptora)

            st.dataframe(
                df_estacoes_doadora_detalhamento.sort_values(
                    by='pontuacao_recomendacao', ascending=False
                ),
                column_order=[
                    'estacao_receptora', 'estacao', 'tecnologia', 'tensao', 'capacidade',
                    'autonomia_horas', 'autonomia_media_horas',
                    'restabelecimento_medio_horas', 'delta', 'distancia'
                ],
                column_config={
                    'estacao_receptora': 'Estação Receptora',
                    'estacao': 'Estação Doadora',
                    'tecnologia': 'Tecnologia',
                    'tensao': 'Tensão',
                    'capacidade': st.column_config.NumberColumn('Capacidade (Ah)', format='%d'),
                    'autonomia_horas': st.column_config.NumberColumn('Aut. Inventário (Hrs)', format='%.2f'),
                    'autonomia_media_horas': st.column_config.NumberColumn('Aut. Calculada (Hrs)', format='%.2f'),
                    'restabelecimento_medio_horas': st.column_config.NumberColumn('Restab. Calculado (Hrs)', format='%.2f'),
                    'delta': st.column_config.NumberColumn('Delta (Hrs)', format='%.2f'),
                    'distancia': st.column_config.NumberColumn('Distância (km)', format='%.2f'),
                },
                hide_index=True,
                width='stretch'
            )

            st.download_button(
                'Download Excel',
                create_excel(df_estacoes_doadora_detalhamento),
                f'gerenciador_{datetime.now().strftime("%Y%m%d")}.xlsx',
                width='stretch'
            )
        else:
            st.warning('Nenhuma estação doadora encontrada para os critérios selecionados.')