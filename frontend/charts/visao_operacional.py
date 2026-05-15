from typing import List, Dict, Tuple, Optional
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from . import TEXT_MAP, COLOR_MAP, format_number


def create_choropleth_map(
    df: pd.DataFrame, 
    geojson: Dict, 
    value: str, 
    title: str, 
    geocontext: str = 'uf', 
    uf: Optional[str] = None, 
    lat: float = -17, 
    lon: float = -54, 
    zoom: float = 3.2
) -> go.Figure:
    if geocontext == 'municipio':
        df_temp = df.copy()
        df_temp = df_temp.groupby('municipio').agg({f'{value}': 'mean'}).reset_index()
        df_temp[f'{value}_normalized'] = np.log(1 + df_temp[value])
        locations_temp = 'municipio'
        featureidkey_temp=  'properties.name'
        geojson_temp = {
            'type': 'FeatureCollection',
            'features': []
        }
        for feature in geojson.get('features', []):
            properties = feature.get('properties', {})
            uf_temp = properties.get('uf')
            if uf_temp == uf:
                geojson_temp['features'].append(feature)

    else:
        df_temp = df.copy()
        df_temp = df_temp.groupby('uf').agg({f'{value}': 'mean'}).reset_index()
        df_temp[f'{value}_normalized'] = np.log(1 + df_temp[value])
        locations_temp = 'uf'
        featureidkey_temp = 'id'
        geojson_temp = geojson
    
    hover_label = 'Município' if geocontext == 'municipio' else 'Estado'
    fig = px.choropleth_mapbox(
        data_frame=df_temp,
        geojson=geojson_temp,
        locations=locations_temp,
        color=f'{value}_normalized',
        featureidkey=featureidkey_temp,
        color_continuous_scale=px.colors.sequential.YlOrRd,
        mapbox_style='carto-darkmatter',
        zoom=zoom,
        center={'lat': lat, 'lon': lon},
        hover_name=geocontext,
        custom_data=[value],
        opacity=.3
    )
    fig.update_traces(
        hovertemplate=(
            f'<b>{hover_label}: %{{hovertext}}</b><br>'
            'Tempo Médio: %{customdata[0]:.2f}h<br>'
        )
    )
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(
                family='Roboto',
                weight='bold'
            )
        ),
        font=dict(
            family='Roboto' 
        ),
        coloraxis_showscale=False,
        legend=dict(
            title=None, 
            traceorder='normal', 
            font=dict(
                size=12,
                color='#F0F0F5'
            ),
            orientation='h',
            yanchor='bottom',  
            y=1,      
            xanchor='right',  
            x=1
        ),
        height=1000,
    )
    return fig


def create_scatter_map(
    df: pd.DataFrame, 
    category: str, 
    custom_values: List, 
    title: str, 
    lat: float = -17, 
    lon: float = -54, 
    zoom: float = 2.8, 
    marker_size: float = 8
) -> go.Figure:
    fig = px.scatter_mapbox(
        data_frame=df.sort_values(category, ascending=False),
        lat='latitude_estacao',
        lon='longitude_estacao',
        color=category,
        color_discrete_map=COLOR_MAP,
        size=[marker_size] * len(df),
        size_max=marker_size,
        zoom=zoom,
        center={'lat': lat, 'lon': lon},
        mapbox_style='carto-darkmatter',
        hover_name='estacao',
        custom_data=custom_values,
    )
    fig.update_traces(
        hovertemplate=(
            'Estação: %{hovertext}<br><br>'
            'Autonomia (hrs): %{customdata[0]:.2f}<br>'
            'Restabelecimento (hrs): %{customdata[1]:.2f}'
        ),
        opacity=0.8
    )
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor='center',
            font=dict(
                family='Roboto',
                weight='bold',
                size=16
            )
        ),
        font=dict(
            family='Roboto' 
        ), 
        legend=dict(
            title=None,
            traceorder='normal',
            font=dict(
                size=12,
                color='#F0F0F5'
            ),
            orientation='h',
            yanchor='bottom',
            y=1,
            xanchor='right',
            x=1
        ),
        height=700,
        margin=dict(l=50, r=50, b=125, t=125)
    )
    return fig


