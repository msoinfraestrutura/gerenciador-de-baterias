import logging
from datetime import datetime, UTC

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, get_jwt_identity, 
    jwt_required, create_refresh_token
)
from api.extensions import db, bcrypt
from api.models import User, UserAccess, RefreshTokenManager
from api.services.auth_service import get_user_by_username, check_user
from api.config.config import Config


logger = logging.getLogger('__name__')
auth_bp = Blueprint('auth', __name__)


#@auth_bp.route('/register', methods=['POST'])
def register_user():
    '''
    Registra um novo usuário
    ---
    tags:
      - Auth
    summary: Registro de usuário e geração de tokens.
    description: |
        Endpoint responsável por registrar usuário e retornar access e refresh token.
    parameters:
        - in: body
          name: body
          required: true
          schema:
            type: object
            properties:
                username:
                    type: string
                    example: 'teste'
                password:
                    type: string
                    example: '123456'
    responses:
        201:
            description: Usuário cadastrado com sucesso.
            schema:
                type: object
                properties:
                    msg:
                        type: string
                        description: Mensagem de successo para registro de usuário.
                    user_id:
                        type: string
                        description: ID do usuário.
                    access_token:
                        type: string
                        description: Access token.
                    refresh_token:
                        type: string
                        description: Refresh token.

            examples:
                application/json:
                    msg: 'Usuário cadastrado com sucesso'
                    user_id: 1
                    access_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
                    refresh_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
        400:
            description: Usuário já existe.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro para registro de usuário.
            examples:
                application/json:
                    error: 'Usuário já existe'
        500:
            description: Erro interno do servidor.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro interno do servidor.
            examples:
                application/json:
                    error: '<erro interno do servidor>'
    '''
    data = request.get_json(force=True)

    if get_user_by_username(data['username']):
        return jsonify({'error': 'Usuário já existe'}), 400
    try:
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(username=data['username'], password=hashed_password)
        db.session.add(new_user)
        db.session.flush()

        access_token = create_access_token(identity=str(new_user.id))
        refresh_token = create_refresh_token(identity=str(new_user.id))

        new_refresh_token = RefreshTokenManager(
            username=data['username'],
            refresh_token=refresh_token,
            refresh_token_expire_at=datetime.now(UTC) + Config.JWT_REFRESH_TOKEN_EXPIRES
        )
        db.session.add(new_refresh_token)
        
        db.session.commit()

        return jsonify({
            'msg': 'Usuário cadastrado com sucesso',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': new_user.id
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    '''
    Realiza autenticação e cadastro de usuário, fornecendo tokens de acesso.
    ---
    tags:
      - Auth
    summary: Autenticação e geração de tokens.
    description: |
        Endpoint responsável por autenticar o usuário via base de dados infratel e cadastrar usuário na API.
    parameters:
        - in: body
          name: body
          required: true
          schema:
              type: object
              properties:
                  username:
                      type: string
                      example: '<login infratel>'
                  password:
                      type: string
                      example: '<senha infratel>'
              required:
                  - username
                  - password
    responses:
        200:
            description: Autenticação realizada com sucesso.
            schema:
                type: object
                properties:
                    access_token:
                        type: string
                        description: Access token.
                    refresh_token:
                        type: string
                        description: Refresh token.
            examples:
                application/json:
                    access_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
                    refresh_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
        401:
            description: Usuário ou senha inválidas.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro para login.
            examples:
                application/json:
                    error: 'Usuário ou senha inválidas'
        500:
            description: Erro interno do servidor.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro interno do servidor.
            examples:
                application/json:
                    error: '<erro interno do servidor>'
    '''
    data = request.get_json(force=True)
    username = data.get('username')
    password = data.get('password')

    # 1. Validação na base corporativa (MD5 / tbl_user)
    if not check_user(username, password):
        return jsonify({'error': 'Usuário ou senha inválidas'}), 401

    try:
        user = get_user_by_username(username)

        if not user:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user = User(username=username, password=hashed_password)
            db.session.add(user)
            db.session.flush()
            logger.info(f'Usuário "{username}" registrado automaticamente.')

        new_login = UserAccess(username=username, created_at=datetime.now(UTC))
        db.session.add(new_login)
            
        existing_refresh_token = (
            RefreshTokenManager.query.filter(
                    RefreshTokenManager.username == user.username,
                    RefreshTokenManager.refresh_token_expire_at > datetime.now(UTC).replace(tzinfo=None)
                ).order_by(RefreshTokenManager.created_at.desc()).first()
            )
        
        if existing_refresh_token:
            access_token = create_access_token(identity=str(user.id))
            db.session.commit()
            return jsonify({
                'access_token': access_token,
                'refresh_token': existing_refresh_token.refresh_token
            }), 200
        
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        new_refresh_token_to_db = RefreshTokenManager(
            username=username,
            refresh_token=refresh_token,
            refresh_token_expire_at=datetime.now(UTC) + Config.JWT_REFRESH_TOKEN_EXPIRES
        )
        db.session.add(new_refresh_token_to_db)
        db.session.commit()

        return jsonify({
            'access_token': access_token, 
            'refresh_token': refresh_token
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    '''
    Fornece token de acesso atualizado.
    ---
    tags:
        - Auth
    summary: Geração de token de acesso atualizado.
    security:
        - Bearer: []
    description: |
        Endpoint responsável por gerar um novo *access token* a partir de um *refresh token* válido.
    responses:
        200:
            description: Novo access token gerado com sucesso.
            schema:
                type: object
                properties:
                    msg:
                        type: string
                        description: Mensagem de sucesso para atualização do token.
            examples:
                application/json:
                    'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
        401:
            description: Erro de autenticação JWT.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro de autenticação.
            examples:
                application/json:
                    error: '<erro de autenticação>'
        500:
            description: Erro interno do servidor.
            schema:
                type: object
                properties:
                    error:
                        type: string
                        description: Mensagem de erro interno do servidor.
            examples:
                application/json:
                    error: '<erro interno do servidor>'
    '''
    try:
        identity = get_jwt_identity()
        user_access = RefreshTokenManager.query.filter_by(
            refresh_token=request.headers.get('Authorization').replace('Bearer ', '')
        ).first()

        if not user_access:
            return jsonify({'error': 'Refresh token inválido ou não existe, fazer o Login novamente'}), 401
        if datetime.now(UTC).replace(tzinfo=None) > user_access.refresh_token_expire_at:
            return jsonify({'error': 'Refresh token expirado, fazer login novamente'}), 401
        
        new_acess_token = create_access_token(identity=identity)

        return jsonify({'access_token': new_acess_token}), 200
    
    except Exception as e:
        logger.error(f'error: {e}')
        return jsonify({'error': str(e)}), 500