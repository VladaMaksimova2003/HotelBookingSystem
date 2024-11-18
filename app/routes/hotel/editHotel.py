import os
import uuid
import json

from flask import render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError

from ...extensions import db
from ...models.hotel import *
from ...models.photo import HotelPhoto
from app.routes.data_aggregators import *
from ...forms import HotelForm

from . import hotel_bp


@hotel_bp.route('/edit/<int:hotel_id>', methods=['GET', 'POST'])
@login_required
def edit_hotel(hotel_id):
    """Отображает форму редактирования отеля и обрабатывает отправленные данные."""
    hotel = Hotel.query.get_or_404(hotel_id)
    countries = Country.query.all()
    form = HotelForm()
    setup_edit_hotel_form(hotel, form)
    if request.method == 'POST' and form.validate_on_submit():
        if update_hotel_data(hotel, form):
            flash('Отель успешно обновлён!', 'success')
            return redirect(url_for('hotel.list_hotels'))
        else:
            flash('Произошла ошибка при обновлении отеля.', 'danger')

    return render_template(
        'editing/hotel.html',
        hotel=hotel,
        features_data_current_hotel=get_features_data_current_hotel(hotel_id),
        features_data=get_features_data(),
        form=form,
        is_edit=True,
        hotel_photos=get_hotel_photos(hotel_id),
        countries=countries
    )


def setup_edit_hotel_form(hotel, form):
    """Подготавливает данные для формы редактирования."""
    location, current_city, current_country = get_current_location_info(hotel)
    form.new_country.data = current_country.name if current_country else ''
    form.new_city.data = current_city.name if current_city else ''
    form.location.data = location.location if location else ''
    print(form.location.data)
    

def update_hotel_data(hotel, form):
    print("hello")
    """Обрабатывает данные формы и обновляет отель, возвращая успех операции."""
    try:
        country, city = get_or_create_country_city(form, hotel)
        current_location = Location.query.get(hotel.location_id)
        location = update_or_get_location(form.location.data.strip(), city.id, country.id, current_location)
        print(location)
        update_hotel_info(hotel, form, location.id)
        handle_edit_hotel_photos(hotel.id, request.files.getlist('photos'))
        update_hotel_features(hotel.id, form.features_json.data)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f'Ошибка: {str(e)}')
        return False


def get_or_create_country_city(form, hotel):
    """Получает или создаёт страну и город на основе данных формы."""
    current_country, current_city = get_country_city_by_location_id(hotel)
    country = get_or_create_country(form.new_country.data.strip(), current_country)
    city = get_or_create_city(form.new_city.data.strip(), current_city)
    return country, city


def update_hotel_features(hotel_id, features_json):
    """Обновляет удобства отеля, добавляет новые и удаляет отсутствующие."""
    features_by_type = json.loads(features_json) if features_json else []

    existing_features = HotelFeatureAssociation.query.filter_by(hotel_id=hotel_id).all()
    existing_features_map = {
        (feature_association.feature_id): feature_association
        for feature_association in existing_features
    }

    for feature_info in features_by_type:
        feature_type_name = feature_info.get('type', '').strip()
        feature_values = feature_info.get('features', [])

        if not feature_type_name:
            raise ValueError("Feature type name cannot be empty")

        # Получаем или создаем тип удобства
        feature_type = get_or_create_feature_type(feature_type_name)

        # Пройдем по значениям удобств для этого типа
        for feature_name in feature_values:
            feature_name = feature_name.strip()
            if feature_name:
                # Получаем или создаем удобство
                feature = get_or_create_feature(feature_name, feature_type.id)

                # Если удобства нет в текущих связях, добавляем его
                feature_key = feature.id
                if feature_key not in existing_features_map:
                    hotel_feature = HotelFeatureAssociation(hotel_id=hotel_id, feature_id=feature.id)
                    db.session.add(hotel_feature)

                # Удаляем из карты существующих удобств, чтобы отметить как обработанное
                existing_features_map.pop(feature_key, None)

    # Удаление неудобств, отсутствующих в новом `features_json`
    for unused_feature in existing_features_map.values():
        db.session.delete(unused_feature)

    db.session.commit()

def get_or_create_feature_type(feature_type_name):
    """Получает или создает тип удобства."""
    feature_type = HotelFeatureType.query.filter_by(name=feature_type_name).first()
    if not feature_type:
        feature_type = HotelFeatureType(name=feature_type_name)
        db.session.add(feature_type)
        db.session.commit()
    return feature_type

def get_or_create_feature(feature_name, feature_type_id):
    """Получает или создает удобство для указанного типа."""
    feature = HotelFeature.query.filter_by(name=feature_name, type_id=feature_type_id).first()
    if not feature:
        feature = HotelFeature(name=feature_name, type_id=feature_type_id)
        db.session.add(feature)
        db.session.commit()
    return feature