def create_stacked_column(
    df: pd.DataFrame, 
    category: str, 
    stacked_category: str, 
    value: str, 
    custom_value: str, 
    title: str, 
    order: Optional[str] = None
) -> go.Figure:
    ordered_df = df[df[stacked_category] == order].sort_values(by=value, ascending=False)
    ordered_categories = ordered_df[category].tolist()
    df['custom_value_formatted'] = df[custom_value].apply(format_number)
    fig = px.bar(
        data_frame=df,
        x=category,
        y=value,
        text=value,
        color=stacked_category,
        color_discrete_map=COLOR_MAP,
        custom_data=['custom_value_formatted']
    )
    fig.update_traces(
        hovertemplate=(
            f'{TEXT_MAP[category]}: %{{x}}<br><br>'
            f'{TEXT_MAP[value]}: %{{y}}<br>'
            f'{TEXT_MAP[custom_value]}: %{{customdata[0]}}<br>'
        ),
        textposition='outside',
        textfont_size=16,
        textfont_color='#FFFFFF',
        opacity=0.8,
    )
    fig.update_layout(
        barmode='stack',
        title=dict(
            text=title,
            x=0.5,
            xanchor='center',
            font=dict(
                family='Roboto',
                weight='bold',
                size=16
            ),
        ),
        font=dict(
            family='Roboto'
        ),
        coloraxis_showscale=False,
        xaxis=dict(
            title=TEXT_MAP[category],
            categoryorder='array', 
            categoryarray=ordered_categories,
            type='category',
            tickangle=-45
        ),
        yaxis=dict(
            visible=True,
            showticklabels=True,
            showgrid=False,
            title=TEXT_MAP[value]
        ),
        showlegend=True,
        legend=dict(
            font=dict(size=12),
            title=None,
            orientation='h',
            yanchor='bottom',
            y=1.05,
            xanchor='right',
            x=1
        ),
        paper_bgcolor='#2A2A2A',
        plot_bgcolor='#2A2A2A',
        height=550,
        margin=dict(l=50, r=50, b=125, t=125)
    )
    return fig


def create_column_line(
    df: pd.DataFrame, 
    category: str, 
    column_value: str, 
    line_value: str, 
    title: str
) -> go.Figure:
    fig = px.bar(
        data_frame=df,
        x=category,
        y=column_value,
        text_auto=True,
        color=category,
        color_discrete_map=COLOR_MAP
    )
    fig.add_trace(
        go.Scatter(
            x=df[category],
            y=df[line_value],
            mode='lines+markers+text',
            name=f'{TEXT_MAP[category]} (hrs)',
            yaxis='y2',
            marker=dict(size=8, color='#FFC000'),
            line=dict(width=1, color='#FFC000'),
            text=df[line_value],
            textposition='top center', 
            textfont=dict(color='#FFFFFF', size=14),
            hovertemplate=(
                f'{TEXT_MAP[category]}: %{{x}}<br><br>'
                f'{TEXT_MAP[line_value]}: %{{y}}'
            )
        )
    )
    fig.update_traces(
        hovertemplate=(
            f'{TEXT_MAP[category]}: %{{x}}<br><br>'
            f'{TEXT_MAP[column_value]}: %{{y}}'
        ),
        textposition='outside',
        textfont=dict(color='#FFFFFF', size=14),
        selector=dict(type='bar'),
        opacity=0.8,
    )
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor='center',
            font=dict(
                family='Roboto',
                weight='bold',
                size=16
            )
        ),
        font=dict(
            family='Roboto'
        ),
        coloraxis_showscale=False,
        xaxis=dict(
            title=TEXT_MAP[category],
            tickangle=-45,
            type='category'
        ),
        yaxis=dict(
            visible=True,
            showticklabels=True,
            showgrid=False,
            title=TEXT_MAP[column_value]
        ),
        yaxis2=dict(
            visible=True,
            title=TEXT_MAP[line_value],
            overlaying='y',
            side='right',
            showgrid=False
        ),
        showlegend=False,
        paper_bgcolor='#2A2A2A',
        plot_bgcolor='#2A2A2A',
        height=550,
        margin=dict(l=50, r=50, b=125, t=125)
    )
    return fig


def create_column(
    df: pd.DataFrame, 
    category: str, 
    value: str, 
    title: str, 
    filter_column: str, 
    custom_value: Optional[str] = None
) -> go.Figure:
    df_filtered = df
    if custom_value:
        df_filtered = df[df[filter_column] == custom_value]
    fig = px.bar(
        data_frame=df_filtered,
        x=category,
        y=value,
        text_auto=True,
        color=filter_column,
        color_discrete_map=COLOR_MAP
    )
    fig.update_traces(
        hovertemplate=(
            f'{TEXT_MAP[category]}: %{{x}}<br><br>'
            f'{TEXT_MAP[value]}: %{{y}}<br>'
        ),
        textposition='outside',
        textfont_size=12,
        textfont_color='#FFFFFF',
        opacity=0.8,
    )
    fig.update_layout(
        barmode='group',
        title=dict(
            text=title,
            x=0.5,
            xanchor='center',
            font=dict(
                family='Roboto',
                weight='bold',
                size=16
            )
        ),
        font=dict(
            family='Roboto'
        ),
        coloraxis_showscale=False,
        xaxis=dict(
            title=TEXT_MAP[category],
            categoryorder='total descending',
            tickangle=-45
        ),
        yaxis=dict(
            title=TEXT_MAP[value],
            visible=True,
            showticklabels=False,
            showgrid=False,
            range=[98, 100]
        ),
        showlegend=True,
        legend=dict(
            font=dict(size=12),
            title=None,
            orientation='h',
            yanchor='bottom',
            y=1.05,
            xanchor='right',
            x=1
        ),
        paper_bgcolor='#2A2A2A',
        plot_bgcolor='#2A2A2A',
        height=550,
        margin=dict(l=50, r=50, b=125, t=125)
    )
    return fig


