import os
import json
import uuid

from flask import render_template, redirect, flash, url_for, jsonify, current_app, request
from flask_login import login_required
from werkzeug.utils import secure_filename

from ...extensions import db
from ...forms import HotelForm
from ...models.hotel import *
from ...models.room import Room
from ...models.photo import HotelPhoto
from app.routes.data_aggregators import *

from . import hotel_bp

@hotel_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_hotel():
    """Обрабатывает запросы на добавление нового отеля."""
    form = HotelForm()
    features_data = get_features_data()
    countries = Country.query.all()

    if form.validate_on_submit():
        try:
            country = get_or_create_country(form.new_country.data) if form.new_country.data else None
            city = get_or_create_city(form.new_city.data) if form.new_city.data else None
            db.session.commit()

            new_location = create_location(form.location.data, city.id, country.id)
            db.session.commit()

            new_hotel = create_hotel(form, new_location.id)
            db.session.commit()

            save_photos(request.files.getlist('photos'), new_hotel.id)

            features_json = form.features_json.data
            add_features_to_hotel(new_hotel.id, features_json)
            db.session.commit()

            flash('Отель успешно добавлен!', 'success')
            return redirect(url_for('hotel.list_hotels'))

        except Exception as e:
            db.session.rollback()
            flash(f'Произошла ошибка: {str(e)}', 'danger')

    else:
        print(form.errors)

    return render_template('adding/hotel.html', form=form, features_data=features_data, countries=countries)

@hotel_bp.route('/get_cities_by_country/<int:country_id>', methods=['GET'])
def get_cities_by_country(country_id):
    """Возвращает список городов для выбранной страны."""
    
    if not Country.query.get(country_id):
        return jsonify({'error': 'Country not found'}), 404
    
    locations = Location.query.filter_by(country_id=country_id).all()
    cities = City.query.filter(City.id.in_([location.city_id for location in locations])).all()
    
    return jsonify({'cities': [{'id': city.id, 'name': city.name} for city in cities]})


@hotel_bp.route('/get_features/<int:feature_type_id>')
def get_features(feature_type_id):
    """Возвращает доступные функции для выбранного типа."""
    features = HotelFeature.query.filter_by(type_id=feature_type_id).all()
    return jsonify({'features': [{'id': feature.id, 'name': feature.name} for feature in features]})


@hotel_bp.route('/hotel/<int:hotel_id>/rooms', methods=['GET'])
def view_rooms(hotel_id):
    """Отображает список комнат отеля."""
    hotel = Hotel.query.get_or_404(hotel_id)
    rooms = Room.query.filter_by(hotel_id=hotel_id).all()
    
    return render_template('reservations/room_list.html', hotel=hotel, rooms=rooms)


def get_or_create_country(name):
    """Получает страну по имени, если не найдено — создает новую."""
    country = Country.query.filter_by(name=name).first()
    if not country:
        country = Country(name=name)
        db.session.add(country)
    return country


def get_or_create_city(name):
    """Получает город по имени, если не найдено — создает новый."""
    city = City.query.filter_by(name=name).first()
    if not city:
        city = City(name=name)
        db.session.add(city)
    return city


def create_location(location_data, city_id, country_id):
    """Создает новую локацию на основе данных."""
    new_location = Location(location=location_data, city_id=city_id, country_id=country_id)
    db.session.add(new_location)
    return new_location


def create_hotel(form, location_id):
    """Создает новый отель на основе данных из формы."""
    new_hotel = Hotel(
        name=form.name.data,
        description=form.description.data,
        phone_number=form.phone_number.data,
        review_count=0,
        location_id=location_id
    )
    db.session.add(new_hotel)
    return new_hotel


def save_photos(photos, hotel_id):
    """Сохраняет фотографии отеля в указанную директорию."""
    upload_folder = os.path.join(current_app.root_path, f'static/uploads/hotels/{hotel_id}')
    os.makedirs(upload_folder, exist_ok=True)

    for photo in photos:
        if photo and photo.filename != '':
            unique_filename = f"{uuid.uuid4().hex}_{secure_filename(photo.filename)}"
            photo.save(os.path.join(upload_folder, unique_filename))

            hotel_photo = HotelPhoto(hotel_id=hotel_id, url=unique_filename)
            db.session.add(hotel_photo)


def add_features_to_hotel(hotel_id, features_json):
    """Добавляет удобства к отелю на основе переданных данных."""
    features_by_type = json.loads(features_json) if features_json else []

    print(features_by_type)

    for feature_info in features_by_type:
        feature_type_name = feature_info.get('type', '').strip()
        feature_values = feature_info.get('features', [])

        if not feature_type_name:
            raise ValueError("Feature type name cannot be empty")

        feature_type = get_or_create_feature_type(feature_type_name)

        for feature_name in feature_values:
            feature_name = feature_name.strip()
            if feature_name:
                feature = get_or_create_feature(feature_name, feature_type.id)

                if feature.id is not None:
                    hotel_feature =  HotelFeatureAssociation(hotel_id=hotel_id, feature_id=feature.id)
                    db.session.add(hotel_feature)
    db.session.commit()


def get_or_create_feature_type(feature_type_name):
    """Получает тип удобства, если не найден — создает новый."""
    feature_type = HotelFeatureType.query.filter_by(name=feature_type_name).first()
    if not feature_type:
        feature_type = HotelFeatureType(name=feature_type_name)
        db.session.add(feature_type)
        db.session.commit()
    return feature_type


def get_or_create_feature(feature_name, feature_type_id):
    """Получает удобство, если не найдено — создает новое."""
    feature = HotelFeature.query.filter_by(name=feature_name, type_id=feature_type_id).first()

    if not feature:
        feature = HotelFeature(name=feature_name, type_id=feature_type_id)
        db.session.add(feature)
        db.session.commit()
    return feature