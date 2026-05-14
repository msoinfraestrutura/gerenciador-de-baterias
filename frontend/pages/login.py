import streamlit as st
from services.api_client import login


def show() -> None:
    '''Conteúdo da página de login'''
    _, col2, _ = st.columns([.2, .6, .2])
    with col2:
        st.image('img/logo.svg', width=70)
        st.title('Gerenciador de Baterias')
        st.subheader('Entrar')

        with st.form('form_entrar', clear_on_submit=True):
            user = st.text_input('Usuário')
            password = st.text_input('Senha', type='password')

            _, col_btn = st.columns([.7, .3])
            with col_btn:
                btn_login = st.form_submit_button('Entrar', width='stretch')

        if btn_login:
            success, error_msg = login(user, password)

            if success:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error(error_msg or 'Falha no login')