def create_pie(
    df: pd.DataFrame, 
    category: str, 
    value: str, 
    title: str
) -> go.Figure:
    fig = px.pie(
        data_frame=df, 
        values=value, 
        names=category,
        color=category,
        color_discrete_map=COLOR_MAP,
        custom_data=[category, value]
    )
    fig.update_traces(
        textposition='outside', 
        textinfo='percent+label+value',
        texttemplate='%{label}<br>%{value:d}<br>%{percent}',
        hole=.8,
        hovertemplate=(
            f'{TEXT_MAP[category]}: %{{label}}<br><br>'
            'Quantidade: %{value:d}<br>'
            'Participação: %{percent:.2%}'
        ),
        opacity=0.8,
        marker=dict(
            line=dict(
                color='#2A2A2A',  
                width=3           
            )
        ),
        textfont=dict(
            size=14,  
            color='white'
        )
    )
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor='center',
            font=dict(
                family='Roboto',
                weight='bold',
                 size=16
            )
        ),
        font=dict(
            family='Roboto'
        ),
        showlegend=False,
        paper_bgcolor='#2A2A2A',
        plot_bgcolor='#2A2A2A',
        height=550,
        margin=dict(l=50, r=50, b=100, t=125)
    )
    return fig
    

def create_multiple_lines(
    df: pd.DataFrame, 
    category: str, 
    values: List, 
    custom_values: List, 
    title: str, 
    aim: float = 99.65
) -> go.Figure:
    line_styles = {
        'disponibilidade': {'color': '#B61F2E', 'name': TEXT_MAP['disponibilidade']},      
        'disponibilidade_parcial': {'color': '#FFC000', 'name': TEXT_MAP['disponibilidade_parcial']},
        'disponibilidade_energia': {'color': '#00FF00', 'name': TEXT_MAP['disponibilidade_energia']}             
    }
    custom_map = dict(zip(values, custom_values))
    fig = go.Figure()
    for col in values:
        if col in line_styles:
            style = line_styles[col]
            labels = [f'{y_val:.2f}' if isinstance(y_val, (int, float)) else str(y_val) for y_val in df[col]]
            specific_custom_col = custom_map.get(col)
            custom_data_for_trace = df[specific_custom_col].values if specific_custom_col else [] 
            fig.add_trace(
                go.Scatter(
                    x=df[category],
                    y=df[col],
                    mode='lines+markers+text',
                    name=style['name'],
                    customdata=custom_data_for_trace,
                    line=dict(width=2, color=style['color']),
                    marker=dict(size=8, symbol='circle'),
                    text=labels,
                    textposition='top center',
                    textfont=dict(size=12, color=style['color']),
                    hovertemplate=(
                        f'{TEXT_MAP[category]}: %{{x}}<br><br>'
                        f'{style["name"]}: %{{y:.2f}}<br>'
                        f'Margem (%): %{{customdata:.2f}}<br>'
                    )
                )
            )
    fig.add_hline(
        y=aim, 
        line_dash='dash', 
        line_color='#A0A0A0',  
        line_width=1,
        annotation_text=aim,
        annotation_position='top right',
        annotation_font=dict(size=12, color='#A0A0A0')
    )
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor='center',
            font=dict(
                family='Roboto', 
                weight='bold', 
                color='#FFFFFF',
                size=16
            )
        ),
        font=dict(family='Roboto', color='#FFFFFF'),
        xaxis=dict(
            title=TEXT_MAP[category],
            tickangle=-45,
            showgrid=False,
            type='category' 
        ),
        yaxis=dict(
            title='% Disponibilidade',
            visible=True,
            showticklabels=True,
            showgrid=True,
            gridcolor='rgba(160, 160, 160, 0.2)'
        ),
        legend=dict(
            font=dict(size=12),
            title=None,
            orientation='h',
            yanchor='bottom',
            y=1.05,
            xanchor='right',
            x=1
        ),
        paper_bgcolor='#2A2A2A',
        plot_bgcolor='#2A2A2A',
        height=550,
        margin=dict(l=50, r=50, b=125, t=125)
    )
    return fig


