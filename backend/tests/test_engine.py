import json
import pytest


@pytest.mark.engine
class TestEngineLoadData:
    @pytest.mark.load_data
    def test_quando_executar_load_data_com_token_valido_deve_retornar_200(self, client, monkeypatch):
        #given
        user_data = {'username': 'teste', 'password': 'teste'}
        client.post(
            '/api/v1/auth/register',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        login_response = client.post(
            '/api/v1/auth/login',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        token = login_response.get_json()['access_token']
        headers = {
            'Authorization': f'Bearer {token}'
        }

        def mock_ok():
            return None

        monkeypatch.setattr(
            'api.routes.engine.run_load_data',
            mock_ok
        )
        
        #when
        response = client.post(
            '/api/v1/engine/load-data',
            headers=headers
        )
        result = response.get_json()
        #then
        assert response.status_code == 200
        assert 'msg' in result
        assert isinstance(result['msg'], str)
        
    @pytest.mark.load_data
    def test_quando_executar_load_data_sem_token_deve_retornar_401(self, client):
        #when
        response = client.post('/api/v1/engine/load-data')
        #then
        assert response.status_code == 401
        
    @pytest.mark.load_data
    def test_quando_ocorrer_erro_no_load_data_deve_retornar_500(self, client, monkeypatch):
        #given
        user_data = {'username': 'teste', 'password': 'teste'}
        client.post(
            '/api/v1/auth/register',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        login_response = client.post(
            '/api/v1/auth/login',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        token = login_response.get_json()['access_token']
        headers = {
            'Authorization': f'Bearer {token}'
        }

        def mock_error():
            raise Exception('Erro forçado')

        monkeypatch.setattr(
            'api.routes.engine.run_load_data',
            mock_error
        )

        #when
        response = client.post(
            '/api/v1/engine/load-data',
            headers=headers
        )
        result = response.get_json()
        #then
        assert response.status_code == 500
        assert 'error' in result


@pytest.mark.engine
class TestEngineFeatureEngineering:
    @pytest.mark.feature_engineering
    def test_quando_executar_feature_engineering_com_token_valido_deve_retornar_200(self, client, monkeypatch):
        #given
        user_data = {'username': 'teste', 'password': 'teste'}
        client.post(
            '/api/v1/auth/register',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        login_response = client.post(
            '/api/v1/auth/login',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        token = login_response.get_json()['access_token']
        headers = {
            'Authorization': f'Bearer {token}'
        }

        def mock_ok():
            return {
                'scores': [],
                'features': []
            }

        monkeypatch.setattr(
            'api.routes.engine.run_feature_engineering',
            mock_ok
        )

        #when
        response = client.post(
            '/api/v1/engine/feature-engineering',
            headers=headers
        )
        result = response.get_json()
        #then
        assert response.status_code == 200
        assert 'scores' in result
        assert 'features' in result
        assert isinstance(result['scores'], list)
        assert isinstance(result['features'], list)
        
    @pytest.mark.feature_engineering
    def test_quando_executar_feature_engineering_sem_token_deve_retornar_401(self, client):
        #when
        response = client.post('/api/v1/engine/feature-engineering')
        #then
        assert response.status_code == 401
        
    
    @pytest.mark.feature_engineering
    def test_quando_ocorrer_erro_no_feature_engineering_deve_retornar_500(self, client, monkeypatch):
        #given
        user_data = {'username': 'teste', 'password': 'teste'}
        client.post(
            '/api/v1/auth/register',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        login_response = client.post(
            '/api/v1/auth/login',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        token = login_response.get_json()['access_token']
        headers = {
            'Authorization': f'Bearer {token}'
        }

        def mock_error():
            raise Exception('Erro forçado')

        monkeypatch.setattr(
            'api.routes.engine.run_feature_engineering',
            mock_error
        )

        #when
        response = client.post(
            '/api/v1/engine/feature-engineering',
            headers=headers
        )
        result = response.get_json()
        #then
        assert response.status_code == 500
        assert 'error' in result
        

@pytest.mark.engine
class TestEngineTrainingData:
    @pytest.mark.training_data
    def test_quando_executar_training_data_com_token_valido_deve_retornar_200(self, client, monkeypatch):
        #given
        user_data = {'username': 'teste', 'password': 'teste'}
        client.post(
            '/api/v1/auth/register',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        login_response = client.post(
            '/api/v1/auth/login',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        token = login_response.get_json()['access_token']
        headers = {
            'Authorization': f'Bearer {token}'
        }
        payload = {
            'baterias_disponiveis': {
                'TESTE': {'custo': 1000, 'ah': 100}
            },
            'investimento': 100000
        }

        def mock_ok(config=None):
            return []

        monkeypatch.setattr(
            'api.routes.engine.run_training_data',
            mock_ok
        )

        #when
        response = client.post(
            '/api/v1/engine/training-data',
            headers=headers,
            data=json.dumps(payload),
            content_type='application/json'
        )
        result = response.get_json()
        #then
        assert response.status_code == 200
        assert isinstance(result, list)
        
    @pytest.mark.training_data
    def test_quando_executar_training_data_sem_token_deve_retornar_401(self, client):
        #when
        response = client.post('/api/v1/engine/training-data')
        #then
        assert response.status_code == 401
        
    @pytest.mark.training_data
    def test_quando_ocorrer_erro_no_training_data_deve_retornar_500(self, client, monkeypatch):
        #given
        user_data = {'username': 'teste', 'password': 'teste'}
        client.post(
            '/api/v1/auth/register',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        login_response = client.post(
            '/api/v1/auth/login',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        token = login_response.get_json()['access_token']
        headers = {
            'Authorization': f'Bearer {token}'
        }

        def mock_error(config=None):
            raise Exception('Erro forçado')

        monkeypatch.setattr(
            'api.routes.engine.run_training_data',
            mock_error
        )

        #when
        response = client.post(
            '/api/v1/engine/training-data',
            headers=headers,
            data=json.dumps({})
        )
        result = response.get_json()
        #then
        assert response.status_code == 500
        assert 'error' in result


@pytest.mark.engine
class TestEngineRun:
    @pytest.mark.full_pipeline
    def test_quando_executar_run_com_token_valido_deve_retornar_200(self, client, monkeypatch):
        #given
        user_data = {'username': 'teste', 'password': 'teste'}
        client.post(
            '/api/v1/auth/register',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        login_response = client.post(
            '/api/v1/auth/login',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        token = login_response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        payload = {
            'baterias_disponiveis': {'TESTE': {'custo': 1000, 'ah': 100}},
            'investimento': 50000
        }

        #mock das três funções que compõem o pipeline
        monkeypatch.setattr('api.routes.engine.run_load_data', lambda: None)
        monkeypatch.setattr('api.routes.engine.run_feature_engineering', lambda: {})
        monkeypatch.setattr('api.routes.engine.run_training_data', lambda config=None: [{'id': 1}])
        
        #when
        response = client.post(
            '/api/v1/engine/full-pipeline', 
            headers=headers,
            data=json.dumps(payload),
            content_type='application/json'
        )
        result = response.get_json()
        #then
        assert response.status_code == 200
        assert 'message' in result or 'status' in result # depende de como você nomeou no return
        assert 'results' in result
        assert isinstance(result['results'], list)

    @pytest.mark.full_pipeline
    def test_quando_executar_run_sem_token_deve_retornar_401(self, client):
        #when
        response = client.post('/api/v1/engine/full-pipeline')
        #then
        assert response.status_code == 401

    @pytest.mark.full_pipeline
    def test_quando_ocorrer_erro_em_qualquer_etapa_do_run_deve_retornar_500(self, client, monkeypatch):
        #given
        user_data = {'username': 'teste', 'password': 'teste'}
        client.post('/api/v1/auth/register', data=json.dumps(user_data), content_type='application/json')
        login_response = client.post('/api/v1/auth/login', data=json.dumps(user_data), content_type='application/json')
        token = login_response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        #mockando um erro na primeira etapa
        def mock_error():
            raise Exception('Falha no pipeline')

        monkeypatch.setattr('api.routes.engine.run_load_data', mock_error)
        
        #when
        response = client.post(
            '/api/v1/engine/full-pipeline',
            headers=headers,
            data=json.dumps({})
        )
        result = response.get_json()
        #then
        assert response.status_code == 500
        assert 'error' in result