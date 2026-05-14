import logging
from api.models.alocacoes import Alocacoes


logger = logging.getLogger(__name__)


def check_db_connection():
    '''
    Executa uma consulta simples para verificar a conexão e o status do banco de dados.

    Return:
        bool: True se a consulta for bem-sucedida, False caso contrário.
    '''
    try:
        Alocacoes.query.limit(1).all()
        return True
    except Exception as e:
        logger.error(f'error: {e}')
        return False