def create_overlaped_lines(
    df: pd.DataFrame, 
    category: str, 
    values: Tuple[str, str],
    title: str
) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df[category],
            y=df[values[0]],
            mode='lines+markers+text', 
            name=TEXT_MAP[values[0]],
            line=dict(color='#0096AA', width=2),
            marker=dict(size=8, symbol='circle'),
            text=df[values[0]].round(2),
            textposition='top center',
            textfont=dict(size=12),
            hovertemplate=(
                f'{TEXT_MAP[category]}: %{{x}}<br><br>'
                f'{TEXT_MAP[values[0]]}: %{{y:.2f}}<br>'
            )
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df[category],
            y=df[values[1]],
            mode='lines+markers+text',
            name=TEXT_MAP[values[1]],
            line=dict(color='#FFA500', dash='dash', width=2),
            marker=dict(size=8, symbol='circle'),
            text=df[values[1]].round(2),
            textposition='top center',
            textfont=dict(size=12),
            yaxis='y2', 
            hovertemplate=(
                f'{category}: %{{x}}<br><br>'
                f'{TEXT_MAP[values[1]]}: %{{y:.2f}}<br>'
            )
        )
    )
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor='center',
            font=dict(family='Roboto', weight='bold', color='#FFFFFF'),
            size=16
        ),
        font=dict(family='Roboto', color='#FFFFFF'),
        xaxis=dict(
            title=TEXT_MAP[category],
            tickangle=-45,
            showgrid=False,
            type='category' 
        ),
        yaxis=dict(
            title='Restabelecimento de Energia (hrs)',
            visible=True,
            showticklabels=True,
            showgrid=True,
            gridcolor='rgba(160, 160, 160, 0.2)'
        ),
        yaxis2=dict(
            title='Disponibilidade (%)',
            visible=True,
            overlaying='y',
            side='right', 
            showticklabels=True,
            showgrid=True,
            gridcolor='rgba(160, 160, 160, 0.2)'
        ),
        legend=dict(
            font=dict(size=12),
            title=None,
            orientation='h',
            yanchor='bottom',
            y=1.05,
            xanchor='right',
            x=1
        ),
        paper_bgcolor='#2A2A2A',
        plot_bgcolor='#2A2A2A',
        height=550,
        margin=dict(l=50, r=70, b=125, t=125)
    )
    return fig


def create_scatter(
    df: pd.DataFrame, 
    x: str, 
    y: str, 
    color: str, 
    title: str, 
    custom_value: Optional[str] = None
) -> go.Figure:
    if not custom_value:
        custom_value = y
    fig = px.scatter(
        data_frame=df, 
        x=x,
        y=y, 
        color=color,
        size=custom_value, 
        hover_name=color,
    )
    fig.update_traces(
        hovertemplate=(
            f'{TEXT_MAP[color]}: %{{hovertext}}<br><br>'
            f'{TEXT_MAP[x]}: %{{x:.2f}}<br>'
            f'{TEXT_MAP[y]}: %{{y:.2f}}<br>'
        )
    )
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor='center',
            font=dict(
                family='Roboto', 
                weight='bold', 
                color='#FFFFFF',
                size=16
            )
        ),
        font=dict(family='Roboto', color='#FFFFFF'),
        xaxis=dict(
            title=TEXT_MAP[x],
            showgrid=True,
            gridcolor='rgba(160, 160, 160, 0.2)'
        ),
        yaxis=dict(
            title=TEXT_MAP[y],
            showgrid=True,
            gridcolor='rgba(160, 160, 160, 0.2)'
        ),
        legend=dict(
            font=dict(size=12),
            title=None,
            orientation='h',
            yanchor='bottom',
            y=1.05,
            xanchor='right',
            x=1
        ),
        paper_bgcolor='#2A2A2A',
        plot_bgcolor='#2A2A2A',
        height=550,
        margin=dict(l=50, r=50, b=125, t=125),
    )
    return fig


