from api.extensions import db


from .users import User
from .user_access import UserAccess
from .refresh_token_manager import RefreshTokenManager
from .estacoes import Estacoes
from .baterias import Baterias
from .indisponibilidades import Indisponibilidades
from .disponibilidade import Disponibilidade
from .trafego_faturamento import TrafegoFaturamento
from .autonomia_restabelecimento import AutonomiaRestabelecimento
from .autonomia_inventario import AutonomiaInventario
from .pontuacoes import Pontuacoes
from .features import Features
from .alocacoes import Alocacoes