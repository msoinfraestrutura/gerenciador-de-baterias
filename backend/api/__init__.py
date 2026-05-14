from api.config.logging_config import setup_logger
from api.extensions import db, bcrypt, cache, swagger, jwt, migrate
from flask import Flask, jsonify
from sqlalchemy import inspect
from api.config.config import Config
from api.routes.health_routes import health_bp
from api.routes.auth_routes import auth_bp
from api.routes.engine_routes import engine_bp
from api.routes.data_routes import data_bp
from api.routes.baterias_routes import baterias_bp


logger = setup_logger('api')


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
        
    #inicializa as extensões com o app
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    cache.init_app(app)
    jwt.init_app(app)
    swagger.init_app(app)
    
    #tratamento de erros do JWT
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        if 'Missing' in str(callback) or 'Authorization header' in str(callback):
            return jsonify({'error': 'Token não informado'}), 401
        return jsonify({'error': 'Erro de autenticação'}), 401


    @jwt.invalid_token_loader
    def invalid_token_callback(err):
        logger.error(f'Erro de token inválido: {err}')
        return jsonify({'error': 'Token inválido'}), 401


    @jwt.expired_token_loader
    def expired_token_callback(header, payload):
        return jsonify({'error': 'Token expirado'}), 401

    #registro de blueprints
    app.register_blueprint(health_bp, url_prefix='/api/v1')
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(engine_bp, url_prefix='/api/v1/engine')
    app.register_blueprint(data_bp, url_prefix='/api/v1/data')
    app.register_blueprint(baterias_bp, url_prefix='/api/v1/baterias')

    #rota raiz
    @app.route('/')
    def home():
        return jsonify({
            'status': 'online',
            'msg': 'Bem-vindo à API.' 
        })
  

    with app.app_context():
        try: 
            logger.info(f'Tabelas criadas/verificadas: {inspect(db.engine).get_table_names()}')
        except Exception as e:
            logger.error(f'error, {e}')

    return app