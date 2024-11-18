# from flask import Blueprint, render_template, redirect, flash, url_for, jsonify, request
# from ..extensions import db
# from ..models.room import *
# from ..forms import RoomForm

# room = Blueprint('room', __name__)


# @room.route('/add/room/<int:hotel_id>', methods=['GET', 'POST'])
# def add_room(hotel_id):
#     form = RoomForm()
#     form.feature_type_choices = load_feature_types()

#     if form.validate_on_submit():
#         try:
#             new_room = create_new_room(form, hotel_id)

#             feature_type = get_or_create_feature_type(form.feature_type_input.data)
        
#             add_features_to_room(new_room.id, feature_type.id, request.form.getlist('features[]'))

#             db.session.commit()
#             flash('Комната добавлена успешно!', 'success')
#             return redirect(url_for('room.add_room', hotel_id=hotel_id))
        
#         except Exception as e:
#             # Откатываем транзакцию в случае ошибки
#             db.session.rollback()
#             print(str(e))
#             flash("При добавлении комнаты и удобств произошла ошибка.", 'danger')

#     return render_template('adding/room.html', form=form, hotel_id=hotel_id)


# def load_feature_types():
#     feature_types = RoomFeatureType.query.all()
#     return [(ft.id, ft.name) for ft in feature_types]


# def create_new_room(form, hotel_id):
#     new_room = Room(
#         hotel_id=hotel_id,
#         status=form.status.data,
#         number=form.number.data,
#         floor_number=form.floor_number.data,
#         price=form.price.data,
#         currency=form.currency.data,
#         room_class=form.room_class.data
#     )
#     db.session.add(new_room)
#     return new_room


# def get_or_create_feature_type(feature_type_name):
#     feature_type_name = feature_type_name.strip()
#     if feature_type_name:
#         feature_type = RoomFeatureType.query.filter_by(name=feature_type_name).first()
#         if not feature_type:
#             feature_type = RoomFeatureType(name=feature_type_name)
#             db.session.add(feature_type)
#     return feature_type


# def add_features_to_room(room_id, feature_type_id, feature_names):
#     for feature_name in feature_names:
#         feature_name = feature_name.strip()
#         if feature_name:
#             feature = RoomFeature.query.filter_by(name=feature_name, type_id=feature_type_id).first()
            
#             if not feature:
#                 feature = RoomFeature(name=feature_name, type_id=feature_type_id)
#                 db.session.add(feature)

#             if feature.id is not None:
#                 room_feature = RoomFeature(room_id=room_id, feature_id=feature.id)
#                 db.session.add(room_feature)


# @room.route('/get_features/<int:type_id>')
# def get_features(type_id):
#     features = RoomFeature.query.filter_by(type_id=type_id).all()
#     return jsonify([{'id': feature.id, 'name': feature.name} for feature in features])


# @room.route('/rooms', methods=['GET'])
# def list_rooms():
#     status = request.args.get('status')
#     floor_number = request.args.get('floor_number')
#     min_price = request.args.get('min_price', type=float)
#     max_price = request.args.get('max_price', type=float)
#     room_class = request.args.get('room_class')

#     query = Room.query

#     # Применяем фильтры
#     if status:
#         query = query.filter(Room.status == status)
#     if floor_number:
#         query = query.filter(Room.floor_number == floor_number)
#     if min_price is not None:
#         query = query.filter(Room.price >= min_price)
#     if max_price is not None:
#         query = query.filter(Room.price <= max_price)
#     if room_class:
#         query = query.filter(Room.room_class == room_class)

#     rooms = query.all()
    
#     # Получаем все удобства для каждой комнаты
#     room_features_dict = {}
#     for room in rooms:
#         # Извлекаем удобства по id комнаты
#         room_features = RoomFeature.query.filter_by(room_id=room.id).all()
#         room_features_dict[room.id] = room_features

#     # Извлекаем все уникальные feature_ids из room_features
#     feature_ids = [rf.feature_id for rf_list in room_features_dict.values() for rf in rf_list]
#     features = {f.id: f for f in RoomFeature.query.filter(RoomFeature.id.in_(feature_ids)).all()}
    
#     # Извлекаем все FeatureTypes
#     feature_types = {ft.id: ft for ft in RoomFeatureType.query.all()}

#     return render_template('reservations/room_list.html', rooms=rooms, room_features_dict=room_features_dict, features=features, feature_types=feature_types)
