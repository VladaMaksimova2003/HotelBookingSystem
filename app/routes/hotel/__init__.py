from flask import Blueprint
from ...extensions import db
# Создаем один общий Blueprint для отеля
hotel_bp = Blueprint('hotel', __name__)

# Импортируем маршруты из других модулей
from .addHotel import *
from .listHotel import *
from .editHotel import *