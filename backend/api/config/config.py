import os
from datetime import timedelta
from dotenv import load_dotenv


load_dotenv()

class Config(object):
    '''Configuração da API'''
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///db_gerenciador_de_baterias.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', '5d8c6b9e2f9d8a3c8e4b7a1d9c0e2b4f6d8a3c8e4b7a1d9c0e2b4f6d8a3c8e4b')
    JWT_ALGORITHM = 'HS256'
    SWAGGER = {
        'title': 'API Gerenciador de Baterias',
        'uiversion': 3,
        'description': 'API Flask desenvolvida para o gerenciador de baterias.',
        'securityDefinitions': {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': 'Digite: Bearer <access_token>'
            }
        }
    }
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=1440)
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 3600


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_SECRET_KEY = '5d8c6b9e2f9d8a3c8e4b7a1d9c0e2b4f6d8a3c8e4b7a1d9c0e2b4f6d8a3c8e4b'
    TESTING = True