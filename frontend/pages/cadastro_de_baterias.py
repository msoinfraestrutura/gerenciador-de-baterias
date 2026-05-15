import streamlit as st
import pandas as pd

from services.api_client import (
    get_baterias,
    post_baterias,
    put_baterias
)
from utils.helpers import format_number
from . import TECNOLOGIAS, FABRICANTES, TENSOES


def show() -> None:
    st.image('img/logo.svg', width=70)
    st.title('Cadastro de Baterias')

    df_baterias = pd.DataFrame(get_baterias())

    if not df_baterias.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric('Cadastradas', df_baterias['id'].nunique(), border=True)
        c2.metric('Fabricantes', df_baterias['fabricante'].nunique(), border=True)
        c3.metric(
            'Preço Médio (R$)',
            format_number(df_baterias['preco'].mean()),
            border=True
        )

    tab1, tab2 = st.tabs(['➕ Cadastrar', '✏️ Atualizar'])

    with tab1:
        st.subheader('Cadastrar')

        col1, col2 = st.columns(2)

        tecnologia = col1.selectbox(
            'Tecnologia',
            TECNOLOGIAS
        )

        fabricante = col2.selectbox(
            'Fabricante',
            FABRICANTES
        )

        col3, col4 = st.columns(2)

        tensao = col3.selectbox(
            'Tensão',
            TENSOES
        )

        capacidade = col4.number_input(
            'Capacidade (Ah)',
            min_value=0.0,
            step=1.0
        )

        preco = st.number_input(
            'Preço (R$)',
            min_value=0.0,
            step=0.10,
            format='%.2f'
        )

        if st.button('Cadastrar', type='primary', width='stretch'):
            if capacidade <= 0:
                st.warning('Preencha todos os campos obrigatórios.')
            else:
                try:
                    post_baterias({
                        'tecnologia': tecnologia,
                        'fabricante': fabricante,
                        'tensao': tensao,
                        'capacidade': capacidade,
                        'preco': float(preco)
                    })
                    get_baterias.clear()
                except Exception:
                    st.warning('Bateria já cadastrada ou erro na conexão.')
                else:
                    st.success('Bateria cadastrada com sucesso.')
                    st.rerun()

    with tab2:
        st.subheader('Atualizar')

        if df_baterias.empty:
            st.warning('Não há baterias cadastradas para atualizar.')
        else:
            bateria_map = {
                f'ID {r.id} | {r.fabricante} | {r.tecnologia} | '
                f'{r.tensao} | {r.capacidade}Ah': r.id
                for _, r in df_baterias.iterrows()
            }

            bateria_label = st.selectbox(
                'Selecione a bateria',
                options=list(bateria_map.keys())
            )

            if bateria_label:
                bateria_id = bateria_map[bateria_label]
                bateria = df_baterias[df_baterias['id'] == bateria_id].iloc[0]

                preco_upd = st.number_input(
                    'Preço (R$)',
                    min_value=0.0,
                    step=0.01,
                    format='%.2f',
                    value=float(bateria['preco']),
                    key=f'upd_preco_{bateria_id}'
                )

                with st.expander('🔧 Dados Técnicos'):
                    col1, col2 = st.columns(2)

                    tecnologia_upd = col1.selectbox(
                        'Tecnologia',
                        TECNOLOGIAS,
                        index=TECNOLOGIAS.index(bateria['tecnologia'])
                        if bateria['tecnologia'] in TECNOLOGIAS else 0,
                        key=f'upd_tecnologia_{bateria_id}'
                    )

                    fabricante_upd = col2.selectbox(
                        'Fabricante',
                        FABRICANTES,
                        index=FABRICANTES.index(bateria['fabricante'])
                        if bateria['fabricante'] in FABRICANTES else 0,
                        key=f'upd_fabricante_{bateria_id}'
                    )

                    col1, col2 = st.columns(2)

                    tensao_upd = col1.selectbox(
                        'Tensão',
                        TENSOES,
                        index=TENSOES.index(bateria['tensao'])
                        if bateria['tensao'] in TENSOES else 0,
                        key=f'upd_tensao_{bateria_id}'
                    )

                    capacidade_upd = col2.number_input(
                        'Capacidade (Ah)',
                        min_value=0.0,
                        step=1.0,
                        value=float(bateria['capacidade']),
                        key=f'upd_capacidade_{bateria_id}'
                    )

                if st.button(
                    'Atualizar',
                    type='primary',
                    width='stretch',
                    key=f'btn_upd_{bateria_id}'
                ):
                    if capacidade_upd <= 0:
                        st.warning('Preencha todos os campos obrigatórios.')
                    else:
                        try:
                            put_baterias(int(bateria_id), {
                                'tecnologia': tecnologia_upd,
                                'fabricante': fabricante_upd,
                                'tensao': tensao_upd,
                                'capacidade': capacidade_upd,
                                'preco': float(preco_upd)
                            })
                            get_baterias.clear()
                        except Exception:
                            st.error('Erro ao atualizar bateria.')
                        else:
                            st.success('Bateria atualizada com sucesso.')
                            st.rerun()

    st.divider()
    
    if not df_baterias.empty:
        st.subheader('Baterias Cadastradas')
        st.dataframe(
            df_baterias[
                ['id', 'fabricante', 'tecnologia', 'tensao',
                 'capacidade', 'preco', 'updated_at']
            ]
            .sort_values('id')
            .assign(
                preco=lambda d: d['preco'].apply(format_number), 
                updated_at=lambda d: pd.to_datetime(d['updated_at']).dt.date
            )
            .rename(columns={
                'id': 'ID',
                'fabricante': 'Fabricante',
                'tecnologia': 'Tecnologia',
                'tensao': 'Tensão',
                'capacidade': 'Capacidade (Ah)',
                'preco': 'Preço (R$)',
                'updated_at': 'Última Atualização'
            }),
            hide_index=True,
            width='stretch'
        )
    else:
        st.warning('Não há baterias cadastradas.')