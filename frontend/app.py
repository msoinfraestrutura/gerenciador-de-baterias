import streamlit as st

from pages import visao_gerencial
from pages import (
    login,
    gerenciador_de_baterias,
    otimizador_de_baterias,
    motor_de_alocacoes,
    sobre,
    glossario
)
from services.api_client import (
    get_estacoes,
    #get_baterias,
    get_alocacoes,
    get_disponibilidade,
    get_trafego_faturamento,
    get_pontuacoes,
    get_features,
)
from services import init_session, clear_session


with open('style/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

init_session()

st.set_page_config(
    page_title='Gerenciador de Baterias',
    page_icon='img/logo.ico',
    layout='wide'
)

if not st.session_state.logged_in:
    pg = st.navigation(
        {
            'Acesso': [
                st.Page(login.show, title='Entrar', url_path='login'),
            ]
        }
    )
    pg.run()
    st.stop()

if 'data_preloaded' not in st.session_state:
    with st.spinner('Carregando dados...'):
        get_estacoes()
        #get_baterias()
        get_alocacoes()
        get_disponibilidade()
        get_trafego_faturamento()
        get_pontuacoes()
        get_features()
    st.session_state.data_preloaded = True
        
with st.sidebar:
    if st.button(
        'Sair',
        help='Sair do Aplicativo',
        width='stretch',
        key='btn_logout'
    ):
        clear_session()
        st.rerun()

menu_items = {
    '📊 Visões': [
        st.Page(visao_gerencial.show, title='Executivo', url_path='executivo'),
    ],
    '⚙️ Operacional': [
        st.Page(otimizador_de_baterias.show, title='Otimizador', url_path='otimizador'),
        st.Page(gerenciador_de_baterias.show, title='Gerenciador', url_path='gerenciador'),
    ]#,
    #'📝 Cadastros': [
    #    st.Page(cadastros_baterias.show, title='Baterias', url_path='cadastros_baterias')
    #],
}

if st.session_state.get('username') == 'f252191':
    menu_items['🛠️ Configurações'] = [
        st.Page(motor_de_alocacoes.show, title='Motor de Alocações', url_path='motor_de_alocacoes')
    ]

menu_items['ℹ️ Info'] = [
    st.Page(sobre.show, title='Sobre', url_path='sobre'),
    st.Page(glossario.show, title='Glossário', url_path='glossario')
]

pg = st.navigation(menu_items)
pg.run()