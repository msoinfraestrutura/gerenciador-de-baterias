import pandas as pd
import numpy as np
import plotly.graph_objects as go


def cretae_scatter_map(
    df_estacoes_doadoras: pd.DataFrame,
    df_estacoes_receptoras: pd.DataFrame,
    zoom: int
) -> go.Figure:
    fig = go.Figure()
    #doadoras
    fig.add_trace(go.Scattermapbox(
        lat=df_estacoes_doadoras['latitude_estacao'],
        lon=df_estacoes_doadoras['longitude_estacao'],
        mode='markers',
        marker=dict(size=12, color='#1476ff', opacity=0.7),
        name='Doadoras',
        text=df_estacoes_doadoras['estacao'],
        customdata=np.stack((
            df_estacoes_doadoras['autonomia_media_horas'],
            df_estacoes_doadoras['restabelecimento_medio_horas'],
            df_estacoes_doadoras['delta']
        ), axis=-1),
        hovertemplate=(
            '<b>%{text}</b><br>'
            'Aut. Calculada: %{customdata[0]:.2f}h<br>'
            'Restab. Calculado: %{customdata[1]:.2f}h<br>'
            'Delta: %{customdata[2]:.2f}h'
            '<extra></extra>'
        )
    ))
    #receptoras
    fig.add_trace(go.Scattermapbox(
        lat=df_estacoes_receptoras['latitude_estacao'],
        lon=df_estacoes_receptoras['longitude_estacao'],
        mode='markers',
        marker=dict(size=12, color='#ef4444', opacity=0.6),
        name='Receptoras',
        text=df_estacoes_receptoras['estacao'],
        customdata=np.stack((
            df_estacoes_receptoras['autonomia_media_horas'],
            df_estacoes_receptoras['restabelecimento_medio_horas'],
            df_estacoes_receptoras['delta']
        ), axis=-1),
        hovertemplate=(
            '<b>%{text}</b><br>'
            'Aut. Calculada: %{customdata[0]:.2f}h<br>'
            'Restab. Calculado: %{customdata[1]:.2f}h<br>'
            'Delta: %{customdata[2]:.2f}h'
            '<extra></extra>'
        )
    ))
    fig.update_layout(
        font=dict(family='Poppins, sans-serif'),
        mapbox=dict(
            center={
                'lat': df_estacoes_receptoras['latitude_estacao'].mean(),
                'lon': df_estacoes_receptoras['longitude_estacao'].mean()
            },
            zoom=zoom,
            style='carto-positron'
        ),
        legend=dict(
            yanchor='bottom', y=0.02, xanchor='left', x=0.02,
            bgcolor='rgba(255,255,255,0.8)', borderwidth=1
        ),
        height=450,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    return fig


def create_scatter_map_station(
    df_estacoes_doadoras: pd.DataFrame,
    df_estacao_receptora: pd.Series,
    estacao_recomendada: str
) -> go.Figure:
    fig = go.Figure()
    #linhas entre doadoras e receptora
    for _, row in df_estacoes_doadoras.iterrows():
        is_rec = row['estacao'] == estacao_recomendada
        fig.add_trace(
            go.Scattermapbox(
                lat=[row['latitude_estacao'], df_estacao_receptora['latitude_estacao']],
                lon=[row['longitude_estacao'], df_estacao_receptora['longitude_estacao']],
                mode='lines',
                line=dict(
                    width=1.0 if is_rec else 0.5,
                    color='#1476ff'
                ),
                opacity=1.0 if is_rec else 0.3,
                showlegend=False,
                hoverinfo='skip'
            )
        )
    #doadoras
    fig.add_trace(
        go.Scattermapbox(
            lat=df_estacoes_doadoras['latitude_estacao'],
            lon=df_estacoes_doadoras['longitude_estacao'],
            mode='markers',
            marker=dict(size=20, color='#1476ff', opacity=1.0),
            text=df_estacoes_doadoras['estacao'],
            name='Doadoras',
            customdata=np.stack((
                df_estacoes_doadoras['autonomia_media_horas'],
                df_estacoes_doadoras['restabelecimento_medio_horas'],
                df_estacoes_doadoras['delta'],
                df_estacoes_doadoras['distancia']
            ), axis=-1),
            hovertemplate=(
                '&lt;b&gt;Doadora: %{text}&lt;/b&gt;&lt;br&gt;'
                'Aut. Calculada: %{customdata[0]:.2f}h&lt;br&gt;'
                'Restab. Calculado: %{customdata[1]:.2f}h&lt;br&gt;'
                'Delta: %{customdata[2]:.2f}h&lt;br&gt;'
                'Distância: %{customdata[3]:.2f}km'
                '&lt;extra&gt;&lt;/extra&gt;'
            )
        )
    )
    #receptora
    fig.add_trace(
        go.Scattermapbox(
            lat=[df_estacao_receptora['latitude_estacao']],
            lon=[df_estacao_receptora['longitude_estacao']],
            mode='markers',
            marker=dict(size=20, color='#ef4444', opacity=1.0),
            text=[df_estacao_receptora['estacao']],
            name='Receptora',
            customdata=np.stack((
                [df_estacao_receptora['autonomia_media_horas']],
                [df_estacao_receptora['restabelecimento_medio_horas']],
                [df_estacao_receptora['delta']]
            ), axis=-1).reshape(1, -1),
            hovertemplate=(
                '&lt;b&gt;Receptora: %{text}&lt;/b&gt;&lt;br&gt;'
                'Aut. Calculada: %{customdata[0]:.2f}h&lt;br&gt;'
                'Restab. Calculado: %{customdata[1]:.2f}h&lt;br&gt;'
                'Delta: %{customdata[2]:.2f}h'
                '&lt;extra&gt;&lt;/extra&gt;'
            )
        )
    )
    fig.update_layout(
        font=dict(family='Poppins, sans-serif'),
        mapbox=dict(
            center={'lat': df_estacao_receptora['latitude_estacao'], 'lon': df_estacao_receptora['longitude_estacao']},
            zoom=7,
            style='carto-positron'
        ),
        showlegend=True,
        legend=dict(
            yanchor='bottom',
            y=0.02,
            xanchor='left',
            x=0.02,
            bgcolor='rgba(255,255,255,0.8)',
            borderwidth=1,
            font=dict(color='black', size=11)
        ),
        height=450,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    return fig


def create_bar_chart(
    df_ranking_estacoes_receptoras: pd.DataFrame
) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df_ranking_estacoes_receptoras['pontuacao'],
            y=df_ranking_estacoes_receptoras['estacao'],
            orientation='h',
            marker=dict(
                color='#ef4444',
                opacity=0.8
            ),
            customdata=np.stack((
                df_ranking_estacoes_receptoras['autonomia_media_horas'],
                df_ranking_estacoes_receptoras['restabelecimento_medio_horas'],
                df_ranking_estacoes_receptoras['delta']
            ), axis=-1),
            hovertemplate=(
                '<b>%{y}</b><br>'
                'Pontuação: %{x:.2f}<br>'
                'Aut. Calculada: %{customdata[0]:.2f}h<br>'
                'Restab. Calculado: %{customdata[1]:.2f}h<br>'
                'Delta: %{customdata[2]:.2f}h'
                '<extra></extra>'
            )
        )
    )
    fig.update_layout(
        font=dict(family='Poppins, sans-serif'),
        template='plotly_white',
        xaxis_title='Pontuação',
        yaxis_title=None,
        yaxis=dict(
            categoryorder='total ascending'
        ),
        height=450,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    return fig