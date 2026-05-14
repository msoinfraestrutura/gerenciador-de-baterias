from typing import Tuple, Dict, Any, Optional
import requests
import streamlit as st
from . import clear_session, set_session, API_URL


def api_requester(
    method: str,
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None
) -> requests.Response:
    '''
    Realiza requisição autenticada à API com suporte a refresh de token.

    Params:
        method (str): Método HTTP (GET, POST, etc).
        endpoint (str): Endpoint da API.
        data (dict, optional): Payload da requisição.
        params (dict, optional): Parâmetros da requisição..

    Returns:
        requests.Response: Resposta da API.
    '''

    access_token = st.session_state.get('access_token')
    refresh_token = st.session_state.get('refresh_token')

    if not access_token:
        raise RuntimeError('Usuário não autenticado')

    url = f'{API_URL}{endpoint}'
    headers = {'Authorization': f'Bearer {access_token}'}

    response = requests.request(
        method,
        url,
        json=data,
        params=params,
        headers=headers,
        timeout=18000
    )

    if response.status_code == 401 and refresh_token:
        refresh_response = requests.post(
            f'{API_URL}/api/v1/auth/refresh',
            headers={'Authorization': f'Bearer {refresh_token}'},
            timeout=10
        )

        if refresh_response.status_code != 200:
            clear_session()
            st.rerun()

        new_access_token = refresh_response.json()['access_token']
        st.session_state.access_token = new_access_token

        headers['Authorization'] = f'Bearer {new_access_token}'
        response = requests.request(
            method,
            url,
            json=data,
            params=params,
            headers=headers,
            timeout=30
        )

    return response


def login(username: str, password: str) -> Tuple[bool, str | None]:
    '''
    Realiza login do usuário e inicializa a sessão.

    Params:
        usuario (str): Nome do usuário.
        senha (str): Senha do usuário.

    Returns:
        tuple: (sucesso, mensagem_erro)
    '''
    response = post_login(username, password)
    if response.status_code == 200:
        data = response.json()
        set_session(
            access_token=data['access_token'],
            refresh_token=data['refresh_token'],
            username=username,
            page='menu'
        )
        return True, None
    try:
        return False, response.json().get('error', 'Credenciais inválidas')
    except Exception:
        return False, 'Erro no servidor'


def post_login(username, password):
    '''
    Realiza autenticação do usuário na API.

    Params:
        usuario (str): Nome do usuário.
        senha (str): Senha do usuário.

    Returns:
        requests.Response: Resposta da API.
    '''
    return requests.post(
        f'{API_URL}/api/v1/auth/login',
        json={'username': username, 'password': password},
        timeout=10
    )


@st.cache_data(ttl=3000, show_spinner=False)
def get_estacoes():
    '''
    Obtém dados de estações.

    Returns:
        list: Lista de dicionários com dados de estações.
    '''
    response = api_requester(method='GET', endpoint='/api/v1/data/estacoes')
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=3000, show_spinner=False)
def get_baterias():
    '''
    Obtém dados de baterias.

    Returns:
        list: Lista de dicionários com dados de baterias.
    '''
    response = api_requester(method='GET', endpoint='/api/v1/data/baterias')
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=3000, show_spinner=False)
def get_autonomia_restabelecimento():
    '''
    Obtém dados de autonomia de restabelecimento.

    Returns:
        list: Lista de registros.
    '''
    response = api_requester(method='GET', endpoint='/api/v1/data/autonomia-restabelecimento')
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=3000, show_spinner=False)
def get_autonomia_inventario():
    '''
    Obtém dados de autonomia de inventário.

    Returns:
        list: Lista de registros.
    '''
    response = api_requester(method='GET', endpoint='/api/v1/data/autonomia-inventario')
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=3000, show_spinner=False)
def get_disponibilidade():
    '''
    Obtém dados de disponibilidade.

    Returns:
        list: Lista de registros.
    '''
    response = api_requester(method='GET', endpoint='/api/v1/data/disponibilidade')
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=3000, show_spinner=False)
def get_trafego_faturamento():
    '''
    Obtém dados de tráfego e faturamento.

    Returns:
        list: Lista de registros.
    '''
    response = api_requester(method='GET', endpoint='/api/v1/data/trafego-faturamento')
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=3000, show_spinner=False)
def get_pontuacoes():
    '''
    Obtém pontuações calculadas.

    Returns:
        list: Lista de registros.
    '''
    response = api_requester(method='GET', endpoint='/api/v1/data/pontuacoes')
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=3000, show_spinner=False)
def get_features():
    '''
    Obtém dataset de features.

    Returns:
        list: Lista de registros.
    '''
    response = api_requester(method='GET', endpoint='/api/v1/data/features')
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=3000, show_spinner=False)
def get_alocacoes():
    '''
    Obtém dados de alocações.

    Returns:
        list: Lista de registros.
    '''
    response = api_requester(method='GET', endpoint='/api/v1/data/alocacoes')
    response.raise_for_status()
    return response.json()


def post_baterias(payload: dict) -> dict:
    '''
    Cria novo registro de bateria.

    Params:
        payload (dict): Dados da bateria.

    Returns:
        dict: Resposta da API.
    '''
    response = api_requester(
        method='POST',
        endpoint='/api/v1/data/baterias',
        data=payload
    )
    response.raise_for_status()
    return response.json()


def put_baterias(id: int, payload: dict) -> dict:
    '''
    Atualiza registro de bateria.

    Params:
        id (int): ID da bateria.
        payload (dict): Dados atualizados.

    Returns:
        dict: Resposta da API.
    '''
    response = api_requester(
        method='PUT',
        endpoint=f'/api/v1/data/baterias/{id}',
        data=payload
    )
    response.raise_for_status()
    return response.json()


def run_load_data() -> Dict[str, Any]:
    '''
    Executa pipeline de carga de dados.

    Returns:
        dict: Resultado da execução.
    '''
    response = api_requester(
        method='POST',
        endpoint='/api/v1/engine/load-data'
    )
    response.raise_for_status()
    return response.json()


def run_feature_engineering() -> Dict[str, Any]:
    '''
    Executa engenharia de features.

    Returns:
        dict: Resultado da execução.
    '''
    response = api_requester(
        method='POST',
        endpoint='/api/v1/engine/feature-engineering'
    )
    response.raise_for_status()
    return response.json()


def run_training_data(config: Dict[str, Any]) -> Dict[str, Any]:
    '''
    Executa o motor de alocação.

    Params:
        config (dict): Configuração de baterias e investimento.

    Returns:
        dict: Resultado da execução.
    '''
    response = api_requester(
        method='POST',
        endpoint='/api/v1/engine/training-data',
        data=config
    )
    response.raise_for_status()
    return response.json()


def run_full_pipeline(config: Dict[str, Any]) -> Dict[str, Any]:
    '''
    Executa pipeline completo (load + features + engine).

    Params:
        config (dict): Configuração do processo.

    Returns:
        dict: Resultado consolidado.
    '''
    response = api_requester(
        method='POST',
        endpoint='/api/v1/engine/full-pipeline',
        data=config
    )
    response.raise_for_status()
    return response.json()