def save_photos(photos, hotel_id):
    upload_folder = os.path.join(current_app.root_path, f'static/uploads/hotels/{hotel_id}')
    os.makedirs(upload_folder, exist_ok=True)

    for photo in photos:
        if photo and photo.filename != '':
            unique_filename = f"{uuid.uuid4().hex}_{secure_filename(photo.filename)}"
            photo.save(os.path.join(upload_folder, unique_filename))

            # Сохраняем только имя файла в поле url
            hotel_photo = HotelPhoto(hotel_id=hotel_id, url=unique_filename)
            db.session.add(hotel_photo)
            db.session.commit()

def delete_unused_location_data(location, city, country):
    """Удаляет локацию, город и страну, если они не связаны с другими отелями."""
    print("hello\n")
    try:
        # Переменные для отслеживания объектов для удаления
        location_deleted = False
        city_deleted = False
        country_deleted = False
        
        # Проверяем, используется ли локация другими отелями
        if location and not Hotel.query.filter_by(location_id=location.id).count():
            print("Deleting location")
            db.session.delete(location)
            location_deleted = True
        
        # Проверяем, используется ли город другими локациями
        if city and not Location.query.filter_by(city_id=city.id).count():
            print("Deleting city")
            db.session.delete(city)
            city_deleted = True
        
        # Проверяем, используется ли страна другими локациями
        if country and not Location.query.filter_by(country_id=country.id).count():
            print("Deleting country")
            db.session.delete(country)
            country_deleted = True
        
        # Если были выполнены удаления, то коммитим все вместе
        if location_deleted or city_deleted or country_deleted:
            db.session.commit()
        print("bay\n")
    except IntegrityError:
        db.session.rollback()
        flash('Ошибка при удалении старых данных о локации', 'danger')





def get_current_location_info(hotel):
    """Получает текущую страну, город и локацию для отеля."""
    location = Location.query.get(hotel.location_id) if hotel.location_id else None
    current_city = City.query.get(location.city_id) if location else None
    current_country = Country.query.get(location.country_id) if location else None
    return location, current_city, current_country

def get_country_city_by_location_id(hotel):
    """Получает страну и город на основе location_id из объекта hotel."""
    location = Location.query.get(hotel.location_id)
    if location:
        country = Country.query.get(location.country_id)
        city = City.query.get(location.city_id)
        return country, city
    return None, None

def get_or_create_country(country_name, current_country):
    """Проверяет или создает запись страны, если она отличается от текущей."""
    if current_country and current_country.name == country_name:
        return current_country
    country = Country.query.filter_by(name=country_name).first()
    if not country:
        country = Country(name=country_name)
        db.session.add(country)
        db.session.commit()
    return country

def get_or_create_city(city_name, current_city):
    """Проверяет или создает запись города, если она отличается от текущего."""
    if current_city and current_city.name == city_name:
        return current_city
    city = City.query.filter_by(name=city_name).first()
    if not city:
        city = City(name=city_name)
        db.session.add(city)
        db.session.commit()
    return city

def update_or_get_location(location_name, city_id, country_id, current_location):
    """Обновляет текущую запись локации с указанными параметрами или возвращает существующую."""
    if current_location:
        # Если текущая локация уже соответствует данным, просто возвращаем её
        if (current_location.location == location_name and 
            current_location.city_id == city_id and 
            current_location.country_id == country_id):
            return current_location

        # Обновляем поля текущей локации
        current_location.location = location_name
        current_location.city_id = city_id
        current_location.country_id = country_id
        db.session.commit()

        return current_location
    else:
        # Если текущей локации нет, создаем новую запись
        location = Location(location=location_name, city_id=city_id, country_id=country_id)
        db.session.add(location)
        db.session.commit()
        
        return location


def update_hotel_info(hotel, form, location_id):
    """Обновляет основную информацию об отеле и присваивает новую локацию."""
    hotel.name = form.name.data.strip()
    hotel.description = form.description.data.strip()
    hotel.phone_number = form.phone_number.data.strip()
    hotel.location_id = location_id
    db.session.commit()

def handle_edit_hotel_photos(hotel_id, photos):
    """Сохраняет фотографии для отеля."""
    save_photos(photos, hotel_id)


def get_hotel_photos(hotel_id):
    return HotelPhoto.query.filter_by(hotel_id=hotel_id).all()

def get_features_data_current_hotel(hotel_id):
    # Получаем все типы удобств
    feature_types = HotelFeatureType.query.all()
    
    # Получаем все удобства
    features = HotelFeature.query.all()
    
    # Получаем ассоциации удобств для конкретного отеля
    associated_features = HotelFeatureAssociation.query.filter_by(hotel_id=hotel_id).all()

    # Создаем словарь для хранения удобств по типам
    features_data = {feature_type.name: [] for feature_type in feature_types}

    # Добавляем удобства в соответствующие типы
    for association in associated_features:
        feature = HotelFeature.query.get(association.feature_id)
        feature_type = HotelFeatureType.query.get(feature.type_id)
        if feature and feature_type:
            features_data[feature_type.name].append(feature.name)

    # Удаляем типы, в которых нет удобств
    features_data = {key: value for key, value in features_data.items() if value}

    return features_data