def create_scatter_lines(
    df: pd.DataFrame, 
    x: str, 
    y: str, 
    color: str,
    title: str, 
    custom_column: Optional[str] = None, 
    custom_value: Optional[str] = None
) -> go.Figure:
    df_temp = df.copy()
    if custom_value:
        df_temp = df[df[custom_column] == custom_value]
    
    df_temp['x_formatted'] = df_temp[x].apply(format_number)
    df_temp['y_formatted'] = df_temp[y].apply(format_number)
    
    median_x = df_temp[x].median()
    median_y = df_temp[y].median()

    q1_df = df_temp[(df_temp[x] < median_x) & (df_temp[y] > median_y)]
    q1_x, q1_y = q1_df[x].sum(), q1_df[y].sum()

    q2_df = df_temp[(df_temp[x] >= median_x) & (df_temp[y] > median_y)]
    q2_x, q2_y = q2_df[x].sum(), q2_df[y].sum()

    q3_df = df_temp[(df_temp[x] < median_x) & (df_temp[y] <= median_y)]
    q3_x, q3_y = q3_df[x].sum(), q3_df[y].sum()

    q4_df = df_temp[(df_temp[x] >= median_x) & (df_temp[y] <= median_y)]
    q4_x, q4_y = q4_df[x].sum(), q4_df[y].sum()

    x_min, x_max = df_temp[x].min(), df_temp[x].max()
    y_min, y_max = df_temp[y].min(), df_temp[y].max()

    fig = px.scatter(
        data_frame=df_temp,
        x=x,
        y=y, 
        color=color,
        size=y,
        hover_name=color,
        hover_data=['x_formatted', 'y_formatted']
    )
    
    fig.add_hline(y=median_y, line_dash="dash", line_color="#FFC000", line_width=1)
    fig.add_vline(x=median_x, line_dash="dash", line_color="#FFC000", line_width=1)

    # Anotações (Mantidas conforme sua lógica de posicionamento)
    fig.add_annotation(
        x=(x_min + median_x) / 2, y=(median_y + y_max) / 2,
        text=f'<b>Q1</b><br>Ganho (hrs): {format_number(q1_y)}<br>Custo (R$): {format_number(q1_x)}',
        showarrow=False, font=dict(size=12, color='#FFFFFF'), opacity=0.8
    )
    fig.add_annotation(
        x=(median_x + x_max) / 2, y=(median_y + y_max) / 2,
        text=f'<b>Q2</b><br>Ganho (hrs): {format_number(q2_y)}<br>Custo (R$): {format_number(q2_x)}',
        showarrow=False, font=dict(size=12, color='#FFFFFF'), opacity=0.8
    )
    fig.add_annotation(
        x=(x_min + median_x) / 2, y=(y_min + median_y) / 2,
        text=f'<b>Q3</b><br>Ganho (hrs): {format_number(q3_y)}<br>Custo (R$): {format_number(q3_x)}',
        showarrow=False, font=dict(size=12, color='#FFFFFF'), opacity=0.8
    )
    fig.add_annotation(
        x=(median_x + x_max) / 2, y=(y_min + median_y) / 2,
        text=f'<b>Q4</b><br>Ganho (hrs): {format_number(q4_y)}<br>Custo (R$): {format_number(q4_x)}',
        showarrow=False, font=dict(size=12, color='#FFFFFF'), opacity=0.8
    )

    fig.update_traces(
        marker=dict(sizemin=10, line=dict(width=0)),
        hovertemplate=(
            f'{TEXT_MAP.get(color, color)}: %{{hovertext}}<br><br>'
            f'{TEXT_MAP[x]}: %{{customdata[0]}}<br>'
            f'{TEXT_MAP[y]}: %{{customdata[1]}}<br>'
        ),
        opacity=0.8
    )

    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center', font=dict(family='Roboto', weight='bold', color='#FFFFFF', size=16)),
        font=dict(family='Roboto', color='#FFFFFF'),
        xaxis=dict(title=TEXT_MAP.get(x, x), showgrid=True, gridcolor='rgba(160, 160, 160, 0.2)'),
        yaxis=dict(title=TEXT_MAP.get(y, y), showgrid=True, gridcolor='rgba(160, 160, 160, 0.2)'),
        showlegend=False,
        paper_bgcolor='#2A2A2A',
        plot_bgcolor='#2A2A2A',
        height=550,
        margin=dict(l=50, r=50, b=125, t=125),
    )
    return fig


