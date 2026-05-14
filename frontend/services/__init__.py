from typing import Optional
import os
import streamlit as st


def init_session() -> None:
    '''
    Inicializa variáveis de sessão do Streamlit.

    Returns:
        None
    '''
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    if 'refresh_token' not in st.session_state:
        st.session_state.refresh_token = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'page' not in st.session_state:
        st.session_state.page = None


def clear_session() -> None:
    '''
    Limpa dados de autenticação da sessão.

    Returns:
        None
    '''
    st.session_state.access_token = None
    st.session_state.refresh_token = None
    st.session_state.username = None
    st.session_state.logged_in = False
    st.session_state.page = None


def set_session(
    access_token: str,
    refresh_token: str,
    username: str,
    page: Optional[str] = None
) -> None:
    '''
    Define dados de autenticação na sessão.

    Params:
        access_token (str): Token de acesso.
        refresh_token (str): Token de refresh.
        username (str): Usuário autenticado.
        page (str, optional): Página inicial.

    Returns:
        None
    '''
    st.session_state.access_token = access_token
    st.session_state.refresh_token = refresh_token
    st.session_state.username = username
    st.session_state.logged_in = True
    st.session_state.page = page


API_URL = os.getenv('API_URL', 'http://localhost:5001')