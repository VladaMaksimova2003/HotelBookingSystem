import json

from flask import render_template, request, flash, jsonify

from ...extensions import db
from ...models.photo import HotelPhoto
from ...forms import FeaturesFilterForm
from app.routes.data_aggregators import *

from . import hotel_bp


@hotel_bp.route('/', methods=['GET', 'POST'])
def list_hotels():
    """
    Обрабатывает запросы для отображения списка отелей с фильтрами.
    Загружает все отели, фотографии, удобства и применяет фильтры.
    """
    try:
        hotels = get_all_hotels()
        hotel_photos_dict = get_hotel_photos()
        hotel_features_dict = get_hotel_features()
        features_data = get_features_data()

        query = apply_filters(request.args)

        features_json = request.args.get('features_json')
        print("Полученный JSON от фильтров:", features_json)
        if features_json:
            query = filter_by_features(query, features_json)

        hotels = query.all()

        countries = Country.query.all()
        cities = City.query.all()
        filter_form = FeaturesFilterForm()

        return render_template(
            'reservations/hotel_list.html',
            hotels=hotels,
            countries=countries,
            cities=cities,
            hotel_photos_dict=hotel_photos_dict,
            hotel_features_dict=hotel_features_dict,
            features_data=features_data,
            filter_form=filter_form
        )
    
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        flash("Произошла ошибка при загрузке данных. Попробуйте позже.", "error")
        return render_template(
            'reservations/hotel_list.html',
            hotels=[],
            countries=[],
            cities=[],
            hotel_photos_dict={},
            hotel_features_dict={},
            features_data={},
            filter_form=FeaturesFilterForm()
        )


def get_all_hotels():
    """
    Возвращает все отели из базы данных.
    """
    return Hotel.query.all()


def get_hotel_photos():
    """
    Получает все фотографии отелей и группирует их по hotel_id.
    """
    hotel_photos = HotelPhoto.query.all()
    hotel_photos_dict = {}
    for photo in hotel_photos:
        hotel_photos_dict.setdefault(photo.hotel_id, []).append(photo)
    return hotel_photos_dict


def apply_filters(args):
    """
    Применяет фильтры для поиска отелей по стране, городу, рейтингу и количеству отзывов.
    """
    query = Hotel.query.join(Location)
    
    country_id = args.get('country', type=int)
    if country_id:
        query = query.filter(Location.country_id == country_id)

    city_id = args.get('city', type=int)
    if city_id:
        query = query.filter(Location.city_id == city_id)

    min_rating = args.get('min_rating', type=float)
    if min_rating is not None:
        query = query.filter(Hotel.rating >= min_rating)
    
    min_reviews = args.get('min_reviews', type=int)
    if min_reviews is not None:
        query = query.filter(Hotel.review_count >= min_reviews)

    return query


def filter_by_features(query, features_json):
    """
    Фильтрует отели по выбранным удобствам, полученным в формате JSON.
    """
    try:
        features_by_type = json.loads(features_json)

        if not features_by_type or all(not fg['type'].strip() for fg in features_by_type):
            return query

        for feature_group in features_by_type:
            type_name = feature_group['type']
            feature_names = feature_group['features']

            print(feature_names)

            if feature_names and any(feature for feature in feature_names if feature.strip()):
                subquery = db.session.query(HotelFeatureAssociation.hotel_id)\
                    .join(HotelFeature, HotelFeatureAssociation.feature_id == HotelFeature.id)\
                    .join(HotelFeatureType, HotelFeature.type_id == HotelFeatureType.id)\
                    .filter(HotelFeatureType.name == type_name, HotelFeature.name.in_(feature_names))\
                    .subquery()


                query = query.filter(Hotel.id.in_(db.session.query(subquery.c.hotel_id)))
            else: 
                subquery = db.session.query(HotelFeatureAssociation.hotel_id)\
                    .join(HotelFeature, HotelFeatureAssociation.feature_id == HotelFeature.id)\
                    .join(HotelFeatureType, HotelFeature.type_id == HotelFeatureType.id)\
                    .filter(HotelFeatureType.name == type_name)\
                    .subquery()

                query = query.filter(Hotel.id.in_(db.session.query(subquery.c.hotel_id)))

    except json.JSONDecodeError:
        print("Ошибка: Неверный формат JSON данных для удобств")

    return query