def delete_unused_feature_data(hotel):
    """Удаляет фичи и их типы, если они не связаны с другими отелями."""
    try:
        # Получаем все ассоциации фич для данного отеля
        feature_associations = HotelFeatureAssociation.query.filter_by(hotel_id=hotel.id).all()
        print(feature_associations)
        # Списки для хранения фич и типов фич, подлежащих удалению
        features_to_delete = set()
        feature_types_to_delete = set()

        for association in feature_associations:
            # Добавляем фичу и тип фичи в списки для удаления, если они не используются другими отелями
            feature = HotelFeature.query.get(association.feature_id)
            if feature:
                # Проверяем, что фича используется только для текущего отеля
                if not HotelFeatureAssociation.query.filter_by(feature_id=feature.id).count() > 1:
                    features_to_delete.add(feature)

                # Проверяем тип фичи
                feature_type = HotelFeatureType.query.get(feature.type_id) if feature else None
                if feature_type and not HotelFeature.query.filter_by(type_id=feature_type.id).count() > 1:
                    feature_types_to_delete.add(feature_type)

            # Удаляем ассоциацию с отелем
            db.session.delete(association)
        # Удаляем ассоциации фич с отелем
        HotelFeatureAssociation.query.filter_by(hotel_id=hotel.id).delete()
        # Удаляем фичи и типы фичи, которые не используются другими отелями
        for feature in features_to_delete:
            print(f"Deleting feature: {feature}")
            db.session.delete(feature)

        for feature_type in feature_types_to_delete:
            print(f"Deleting feature type: {feature_type}")
            db.session.delete(feature_type)

        # Единый коммит после всех удалений
        db.session.commit()
        flash('Unused features and feature types deleted successfully.', 'success')

    except IntegrityError:
        db.session.rollback()
        flash('Error occurred while deleting unused feature data.', 'danger')


@hotel_bp.route('/delete/<int:hotel_id>', methods=['GET', 'POST'])
@login_required
def delete_hotel(hotel_id):
    try:
        # Получаем отель по ID
        hotel = Hotel.query.get_or_404(hotel_id)
        location, current_city, current_country = get_current_location_info(hotel)

        # Удаляем данные, связанные с фичами отеля
        delete_unused_feature_data(hotel)

        # Удаляем ассоциации фич
        HotelFeatureAssociation.query.filter_by(hotel_id=hotel_id).delete()

        # Удаляем фото
        photos = HotelPhoto.query.filter_by(hotel_id=hotel_id).all()
        for photo in photos:
            # Удаляем фото с сервера
            photo_path = os.path.join(current_app.root_path, 'static/uploads/hotels', str(hotel_id), photo.url)
            if os.path.exists(photo_path):
                os.remove(photo_path)
        
        # Удаляем фото из базы данных
        HotelPhoto.query.filter_by(hotel_id=hotel_id).delete()

        # Теперь можно удалить сам отель
        db.session.delete(hotel)

        # Выполняем коммит
        db.session.commit()

        # Удаляем неиспользуемые локации, города и страны
        delete_unused_location_data(location, current_city, current_country)

        flash('Hotel and associated data deleted successfully!', 'success')
        return redirect(url_for('hotel.list_hotels'))

    except IntegrityError:
        db.session.rollback()
        flash('Error occurred while deleting the hotel and associated data.', 'danger')


    except FileNotFoundError as e:
        flash(f"File error occurred: {str(e)}", 'danger')
        return redirect(url_for('hotel.list_hotels'))

    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while deleting the hotel: {str(e)}", 'danger')
        return redirect(url_for('hotel.list_hotels'))



@hotel_bp.route('/delete/photo', methods=['GET','POST'])
@login_required
def delete_photo():
    print("hello")
    try:
        # Проверка типа данных запроса
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        data = request.get_json()
        hotel_id = data.get('id')
        photo_url = data.get('photo_url')
        print(data, hotel_id, photo_url)

        if not hotel_id or not photo_url:
            return jsonify({"error": "Missing hotel_id or photo_url"}), 400

        # Поиск фото в базе данных
        photo = HotelPhoto.query.filter_by(hotel_id=hotel_id, url=photo_url).first()
        print(photo)

        if photo:
            try:
                db.session.delete(photo)
                db.session.commit()

                photo_path = os.path.join(current_app.root_path, 'static', 'uploads', 'hotels', str(hotel_id), photo_url)
                print(photo_path)

                try:
                    if os.path.exists(photo_path):
                        os.remove(photo_path)
                    else:
                        db.session.rollback()
                        return jsonify({"error": f"File not found at {photo_path}"}), 404
                    print("1")
                except OSError as e:
                    db.session.rollback()
                    print("2")
                    return jsonify({"error": f"Error deleting file: {str(e)}"}), 500

                return jsonify({"message": "Photo deleted successfully"}), 200

            except Exception as e:
                db.session.rollback()
                print("3")
                return jsonify({"error": str(e)}), 500
        else:
            print("4")
            return jsonify({"error": "Photo not found"}), 404

    except Exception as e:
        print("5")
        return jsonify({"error": str(e)}), 500
