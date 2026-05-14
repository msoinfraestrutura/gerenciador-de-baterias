import pandas as pd
import plotly.graph_objects as go


def create_line_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['pct_custo'],
        y=df['pct_ganho'],
        name='Alocações Otimizadas',
        customdata=df[['custo', 'ganho']]
    ))
    fig.add_trace(go.Scatter(
        x=[0, 100],
        y=[0, 100],
        name='Alocações Aleatórias'
    ))
    fig.update_traces(
        selector=dict(name='Alocações Otimizadas'),
        mode='lines',
        line=dict(color='#1476ff', width=4),
        fill='tozeroy',
        fillcolor='rgba(20, 118, 255, 0.1)',
        hovertemplate=(
            'Investimento: %{x:.2f}% (R$ %{customdata[0]:.2f})<br>'
            'Ganho: %{y:.2f}% (%{customdata[1]:.2f} h)<br>'
        )
    )
    fig.update_traces(
        selector=dict(name='Alocações Aleatórias'),
        line=dict(color='#cbd5e1', dash='dash')
    )
    fig.update_layout(
        xaxis_title='% Investimento',
        yaxis_title='% Ganho',
        template='plotly_white',
        height=450,
        margin=dict(l=0, r=0, t=20, b=0)
    )
    return fig