def create_pareto(
    df: pd.DataFrame, 
    category: str, 
    column_value: str, 
    line_value: str, 
    custom_value: str, 
    title: str
) -> go.Figure:
    fig = px.bar(
        data_frame=df,
        x=category,
        y=column_value,
        text_auto=True,
        color=category,
        color_discrete_map=COLOR_MAP
    )
    fig.add_trace(
        go.Scatter(
            x=df[category],
            y=df[line_value],
            mode='lines+markers+text',
            name='Acumulado (%)',
            yaxis='y2',
            marker=dict(size=8, color='#FFC000'),
            line=dict(width=1, color='#FFC000'),
            text=df[line_value].apply(lambda x: f'{x:.2f}%'),
            textposition='top center', 
            textfont=dict(color='#FFFFFF', size=12),
            customdata=df[[custom_value]].values,
            hovertemplate=(
                f'{TEXT_MAP[category]}: %{{x}}<br><br>'
                'Participação: %{customdata[0]:.2%}'
            )
        )
    )
    for trace in fig.data:
        if trace.type == 'bar':
            trace.showlegend = False
    fig.update_traces(
        hovertemplate=(
            f'{TEXT_MAP[category]}: %{{x}}<br><br>'
            f'{TEXT_MAP[column_value]}: %{{y}}'
        ),
        textposition='outside',
        textfont_size=12,
        textfont_color='#FFFFFF',
        selector=dict(type='bar'),
        opacity=0.8,
    )
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor='center',
            font=dict(
                family='Roboto',
                weight='bold'
            )
        ),
        font=dict(
            family='Roboto'
        ),
        legend=dict(
            title_text=None
        ),
        coloraxis_showscale=False,
        xaxis=dict(
            title=TEXT_MAP[category],
            tickangle=-45,
            type='category'
        ),
        yaxis=dict(
            visible=True,
            showticklabels=False,
            showgrid=False,
            title=TEXT_MAP[column_value]
        ),
        yaxis2=dict(
            visible=False,
            title=TEXT_MAP[line_value],
            overlaying='y',
            side='right',
            showgrid=False
        ),
        showlegend=True,
        paper_bgcolor='#2A2A2A',
        plot_bgcolor='#2A2A2A',
        height=550,
        margin=dict(l=50, r=50, b=125, t=125)
    )
    return fig


def create_radar(
    df_1: pd.DataFrame, 
    df_2: pd.DataFrame,
    r_col: str,
    theta_col_1: str,
    theta_col_2: str,
    name_1: str,
    name_2: str,
    title: str
) -> go.Figure:
    max_df1 = df_1[r_col].max()
    max_df2 = df_2[r_col].max()
    max_participation = max(max_df1, max_df2)
    if max_participation > 90:
        max_r = 100
    else:
        max_r = np.ceil(max_participation / 5) * 5 
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=df_1[r_col],
        theta=df_1[theta_col_1],
        fill='toself',
        name=name_1,
        line=dict(color='#00FF00', width=1),
        fillcolor='rgba(0, 255, 0, 0.15)',
        mode='lines+markers+text',
        text=df_1[r_col].apply(lambda x: f'{x:.2f}'), 
        textposition='top center',
        textfont=dict(
            size=14, 
            color='#A0A0A0' #00FF00
        ),
        hovertemplate='<b>Categoria:</b> %{theta}<br><b>Participação:</b> %{r:.2f}%<extra></extra>'
    ))
    fig.add_trace(go.Scatterpolar(
        r=df_2[r_col],
        theta=df_2[theta_col_2],
        fill='toself',
        name=name_2,
        line=dict(color='#B61F2E', width=1),
        fillcolor='rgba(182, 31, 46, 0.3)',
        mode='lines+markers+text',
        text=df_2[r_col].apply(lambda x: f'{x:.2f}'),  
        textposition='top center',
        textfont=dict(
            size=14, 
            color='#A0A0A0' #B61F2E
        ),
        hovertemplate='<b>Categoria:</b> %{theta}<br><b>Participação:</b> %{r:.2f}%<extra></extra>'
    ))
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor='center',
            font=dict(
                family='Roboto',
                weight='bold',
                color='#FFFFFF',
                size=18
            )
        ),
        font=dict(
            family='Roboto',
            color='#FFFFFF'
        ),
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max_r],
                gridcolor='#A0A0A0',
                linecolor='#A0A0A0',
                tickfont=dict(color='#FFC000')
            ),
            angularaxis=dict(
                linecolor='#A0A0A0', 
                gridcolor='#A0A0A0',
                tickfont=dict(color='#FFFFFF', size=14)
            ),
            bgcolor='rgba(160, 160, 160, 0.1)'
        ),
        showlegend=True,
        legend=dict(
            font=dict(size=12),
            title=None,
            orientation='h',
            yanchor='bottom',
            y=1.05,
            xanchor='right',
            x=1
        ),
        paper_bgcolor='#2A2A2A',
        plot_bgcolor='#2A2A2A',
        height=700,
        margin=dict(l=50, r=50, b=150, t=150) 
    )
    return fig


