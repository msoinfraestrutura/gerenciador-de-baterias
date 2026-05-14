import pytest
from sqlalchemy.exc import IntegrityError


@pytest.mark.baterias
class TestPostBaterias:
    @pytest.mark.baterias
    def test_quando_cadastrar_bateria_com_token_valido_deve_retornar_201(self, client, monkeypatch):
        user_data = {'username': 'teste', 'password': 'teste'}
        client.post('/api/v1/auth/register', json=user_data)
        login = client.post('/api/v1/auth/login', json=user_data)
        token = login.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        payload = {
            'tecnologia': 'LITIO',
            'fabricante': 'TESTE',
            'tensao': '48V',
            'capacidade': 100,
            'preco': 2500
        }

        def mock_post(data):
            return {
                'id': 1,
                **data,
                'updated_at': '2026-04-23T10:00:00'
            }

        monkeypatch.setattr('api.routes.data.post_baterias', mock_post)

        response = client.post('/api/v1/data/baterias', json=payload, headers=headers)
        assert response.status_code == 201
        assert 'id' in response.get_json()

    @pytest.mark.baterias
    def test_quando_cadastrar_bateria_sem_token_deve_retornar_401(self, client):
        response = client.post('/api/v1/data/baterias', json={})
        assert response.status_code == 401

    @pytest.mark.baterias
    def test_quando_cadastrar_bateria_duplicada_deve_retornar_409(self, client, monkeypatch):
        user_data = {'username': 'teste', 'password': 'teste'}
        client.post('/api/v1/auth/register', json=user_data)
        login = client.post('/api/v1/auth/login', json=user_data)
        token = login.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        def mock_post(_):
            raise IntegrityError(None, None, None)

        monkeypatch.setattr('api.routes.data.post_baterias', mock_post)

        response = client.post('/api/v1/data/baterias', json={}, headers=headers)
        assert response.status_code == 409

    @pytest.mark.baterias
    def test_quando_ocorrer_erro_interno_no_post_baterias_deve_retornar_500(self, client, monkeypatch):
        user_data = {'username': 'teste', 'password': 'teste'}
        client.post('/api/v1/auth/register', json=user_data)
        login = client.post('/api/v1/auth/login', json=user_data)
        token = login.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        def mock_post(_):
            raise Exception('Erro forçado')

        monkeypatch.setattr('api.routes.data.post_baterias', mock_post)

        response = client.post('/api/v1/data/baterias', json={}, headers=headers)
        assert response.status_code == 500
        assert 'error' in response.get_json()


@pytest.mark.baterias
class TestPutBaterias:
    @pytest.mark.baterias
    def test_quando_atualizar_bateria_com_token_valido_deve_retornar_200(self, client, monkeypatch):
        user_data = {'username': 'teste', 'password': 'teste'}
        client.post('/api/v1/auth/register', json=user_data)
        login = client.post('/api/v1/auth/login', json=user_data)
        token = login.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        payload = {'preco': 3000}

        def mock_put(_, data):
            return {'id': 1, **data}

        monkeypatch.setattr('api.routes.data.put_baterias', mock_put)

        response = client.put('/api/v1/data/baterias/1', json=payload, headers=headers)
        assert response.status_code == 200
        assert 'id' in response.get_json()

    @pytest.mark.baterias
    def test_quando_atualizar_bateria_sem_token_deve_retornar_401(self, client):
        response = client.put('/api/v1/data/baterias/1', json={})
        assert response.status_code == 401

    @pytest.mark.baterias
    def test_quando_bateria_nao_existir_deve_retornar_404(self, client, monkeypatch):
        user_data = {'username': 'teste', 'password': 'teste'}
        client.post('/api/v1/auth/register', json=user_data)
        login = client.post('/api/v1/auth/login', json=user_data)
        token = login.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        def mock_put(_, __):
            raise ValueError('Bateria não encontrada')

        monkeypatch.setattr('api.routes.data.put_baterias', mock_put)

        response = client.put('/api/v1/data/baterias/99', json={}, headers=headers)
        assert response.status_code == 404

    @pytest.mark.baterias
    def test_quando_atualizar_bateria_duplicada_deve_retornar_409(self, client, monkeypatch):
        user_data = {'username': 'teste', 'password': 'teste'}
        client.post('/api/v1/auth/register', json=user_data)
        login = client.post('/api/v1/auth/login', json=user_data)
        token = login.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        def mock_put(_, __):
            raise IntegrityError(None, None, None)

        monkeypatch.setattr('api.routes.data.put_baterias', mock_put)

        response = client.put('/api/v1/data/baterias/1', json={}, headers=headers)
        assert response.status_code == 409

    @pytest.mark.baterias
    def test_quando_ocorrer_erro_interno_no_put_baterias_deve_retornar_500(self, client, monkeypatch):
        user_data = {'username': 'teste', 'password': 'teste'}
        client.post('/api/v1/auth/register', json=user_data)
        login = client.post('/api/v1/auth/login', json=user_data)
        token = login.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        def mock_put(_, __):
            raise Exception('Erro forçado')

        monkeypatch.setattr('api.routes.data.put_baterias', mock_put)

        response = client.put('/api/v1/data/baterias/1', json={}, headers=headers)
        assert response.status_code == 500
        assert 'error' in response.get_json()