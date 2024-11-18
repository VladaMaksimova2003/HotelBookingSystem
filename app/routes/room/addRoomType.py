import os
import json
import uuid
from flask_login import login_required
from werkzeug.utils import secure_filename
from flask import render_template, redirect, flash, url_for, jsonify, current_app, request

from ...extensions import db
from ...forms import RoomTypeForm
from ...models.room import *
from ...models.photo import RoomTypePhoto
from app.routes.data_aggregators import *
from . import room_bp


@room_bp.route('/add/<int:hotel_id>', methods=['GET', 'POST'])
@login_required
def add_room_type(hotel_id):

    """Обработчик маршрута, который отвечает за добавление нового типа комнаты в отель."""

    form = RoomTypeForm()
    features_data = get_features_data_room()

    if form.validate_on_submit():
        try:
            new_room = create_room_type(form, hotel_id)

            save_photos(request.files.getlist('photos'), new_room.id)

            features_json = form.features_json.data
            add_features_to_room(new_room.id, features_json)

            flash('Комната успешно добавлена!', 'success')
            return redirect(url_for('room.list_rooms', hotel_id=hotel_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Произошла ошибка: {str(e)}', 'danger')
    return render_template('adding/room.html', form=form, hotel_id=hotel_id, features_data=features_data)

@room_bp.route('/get_features/<int:feature_type_id>', methods=['GET'])
def get_features(feature_type_id):

    """Обработчик маршрута, который получает все удобства для конкретного типа удобств и возвращает их в формате JSON."""

    features = RoomFeature.query.filter_by(type_id=feature_type_id).all()
    return jsonify({'features': [{'id': feature.id, 'name': feature.name} for feature in features]})

def get_or_create_feature_type(feature_type_name):

    """Функция проверяет, существует ли тип удобства с данным названием в базе данных."""

    feature_type = RoomFeatureType.query.filter_by(name=feature_type_name).first()
    if not feature_type:
        feature_type = RoomFeatureType(name=feature_type_name)
        db.session.add(feature_type)
        db.session.commit()
    return feature_type


def get_or_create_feature(feature_name, feature_type_id):

    """ Функция проверяет, существует ли удобство с данным названием и ID типа удобства"""

    feature = RoomFeature.query.filter_by(name=feature_name, type_id=feature_type_id).first()
    if not feature:
        feature = RoomFeature(name=feature_name, type_id=feature_type_id)
        db.session.add(feature)
        db.session.commit()
    return feature


def add_features_to_room(room_type_id, features_json):

    """Функция добавляет удобства к типу комнаты на основе переданного JSON с удобствами."""

    features_by_type = json.loads(features_json) if features_json else []

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
                    room_feature = RoomFeatureAssociation(room_type_id=room_type_id, feature_id=feature.id)
                    db.session.add(room_feature)
    db.session.commit()


def create_room_type(form, hotel_id):

    """Функция создает новый тип комнаты на основе данных из формы и связывает его с отелем."""

    new_room_type = RoomType(
        hotel_id=hotel_id, 
        name=form.name.data,
        description=form.description.data,  
        price=form.price.data, 
        currency=form.currency.data 
    )
    db.session.add(new_room_type)
    db.session.commit()
    return new_room_type


def save_photos(photos, room_type_id):

    """Функция сохраняет фотографии для конкретного типа комнаты на сервере."""

    upload_folder = os.path.join(current_app.root_path, f'static/uploads/rooms/{room_type_id}')
    os.makedirs(upload_folder, exist_ok=True)

    for photo in photos:
        if photo and photo.filename != '':
            unique_filename = f"{uuid.uuid4().hex}_{secure_filename(photo.filename)}"
            photo.save(os.path.join(upload_folder, unique_filename))

            room_photo = RoomTypePhoto(room_type_id=room_type_id, url=unique_filename)
            db.session.add(room_photo)
    db.session.commit()