def create_stacked_column_multiple_lines(
    df: pd.DataFrame, 
    category: str, 
    stacked_category: str, 
    bar_value: str, 
    line_value_1: str,
    line_value_2: str,
    title: str, 
    order: Optional[str] = None
) -> go.Figure:
    
    ordered_categories = None
    if order and order in df[stacked_category].unique():
        ordered_df = (
            df[df[stacked_category] == order]
            .sort_values(by=bar_value, ascending=False)
        )
        ordered_categories = ordered_df[category].tolist()
    df_line_mean_1 = df.groupby(category, as_index=False)[line_value_1].mean()
    df_line_mean_2 = df.groupby(category, as_index=False)[line_value_2].mean()

    if ordered_categories:
        for df_temp in [df_line_mean_1, df_line_mean_2]:
            df_temp[category] = pd.Categorical(
                df_temp[category], 
                categories=ordered_categories, 
                ordered=True
            )
        df_line_mean_1 = df_line_mean_1.sort_values(by=category)
        df_line_mean_2 = df_line_mean_2.sort_values(by=category)

    fig = go.Figure()
    for stack_cat in df[stacked_category].unique():
        df_bar_segment = df[df[stacked_category] == stack_cat].copy()
        
        hover_text_bar = (
            f'{TEXT_MAP[category]}: %{{x}}<br><br>'
            f'{TEXT_MAP[stacked_category]}: {stack_cat}<br>'
            f'{TEXT_MAP[bar_value]}: %{{y}}<br>'
        )
        
        fig.add_trace(
            go.Bar(
                x=df_bar_segment[category],
                y=df_bar_segment[bar_value],
                name=f'{stack_cat}',
                marker_color=COLOR_MAP.get(stack_cat),
                opacity=0.7,
                hovertemplate=hover_text_bar,
                text=df_bar_segment[bar_value], 
                textposition='outside', 
                textfont=dict(size=14, color='#FFFFFF'),
                legendgroup=stack_cat,
                showlegend=True
            )
        )
    hover_text_line_1 = (
        f'{TEXT_MAP[category]}: %{{x}}<br><br>'
        f'{TEXT_MAP[line_value_1]}: %{{y:.2f}}<br>'
    )
    
    fig.add_trace(
        go.Scatter(
            x=df_line_mean_1[category],
            y=df_line_mean_1[line_value_1],
            name=f'{TEXT_MAP[line_value_1]}',
            mode='lines+markers+text',
            marker=dict(size=8, symbol='circle', line=dict(width=1, color='#FFC000')), 
            line=dict(width=2, dash='dash', color='#FFC000'),
            hovertemplate=hover_text_line_1,
            text=df_line_mean_1[line_value_1].apply(lambda x: f'{x:.2f}'),
            textposition='top center',
            textfont=dict(color='#FFC000', size=14),
            yaxis='y2', # Vinculado ao eixo da direita
            showlegend=True
        )
    )
    hover_text_line_2 = (
        f'{TEXT_MAP[category]}: %{{x}}<br><br>'
        f'{TEXT_MAP[line_value_2]}: %{{y:.2f}}<br>'
    )
    
    fig.add_trace(
        go.Scatter(
            x=df_line_mean_2[category],
            y=df_line_mean_2[line_value_2],
            name=f'{TEXT_MAP[line_value_2]}',
            mode='lines+markers+text',
            marker=dict(size=8, symbol='circle', line=dict(width=1, color='#000000')),
            line=dict(width=2, dash='dash', color='#000000'),
            hovertemplate=hover_text_line_2,
            text=df_line_mean_2[line_value_2].apply(lambda x: f'{x:.2f}'),
            textposition='bottom center',
            textfont=dict(color='#000000', size=14),
            showlegend=True
        )
    )
    fig.update_layout(
        barmode='stack',
        title=dict(
            text=title,
            x=0.5,
            xanchor='center',
            font=dict(family='Roboto', weight='bold', size=16),
        ),
        font=dict(family='Roboto'),
        paper_bgcolor='#2A2A2A',
        plot_bgcolor='#2A2A2A',
        height=550,
        showlegend=True,
        legend=dict(
            font=dict(size=12),
            orientation='h',
            yanchor='bottom',
            y=1.05,
            xanchor='right',
            x=1
        ),
        xaxis=dict(
            title=TEXT_MAP[category],
            type='category', 
            tickangle=-45,
            categoryorder='array' if ordered_categories else 'trace', 
            categoryarray=ordered_categories if ordered_categories else None,
        ),
        yaxis=dict(
            title='% (0 - 100)',
            visible=True,
            showticklabels=True,
            showgrid=False,
            side='left'
        ),
        yaxis2=dict(
            title='% (98 - 100)',
            visible=True,
            overlaying='y', 
            showgrid=False,
            side='right',
            range=[98, 100]
        ),
        margin=dict(l=50, r=50, b=125, t=125)
    )
    return fig


