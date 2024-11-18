import json
from flask import render_template, request, flash
from ...extensions import db
from ...forms import FeaturesFilterForm
from ...models.room import *
from ...models.photo import RoomTypePhoto
from app.routes.data_aggregators import *
from . import room_bp

@room_bp.route('/<int:hotel_id>', methods=['GET', 'POST'])
def list_rooms(hotel_id):
    
    """Обрабатывает запросы для отображения списка типов номеров отеля с фильтрами."""
    try:
        room_types = get_all_rooms(hotel_id)
        room_type_photos_dict = get_room_type_photos()
        room_type_features_dict = get_room_features()
        features_data = get_features_data_room()

        query = apply_filters_for_rooms(request.args)
        
        features_json = request.args.get('features_json')
        print("Полученный JSON от фильтров:", features_json)
        if features_json:
            query = filter_rooms_by_features(query, features_json)
        
        room_types = query.all()

        filter_form = FeaturesFilterForm()

        return render_template(
            'reservations/room_list.html',
            hotel_id=hotel_id,
            room_types=room_types,
            room_type_photos_dict=room_type_photos_dict,
            room_type_features_dict=room_type_features_dict,
            features_data=features_data,
            filter_form=filter_form
        )
    
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        flash("Произошла ошибка при загрузке данных. Попробуйте позже.", "error")
        return render_template(
            'reservations/room_list.html',
            hotel_id=hotel_id,
            room_types=room_types,
            room_type_photos_dict=room_type_photos_dict,
            room_features_dict=room_type_features_dict,
            features_data=features_data,
            filter_form=filter_form
        )

def get_all_rooms(hotel_id):

    """Возвращает все типы номеров для указанного отеля"""

    return RoomType.query.filter_by(hotel_id=hotel_id).all()


def get_room_type_photos():

    """Получает все фотографии для типов номеров и группирует их по идентификатору типа номера."""
    
    room_type_photos = RoomTypePhoto.query.all()
    room_type_photos_dict = {}
    for photo in room_type_photos:
        room_type_photos_dict.setdefault(photo.room_type_id, []).append(photo)
    return room_type_photos_dict

def apply_filters_for_rooms(args):

    """Применяет фильтры для поиска типов номеров по имени и 
    минимальной цене на основе переданных параметров в запросе."""

    query = RoomType.query.join(Hotel)
    
    room_name = args.get('room_name', type=str)
    if room_name:
        query = query.filter(RoomType.name.ilike(f'%{room_name}%'))

    min_price = args.get('min_price', type=int)
    if min_price is not None:
        query = query.filter(RoomType.price >= min_price)

    return query


def filter_rooms_by_features(query, features_json):

    """Фильтрует типы номеров по удобствам, указанным в формате JSON. Применяет фильтрацию по типам и
      названиям удобств, если они присутствуют в запросе."""

    try:
        features_by_type = json.loads(features_json)

        if not features_by_type or all(not fg['type'].strip() for fg in features_by_type):
            return query

        for feature_group in features_by_type:
            type_name = feature_group['type']
            feature_names = feature_group['features']

            print(feature_names)

            if feature_names and any(feature for feature in feature_names if feature.strip()):
                subquery = db.session.query(RoomFeatureAssociation.room_type_id)\
                    .join(RoomFeature, RoomFeatureAssociation.feature_id == RoomFeature.id)\
                    .join(RoomFeatureType, RoomFeature.type_id == RoomFeatureType.id)\
                    .filter(RoomFeatureType.name == type_name, RoomFeature.name.in_(feature_names))\
                    .subquery()

                query = query.filter(RoomType.id.in_(db.session.query(subquery.c.room_type_id)))
            else:
                subquery = db.session.query(RoomFeatureAssociation.room_type_id)\
                    .join(RoomFeature, RoomFeatureAssociation.feature_id == RoomFeature.id)\
                    .join(RoomFeatureType, RoomFeature.type_id == RoomFeatureType.id)\
                    .filter(RoomFeatureType.name == type_name)\
                    .subquery()

                query = query.filter(Room.id.in_(db.session.query(subquery.c.room_type_id)))

    except json.JSONDecodeError:
        print("Ошибка: Неверный формат JSON данных для удобств")

    return query


