from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
cache = Cache()
jwt = JWTManager()
swagger = Swagger()