def create_risk_heatmap(
    df: pd.DataFrame, 
    prob_labels: list, 
    imp_labels: list,
    title: str
) -> go.Figure:

    COLOR_MAP = [
        [1, 2, 3, 3], #muito crítico
        [0, 2, 3, 3], #crítico
        [0, 1, 2, 2], #severo
        [0, 0, 1, 2]  #moderado
    ]
    colorscale = [
        [0.0, '#FFEB3B'], 
        [0.33, '#FF9800'], 
        [0.66, '#E53935'], 
        [1.0, '#B71C1C']
    ]
    #criar o heatmap anotado
    fig = ff.create_annotated_heatmap(
        z=COLOR_MAP,
        x=prob_labels,
        y=imp_labels,
        annotation_text=df.values.astype(str),
        colorscale=colorscale,
        showscale=False
    )
    fig.update_traces(
        text=df.values.astype(str),
        hovertemplate=(
            'Impacto: %{y}<br>'
            'Probabilidade: %{x}<br>'
            'Quantidade: %{text}<extra></extra>'
        )
    ),
    fig.update_annotations(
        font=dict(
            family='Roboto',
            size=18,
            color='#000000', 
            weight='bold'
        )
    ),
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor='center',
            font=dict(family='Roboto', weight='bold', size=16),
        ),
        font=dict(family='Roboto'),
        paper_bgcolor='#2A2A2A',
        plot_bgcolor='#2A2A2A',
        xaxis=dict(
            side='top', 
            title=dict(text='Probabilidade', font=dict(size=16)), 
            tickfont_size=12,
            gridcolor='#444444'
        ),
        yaxis=dict(
            title=dict(text='Impacto', font=dict(size=16)), 
            tickfont_size=12,
            gridcolor='#444444',
            autorange='reversed'
        ),
        height=550,
        margin=dict(l=50, r=50, b=125, t=150)
    )
    return fig


def create_quadrant_heatmap(df, x_labels, y_labels, title):
    COLOR_MAP = [[3, 2], [1, 0] ]
    colorscale = [
        [0.0, '#E53935'], 
        [0.33, '#FFEB3B'],
        [0.66, '#FF9800'], 
        [1.0, '#2E7D32']
    ]
    text = [
        [
            f"<b>Q1</b><br>Quantidade: {int(df.loc['Q1', 'qtd'])}<br>Custo (R$): {format_number(df.loc['Q1', 'custo_total'])}<br>Ganho (hrs): {format_number(df.loc['Q1', 'ganho_total'])}",
            f"<b>Q2</b><br>Quantidade: {int(df.loc['Q2', 'qtd'])}<br>Custo (R$): {format_number(df.loc['Q2', 'custo_total'])}<br>Ganho (hrs): {format_number(df.loc['Q2', 'ganho_total'])}"
        ],
        [
            f"<b>Q3</b><br>Quantidade: {int(df.loc['Q3', 'qtd'])}<br>Custo (R$): {format_number(df.loc['Q3', 'custo_total'])}<br>Ganho (hrs): {format_number(df.loc['Q3', 'ganho_total'])}",
            f"<b>Q4</b><br>Quantidade: {int(df.loc['Q4', 'qtd'])}<br>Custo (R$): {format_number(df.loc['Q4', 'custo_total'])}<br>Ganho (hrs): {format_number(df.loc['Q4', 'ganho_total'])}"
        ]
    ]
    fig = ff.create_annotated_heatmap(
        z=COLOR_MAP,
        x=x_labels,
        y=y_labels, 
        annotation_text=text,
        colorscale=colorscale,
        showscale=False
    )
    fig.update_traces(
        hovertemplate=(
            '%{y}<br>'
            '%{x}<extra></extra>'
        )
    )
    fig.update_annotations(
        font=dict(
            family='Roboto', 
            size=16, 
            color='#000000'
        )
    ),
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor='center',
            font=dict(family='Roboto', weight='bold', size=16),
        ),
        font=dict(family='Roboto'),
        paper_bgcolor='#2A2A2A',
        plot_bgcolor='#2A2A2A',
        xaxis=dict(
            side='top', 
            title=dict(text='Custo', font=dict(size=14)), 
            tickfont_size=12,
            gridcolor='#444444'
        ),
        yaxis=dict(
            title=dict(text='Ganho', font=dict(size=14)), 
            tickfont_size=12,
            gridcolor='#444444',
            autorange='reversed'
        ),
        height=550,
        margin=dict(l=50, r=50, b=125, t=150)
    )
    return fig