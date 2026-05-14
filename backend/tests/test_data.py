import json
import pytest


@pytest.mark.data
class TestEstacoes:
    @pytest.mark.estacoes
    def test_quando_listar_estacoes_com_token_valido_deve_retornar_200(self, client):
        #given
        user_data = {'username': 'teste', 'password': 'teste'}
        client.post('/api/v1/auth/register', data=json.dumps(user_data), content_type='application/json')
        login_response = client.post('/api/v1/auth/login', data=json.dumps(user_data), content_type='application/json')
        token = login_response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        #when
        response = client.get('/api/v1/data/estacoes', headers=headers)
        result = response.get_json()
        #then
        assert response.status_code == 200
        assert isinstance(result, list)

        if result:
            item = result[0]
            assert 'id' in item
            assert 'estacao' in item
            assert 'cd_ibge' in item
            assert 'uf' in item
            assert 'municipio' in item
            assert 'cluster' in item
            assert 'latitude_estacao' in item
            assert 'longitude_estacao' in item
            assert 'updated_at' in item

    @pytest.mark.estacoes
    def test_quando_listar_estacoes_sem_token_deve_retornar_401(self, client):
        #when
        response = client.get('/api/v1/data/estacoes')
        #then
        assert response.status_code == 401

    @pytest.mark.estacoes
    def test_quando_ocorrer_erro_interno_nas_estacoes_deve_retornar_500(self, client, monkeypatch):
        #given
        user_data = {'username': 'teste', 'password': 'teste'}
        client.post('/api/v1/auth/register', data=json.dumps(user_data), content_type='application/json')
        login_response = client.post('/api/v1/auth/login', data=json.dumps(user_data), content_type='application/json')
        token = login_response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        def mock_error():
            raise Exception('Erro forçado nas estações')

        monkeypatch.setattr('api.routes.data.get_estacoes', mock_error)

        #when
        response = client.get('/api/v1/data/estacoes', headers=headers)
        result = response.get_json()
        #then
        assert response.status_code == 500
        assert 'error' in result


@pytest.mark.data
class TestAutonomiaRestabelecimento:
    @pytest.mark.autonomia_restabelecimento
    def test_quando_listar_autonomia_com_token_valido_deve_retornar_200(self, client):
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
        #when
        response = client.get(
            '/api/v1/data/autonomia-restabelecimento',
            headers=headers
        )
        result = response.get_json()
        #then
        assert response.status_code == 200
        assert isinstance(result, list)

        if result:
            item = result[0]
            assert 'id' in item
            assert 'estacao' in item
            assert 'autonomia_media_horas' in item
            assert 'restabelecimento_medio_horas' in item
            assert 'tipo_autonomia' in item
            assert 'updated_at' in item
    
    @pytest.mark.autonomia_restabelecimento
    def test_quando_listar_autonomia_sem_token_deve_retornar_401(self, client):
        #when
        response = client.get('/api/v1/data/autonomia-restabelecimento')
        #then
        assert response.status_code == 401
    
    @pytest.mark.autonomia_restabelecimento
    def test_quando_ocorrer_erro_interno_deve_retornar_500(self, client, monkeypatch):
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
            'api.routes.data.get_autonomia_restabelecimento',
            mock_error
        )
        #when
        response = client.get(
            '/api/v1/data/autonomia-restabelecimento',
            headers=headers
        )
        result = response.get_json()
        #then
        assert response.status_code == 500
        assert 'error' in result

import json
import pytest


@pytest.mark.data
class TestAutonomiaInventario:
    @pytest.mark.autonomia_inventario
    def test_quando_listar_autonomia_inventario_com_token_valido_deve_retornar_200(self, client):
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
        #when
        response = client.get(
            '/api/v1/data/autonomia-inventario',
            headers=headers
        )
        result = response.get_json()
        #then
        assert response.status_code == 200
        assert isinstance(result, list)
        
        if result:
            item = result[0]
            assert 'id' in item
            assert 'estacao' in item
            assert 'autonomia_inventario_horas' in item
            assert 'updated_at' in item

    @pytest.mark.autonomia_inventario
    def test_quando_listar_autonomia_inventario_sem_token_deve_retornar_401(self, client):
        #when
        response = client.get('/api/v1/data/autonomia-inventario')
        #then
        assert response.status_code == 401

    @pytest.mark.autonomia_inventario
    def test_quando_ocorrer_erro_interno_em_autonomia_inventario_deve_retornar_500(self, client, monkeypatch):
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
            'api.routes.data.get_autonomia_inventario',
            mock_error
        )
        #when
        response = client.get(
            '/api/v1/data/autonomia-inventario',
            headers=headers
        )
        result = response.get_json()
        #then
        assert response.status_code == 500
        assert 'error' in result

