
from datetime import datetime
import streamlit as st
from services.data_service import otimizador
from utils.helpers import format_number, create_excel
from charts.otimizador_de_baterias import (
    create_line_chart,
    create_scatter_map_chart,
)


def show() -> None:
    st.image('img/logo.svg', width=70)
    st.title('Otimizador de Baterias')
    st.divider()

    st.write('Defina o investimento para obter um cronograma de aquisição otimizado.')

    #dados
    df = otimizador()

    if df.empty:
        st.warning('Dados insuficientes.')
        return

    #filtros
    col1, col2 = st.columns([1, 2])

    with col1:
        options_cluster = sorted(df['cluster'].unique())
        cluster = st.multiselect(
            'Cluster',
            options=options_cluster,
            placeholder='Todos'
        )

        if cluster:
            df = df[df['cluster'].isin(cluster)].copy()

        df['custo_acumulado'] = df['custo'].cumsum()
        df['ganho_acumulado'] = df['ganho'].cumsum()

    with col2:
        max_investimento = df['custo_acumulado'].iloc[-1]
        investimento = st.slider(
            'Investimento (R$)',
            min_value=3226.56,
            max_value=max_investimento,
            value=max_investimento,
            step=10000.00,
            format='R$ %.2f'
        )

    #alocações filtradas
    df_alocacoes = df[df['custo_acumulado'] <= investimento].copy()

    ganho_total = df['ganho'].sum()

    aproveitamento = (
        df_alocacoes['ganho'].sum() / ganho_total * 100
        if ganho_total > 0 else 0
    )

    #cartões
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        'Investimento (R$)',
        format_number(
            df_alocacoes['custo_acumulado'].iloc[-1]
            if not df_alocacoes.empty else 0
        ),
        border=True
    )
    col2.metric(
        'Ganho (Hrs)',
        format_number(
            df_alocacoes['ganho_acumulado'].iloc[-1]
            if not df_alocacoes.empty else 0
        ),
        border=True
    )
    col3.metric(
        'Qtde. Bancos de Baterias',
        len(df_alocacoes),
        border=True
    )
    col4.metric(
        'Aproveitamento',
        f'{aproveitamento:.2f}%',
        help='Percentual do ganho total possível com o investimento simulado.',
        border=True
    )

    st.divider()

    col1, col2 = st.columns([6, 4])
    with col1:
        st.subheader('Eficiência')
        fig_eficiencia_alocacoes = create_line_chart(df_alocacoes)
        st.plotly_chart(fig_eficiencia_alocacoes, width='stretch')
        try:
            ganho_filtrado = df_alocacoes['ganho'].sum()
            custo_filtrado = df_alocacoes['custo'].sum()

            df_temp = df_alocacoes.copy()
            df_temp['pct_ganho'] = (df_temp['ganho'].cumsum() / ganho_filtrado) * 100
            df_temp['pct_custo'] = (df_temp['custo'].cumsum() / custo_filtrado) * 100

            p_80 = df_temp[df_temp['pct_ganho'] >= 80].iloc[0]

            st.success(
                f'**Eficiência:** O algoritmo atingiu **80%** do **ganho** '
                f'com **{p_80["pct_custo"]:.2f}%** do **investimento** total simulado.'
            )
        except Exception:
            pass

    with col2:
        st.subheader('Mapa de Estações')
        fig_map = create_scatter_map_chart(df_alocacoes)
        st.plotly_chart(fig_map, width='stretch')

    st.subheader('Alocações e Cronograma')
    st.info(f'Para o investimento simulado, o algoritmo priorizou **{df_alocacoes["estacao"].nunique()}** estações para alocação de baterias.')
    
    st.dataframe(
        df_alocacoes.sort_values('id'),
        column_order=[
            'id', 'estacao', 'uf', 'cluster', 'tipologia', 'rodada_alocacao', 'custo', 'ganho',
            'autonomia_media_horas', 'autonomia_horas', 'restabelecimento_medio_horas'
        ],
        column_config={
            'estacao': st.column_config.TextColumn('Estação'),
            'uf': st.column_config.TextColumn('UF'),
            'cluster': st.column_config.TextColumn('Cluster'),
            'tipologia': st.column_config.TextColumn('Tipologia'),
            'id': st.column_config.NumberColumn('Ordem'),
            'rodada_alocacao': st.column_config.NumberColumn('Qtde. Alocações'),
            'custo': st.column_config.NumberColumn(
                'Custo (R$)', 
                format='%.2f'
            ),
            'ganho': st.column_config.NumberColumn(
                'Ganho (Hrs)', 
                help='Autonomia adicional gerada pela alocação do banco de baterias na rodada',
                format='%.2f'
            ),
            'autonomia_media_horas': st.column_config.NumberColumn(
                'Aut. Calculada (Hrs)', 
                help='Autonomia de bateria calculada da estação',
                format='%.2f'
            ),
            'autonomia_horas': st.column_config.NumberColumn(
                'Aut. de Inventário (Hrs)', 
                help='Autonomia de bateria de inventário da estação',
                format='%.2f'
            ),
            'restabelecimento_medio_horas': st.column_config.NumberColumn(
                'Restab. Calculado (Hrs)', 
                help='Tempo médio de restabelecimento pela concessionária',
                format='%.2f'
            ),
        },
        hide_index=True,
        width='stretch'
    )
    file_name = f'otimizador_de_baterias{datetime.now().strftime("%Y-%m-%d")}'
    st.download_button(
        label='Download Excel',
        data=create_excel(df_alocacoes),
        file_name=f'{file_name}.xlsx',
        width='stretch'
    )