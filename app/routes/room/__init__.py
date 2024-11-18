from flask import Blueprint

# Создаем один общий Blueprint для отеля
room_bp = Blueprint('room', __name__)

# Импортируем маршруты из других модулей
from .addRoomType import *
from .listRoomType import *
from .editRoomType import *