@pytest.mark.data
class TestIndisponibilidades:
    @pytest.mark.indisponibilidades
    def test_quando_listar_indisponibilidades_com_token_valido_deve_retornar_200(self, client):
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
        #when
        response = client.get(
            '/api/v1/data/indisponibilidades',
            headers=headers
        )
        result = response.get_json()
        #then
        assert response.status_code == 200
        assert isinstance(result, list)

        if result:
            item = result[0]
            assert 'id' in item
            assert 'estacao' in item
            assert 'submit_date' in item
            assert 'clear_date' in item
            assert 'indisponibilidade_horas' in item
            assert 'updated_at' in item

    @pytest.mark.indisponibilidades
    def test_quando_listar_indisponibilidades_sem_token_deve_retornar_401(self, client):
        #when
        response = client.get('/api/v1/data/indisponibilidades')
        #then
        assert response.status_code == 401

    @pytest.mark.indisponibilidades
    def test_quando_ocorrer_erro_interno_deve_retornar_500(self, client, monkeypatch):
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
            'api.routes.data.get_indisponibilidades',
            mock_error
        )
        #when
        response = client.get(
            '/api/v1/data/indisponibilidades',
            headers=headers
        )
        result = response.get_json()
        #then
        assert response.status_code == 500
        assert 'error' in result        
        

@pytest.mark.data
class TestDisponibilidade:
    @pytest.mark.disponibilidade
    def test_quando_listar_disponibilidade_com_token_valido_deve_retornar_200(self, client):
        #given
        user_data = {'username': 'teste', 'password': 'teste'}
        client.post('/api/v1/auth/register', data=json.dumps(user_data), content_type='application/json')
        login_response = client.post('/api/v1/auth/login', data=json.dumps(user_data), content_type='application/json')
        token = login_response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        #when
        response = client.get('/api/v1/data/disponibilidade', headers=headers)
        result = response.get_json()
        #then
        assert response.status_code == 200
        assert isinstance(result, list)

        if result:
            item = result[0]
            fields = [
                'id', 'ano', 'estacao', 'disponibilidade', 'disponibilidade_parcial',
                'disponibilidade_energia', 'indisponibilidade_horas', 'indisponibilidade_parcial_horas',
                'indisponibilidade_energia_horas', 'indisponibilidade_energia',
                'diferenca_meta_disponibilidade', 'diferenca_meta_disponibilidade_parcial',
                'diferenca_meta_disponibilidade_energia', 'incidentes', 'incidentes_parcial',
                'incidentes_energia', 'updated_at'
            ]
            for field in fields:
                assert field in item

    @pytest.mark.disponibilidade
    def test_quando_listar_disponibilidade_sem_token_deve_retornar_401(self, client):
        #when
        response = client.get('/api/v1/data/disponibilidade')
        #then
        assert response.status_code == 401

    @pytest.mark.disponibilidade
    def test_quando_ocorrer_erro_interno_na_disponibilidade_deve_retornar_500(self, client, monkeypatch):
        #given
        user_data = {'username': 'teste', 'password': 'teste'}
        client.post('/api/v1/auth/register', data=json.dumps(user_data), content_type='application/json')
        login_response = client.post('/api/v1/auth/login', data=json.dumps(user_data), content_type='application/json')
        token = login_response.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        def mock_error():
            raise Exception('Erro forçado na disponibilidade')

        monkeypatch.setattr('api.routes.data.get_disponibilidade', mock_error)

        #when
        response = client.get('/api/v1/data/disponibilidade', headers=headers)
        result = response.get_json()
        #then
        assert response.status_code == 500
        assert 'error' in result


@pytest.mark.data
class TestPontuacoes:
    @pytest.mark.pontuacoes
    def test_quando_listar_pontuacoes_com_token_valido_deve_retornar_200(self, client):
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
        #when
        response = client.get(
            '/api/v1/data/pontuacoes',
            headers=headers
        )
        result = response.get_json()
        #then
        assert response.status_code == 200
        assert isinstance(result, list)

        if result:
            item = result[0]
            assert 'id' in item
            assert 'estacao' in item
            assert 'pontuacao_autonomia' in item
            assert 'pontuacao_trafego_dados' in item
            assert 'pontuacao_hierarquia' in item
            assert 'pontuacao_tmr' in item
            assert 'pontuacao_idade_bateria' in item
            assert 'pontuacao_faturamento' in item
            assert 'pontuacao_cliente' in item
            assert 'pontuacao' in item
            assert 'updated_at' in item

    @pytest.mark.pontuacoes
    def test_quando_listar_pontuacoes_sem_token_deve_retornar_401(self, client):
        #when
        response = client.get('/api/v1/data/pontuacoes')
        #then
        assert response.status_code == 401

    @pytest.mark.pontuacoes
    def test_quando_ocorrer_erro_interno_deve_retornar_500(self, client, monkeypatch):
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
            'api.routes.data.get_pontuacoes',
            mock_error
        )
        #when
        response = client.get(
            '/api/v1/data/pontuacoes',
            headers=headers
        )
        result = response.get_json()
        #then
        assert response.status_code == 500
        assert 'error' in result


