from flask import Flask

# from .bundles import bundles, register_bundles
# from .extensions import db, migrate, login_manager, assets
from .extensions import db, migrate, login_manager
from .config import Config

from .routes.hotel import hotel_bp
from .routes.room import room_bp
from .routes.customer import customer



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(customer)
    app.register_blueprint(hotel_bp, url_prefix='/hotel')
    app.register_blueprint(room_bp, url_prefix='/hotel/room')



    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    # assets.init_app(app)

    # # LOGIN MANAGER
    login_manager.login_view = 'customer.login'
    login_manager.login_message = 'Вы не можете получить доступ к данной странице. Нужно сначала войти.'
    login_manager.login_message_category = 'info'

    # # ASSETS
    # register_bundles(assets, bundles)

    with app.app_context():
        db.create_all()

    return app
