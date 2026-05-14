import pandas as pd
import numpy as np
import plotly.graph_objects as go



def create_line_chart(df_alocacoes: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_alocacoes['custo_acumulado'],
            y=df_alocacoes['ganho_acumulado'],
            mode='lines',
            name='Aproveitamento',
            fill='tozeroy',
            line=dict(color='#1476ff', width=2),
            hovertemplate=(
                'Investimento: R$ %{x:,.2f}<br>'
                'Ganho: %{y:,.2f} h<br>'
            ),
            hoverlabel=dict(
                bgcolor='#1476ff',
                font_size=14,
                font_color='white',
                font_family='Poppins, sans-serif',
                bordercolor='#1476ff'
            )
        )
    )
    fig.update_layout(
        font=dict(family='Poppins, sans-serif', color='#262730'),
        xaxis_title='Investimento (R$)',
        yaxis_title='Ganho (Hrs)',
        template='plotly_white',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        height=450,
        margin=dict(l=0, r=0, t=20, b=0)
    )
    return fig


def create_scatter_map_chart(df_alocacoes: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scattermapbox(
            lat=df_alocacoes['latitude_estacao'],
            lon=df_alocacoes['longitude_estacao'],
            mode='markers',
            marker=dict(
                size=df_alocacoes['ganho'],
                sizemode='area',
                sizeref=2. * df_alocacoes['ganho'].max() / (40 ** 2),
                color='#1476ff',
                opacity=0.75
            ),
            customdata=df_alocacoes[['estacao', 'ganho', 'custo']],
            hovertemplate=(
                '<b>%{customdata[0]}</b><br><br>'
                'Ganho: %{customdata[1]:.2f} h<br>'
                'Custo: R$ %{customdata[2]:.2f}<br>'
                '<extra></extra>'
            ),
            name='Estações'
        )
    )
    fig.update_layout(
        font=dict(family='Poppins, sans-serif'),
        mapbox=dict(
            center={
                'lat': df_alocacoes['latitude_estacao'].mean(),
                'lon': df_alocacoes['longitude_estacao'].mean()
            },
            zoom=5,
            style='carto-positron'
        ),
        height=450,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    return fig