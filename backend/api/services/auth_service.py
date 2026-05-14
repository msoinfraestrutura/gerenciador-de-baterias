import logging
import pymysql
import hashlib
from sshtunnel import SSHTunnelForwarder
from api.models.users import User
from flask import current_app
from . import (
    SSH_HOST,
    SSH_USER,
    SSH_PASSWORD,
    MYSQL_DB_HOST,
    MYSQL_DB_PORT,
    MYSQL_DB_NAME_2,
    MYSQL_DB_USER,
    MYSQL_DB_PASSWORD,
    MYSQL_LOCAL_PORT_TUNNEL
)

logger = logging.getLogger(__name__)


def get_user_by_username(username):
    '''
    Busca e retorna um objeto de usuário (User) baseado no nome de usuário (username).

    Args:
        username (str): O nome de usuário a ser buscado no banco de dados.

    Returns:
        User: O objeto User correspondente ao username, ou None se nenhum usuário for encontrado.
    '''
    user = User.query.filter_by(username=username).first()
    
    return user


def check_user(username, password):
    '''
    Valida credenciais no banco corporativo via Túnel SSH.
    '''
    cursor = None
    conn = None
    server = None
    
    try:
        
        if current_app.config.get("TESTING"):
            return True

        server = SSHTunnelForwarder(
            (SSH_HOST, 3128),
            ssh_username=SSH_USER,
            ssh_password=SSH_PASSWORD,
            remote_bind_address=(MYSQL_DB_HOST, MYSQL_DB_PORT),
            local_bind_address=('127.0.0.1', MYSQL_LOCAL_PORT_TUNNEL)
        )
        
        server.start()
        logger.info('Túnel SSH estabelecido para validação de login')

        conn = pymysql.connect(
            host='127.0.0.1',
            port=MYSQL_LOCAL_PORT_TUNNEL,
            database=MYSQL_DB_NAME_2,
            user=MYSQL_DB_USER,
            password=MYSQL_DB_PASSWORD
        )
        
        cursor = conn.cursor()
        
        hashed_password = hashlib.md5(password.encode('utf-8')).hexdigest()
        
        query = '''
            SELECT 1 FROM tbl_user
            WHERE Login = %s AND Senha = %s AND ID_Empresa = %s
        '''
        
        cursor.execute(query, (username, hashed_password, 302))
        result = cursor.fetchone()
        
        return result is not None

    except Exception as e:
        logger.error(f'Erro na conexão SSH/MySQL para login: {e}')
        return False
        
    finally:
        if cursor: 
            cursor.close()
        if conn: 
            conn.close()
        if server: 
            server.stop()
            logger.info('Túnel SSH encerrado')