@pytest.mark.data
class TestFeatures:
    @pytest.mark.features
    def test_quando_listar_features_com_token_valido_deve_retornar_200(self, client):
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
        #when
        response = client.get(
            '/api/v1/data/features',
            headers=headers
        )
        result = response.get_json()
        #then
        assert response.status_code == 200
        assert isinstance(result, list)

        if result:
            item = result[0]
            assert 'id' in item
            assert 'estacao' in item
            assert 'capacidade_baterias' in item
            assert 'carga' in item
            assert 'indisponibilidade_media_horas' in item
            assert 'pontuacao_hierarquia' in item
            assert 'pontuacao' in item
            assert 'updated_at' in item

    @pytest.mark.features
    def test_quando_listar_features_sem_token_deve_retornar_401(self, client):
        #when
        response = client.get('/api/v1/data/features')
        #then
        assert response.status_code == 401

    @pytest.mark.features
    def test_quando_ocorrer_erro_interno_deve_retornar_500(self, client, monkeypatch):
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
            'api.routes.data.get_features',
            mock_error
        )
        #when
        response = client.get(
            '/api/v1/data/features',
            headers=headers
        )
        result = response.get_json()
        #then
        assert response.status_code == 500
        assert 'error' in result


@pytest.mark.data
class TestAlocacoes:
    @pytest.mark.alocacoes
    def test_quando_listar_alocacoes_com_token_valido_deve_retornar_200(self, client):
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
        #when
        response = client.get(
            '/api/v1/data/alocacoes',
            headers=headers
        )
        result = response.get_json()
        #then
        assert response.status_code == 200
        assert isinstance(result, list)

        if result:
            item = result[0]
            assert 'id' in item
            assert 'estacao' in item
            assert 'rodada_alocacao' in item
            assert 'ganho' in item
            assert 'custo' in item
            assert 'ganho_por_custo' in item
            assert 'investimento_restante' in item
            assert 'indisponibilidade_restante' in item
            assert 'ganho_acumulado' in item
            assert 'custo_acumulado' in item
            assert 'created_at' in item

    @pytest.mark.alocacoes
    def test_quando_listar_alocacoes_sem_token_deve_retornar_401(self, client):
        #when
        response = client.get('/api/v1/data/alocacoes')
        #then
        assert response.status_code == 401

    @pytest.mark.alocacoes
    def test_quando_ocorrer_erro_interno_deve_retornar_500(self, client, monkeypatch):
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
            'api.routes.data.get_alocacoes',
            mock_error
        )
        #when
        response = client.get(
            '/api/v1/data/alocacoes',
            headers=headers
        )
        result = response.get_json()
        #then
        assert response.status_code == 500
        assert 'error' in result



@pytest.mark.data
class TestGetBaterias:
    @pytest.mark.baterias
    def test_quando_listar_baterias_com_token_valido_deve_retornar_200(self, client):
        #given
        user_data = {'username': 'teste', 'password': 'teste'}
        client.post('/api/v1/auth/register', json=user_data)
        login = client.post('/api/v1/auth/login', json=user_data)
        token = login.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        #when
        response = client.get('/api/v1/data/baterias', headers=headers)
        result = response.get_json()
        #then
        assert response.status_code == 200
        assert isinstance(result, list)

        if result:
            item = result[0]
            assert 'id' in item
            assert 'tecnologia' in item
            assert 'fabricante' in item
            assert 'tensao' in item
            assert 'capacidade' in item
            assert 'preco' in item
            assert 'updated_at' in item

    @pytest.mark.baterias
    def test_quando_listar_baterias_sem_token_deve_retornar_401(self, client):
        response = client.get('/api/v1/data/baterias')
        assert response.status_code == 401

    @pytest.mark.baterias
    def test_quando_ocorrer_erro_interno_ao_listar_baterias_deve_retornar_500(self, client, monkeypatch):
        user_data = {'username': 'teste', 'password': 'teste'}
        client.post('/api/v1/auth/register', json=user_data)
        login = client.post('/api/v1/auth/login', json=user_data)
        token = login.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        def mock_error():
            raise Exception('Erro forçado')

        monkeypatch.setattr('api.routes.data.get_baterias', mock_error)

        response = client.get('/api/v1/data/baterias', headers=headers)
        assert response.status_code == 500
        assert 'error' in response.get_json()