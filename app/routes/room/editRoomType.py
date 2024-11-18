import os
import json
import uuid
from flask_login import login_required
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
from flask import render_template, redirect, flash, url_for, jsonify, current_app, request

from ...extensions import db
from ...forms import RoomTypeForm
from ...models.room import *
from ...models.photo import RoomTypePhoto
from app.routes.data_aggregators import *
from . import room_bp


@room_bp.route('/edit/<int:room_type_id>', methods=['GET', 'POST'])
@login_required
def edit_room_type(room_type_id):
    """Обрабатывает запросы на редактирование типа комнаты. Извлекает и отображает текущие
      данные типа комнаты, удобства и фотографии, и позволяет их обновить."""
    room_type = RoomType.query.get_or_404(room_type_id)
    hotel_id = room_type.hotel_id
    features_data_current_room_type = get_features_data_current_room_type(room_type_id)
    features_data = get_features_data_room()
    room_type_photos = get_room_type_photos(room_type_id)

    form = RoomTypeForm(obj=room_type)

    if request.method == 'POST' and form.validate_on_submit():
        try:
            update_room_type_info(room_type, form)
            handle_edit_room_type_photos(room_type.id, request.files.getlist('photos'))
            features_json = form.features_json.data
            update_room_type_features(room_type.id, features_json)
            db.session.commit()

            flash('room_type updated successfully!', 'success')
            return redirect(url_for('room.list_rooms', hotel_id=hotel_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Произошла ошибка: {str(e)}', 'danger')

    else:
        print(form.errors)

    return render_template(
        'editing/room.html',
        room_type=room_type,
        features_data_current_room_type=features_data_current_room_type,
        features_data=features_data,
        form=form,
        is_edit=True,
        room_type_photos=room_type_photos
    )


@room_bp.route('/delete/<int:room_type_id>', methods=['GET', 'POST'])
@login_required
def delete_room_type(room_type_id):
    """Удаляет тип комнаты, включая его удобства и фотографии.
      Также очищает связанные данные и удаляет файлы с сервера."""
    room_type = RoomType.query.get_or_404(room_type_id)
    hotel_id = room_type.hotel_id
    try:
        delete_unused_feature_data(room_type)
        RoomFeatureAssociation.query.filter_by(room_type_id=room_type_id).delete()
        photos = RoomTypePhoto.query.filter_by(room_type_id=room_type_id).all()

        for photo in photos:
            photo_path = os.path.join(current_app.root_path, 'static/uploads/room_types', str(room_type_id), photo.url)
            if os.path.exists(photo_path):
                os.remove(photo_path)
        
        RoomTypePhoto.query.filter_by(room_type_id=room_type_id).delete()
        db.session.delete(room_type)
        db.session.commit()

        flash('room_type and associated data deleted successfully!', 'success')
        return redirect(url_for('room.list_rooms', hotel_id=hotel_id))

    except IntegrityError:
        db.session.rollback()
        flash('Error occurred while deleting the room_type and associated data.', 'danger')

    except FileNotFoundError as e:
        flash(f"File error occurred: {str(e)}", 'danger')
        return redirect(url_for('room.list_rooms', hotel_id=hotel_id))

    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while deleting the room_type: {str(e)}", 'danger')
        return redirect(url_for('room.list_rooms', hotel_id=hotel_id))


@room_bp.route('/delete/photo', methods=['POST'])
@login_required
def delete_photo():
    """Удаляет фотографию типа комнаты. Удаляет запись в базе данных и сам файл с сервера."""
    print("hello")
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        room_type_id = data.get('id')
        photo_url = data.get('photo_url')

        if not room_type_id or not photo_url:
            return jsonify({"error": "Missing room_type_id or photo_url"}), 400

        photo = RoomTypePhoto.query.filter_by(room_type_id=room_type_id, url=photo_url).first()
        print(photo)
        if photo:
            try:
                db.session.delete(photo)
                db.session.commit()

                photo_path = os.path.join(current_app.root_path, 'static', 'uploads', 'rooms', str(room_type_id), photo_url)
                print(photo_path)

                if os.path.exists(photo_path):
                    os.remove(photo_path)
                else:
                    db.session.rollback()
                    return jsonify({"error": f"File not found at {photo_path}"}), 404

                return jsonify({"message": "Photo deleted successfully"}), 200
            
            except Exception as e:
                db.session.rollback()
                return jsonify({"error": str(e)}), 500
        else:
            return jsonify({"error": "Photo not found"}), 404
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def update_room_type_features(room_type_id, features_json):
    """Обновляет удобства для типа комнаты. Добавляет новые удобства и удаляет неиспользуемые,
      проверяя их наличие в базе данных."""
    features_by_type = json.loads(features_json) if features_json else []
    existing_features = RoomFeatureAssociation.query.filter_by(room_type_id=room_type_id).all()
    existing_features_map = {
        (feature_association.feature_id): feature_association
        for feature_association in existing_features
    }

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

                feature_key = feature.id
                if feature_key not in existing_features_map:
                    room_type_feature = RoomFeatureAssociation(room_type_id=room_type_id, feature_id=feature.id)
                    db.session.add(room_type_feature)

                existing_features_map.pop(feature_key, None)

    for unused_feature in existing_features_map.values():
        db.session.delete(unused_feature)

    db.session.commit()


def get_or_create_feature_type(feature_type_name):
    """Получает или создает тип удобства."""
    feature_type = RoomFeatureType.query.filter_by(name=feature_type_name).first()
    if not feature_type:
        feature_type = RoomFeatureType(name=feature_type_name)
        db.session.add(feature_type)
        db.session.commit()
    return feature_type


def get_or_create_feature(feature_name, feature_type_id):
    """Получает или создает удобство для указанного типа."""
    feature = RoomFeature.query.filter_by(name=feature_name, type_id=feature_type_id).first()
    if not feature:
        feature = RoomFeature(name=feature_name, type_id=feature_type_id)
        db.session.add(feature)
        db.session.commit()
    return feature


def save_photos(photos, room_type_id):
    """Сохраняет фотографии для типа комнаты.
      Фотографии сохраняются с уникальными именами и добавляются в базу данных."""
    upload_folder = os.path.join(current_app.root_path, f'static/uploads/rooms/{room_type_id}')
    os.makedirs(upload_folder, exist_ok=True)

    for photo in photos:
        if photo and photo.filename != '':
            unique_filename = f"{uuid.uuid4().hex}_{secure_filename(photo.filename)}"
            photo.save(os.path.join(upload_folder, unique_filename))

            room_type_photo = RoomTypePhoto(room_type_id=room_type_id, url=unique_filename)
            db.session.add(room_type_photo)
            db.session.commit()


def update_room_type_info(room_type, form):
    """Обновляет основную информацию об отеле и присваивает новую локацию."""
    room_type.name = form.name.data.strip()
    room_type.description = form.description.data.strip()
    room_type.currency = form.currency.data
    room_type.price = form.price.data
    db.session.commit()


def handle_edit_room_type_photos(room_type_id, photos):
    """Сохраняет фотографии для отеля."""
    save_photos(photos, room_type_id)


def get_room_type_photos(room_type_id):
    """Извлекает фотографии для указанного типа комнаты."""
    return RoomTypePhoto.query.filter_by(room_type_id=room_type_id).all()


def get_features_data_current_room_type(room_type_id):
    """Извлекает данные об удобствах для текущего типа комнаты."""
    feature_types = RoomFeatureType.query.all()
    associated_features = RoomFeatureAssociation.query.filter_by(room_type_id=room_type_id).all()
    features_data = {feature_type.name: [] for feature_type in feature_types}

    for association in associated_features:
        feature = RoomFeature.query.get(association.feature_id)
        feature_type = RoomFeatureType.query.get(feature.type_id)
        if feature and feature_type:
            features_data[feature_type.name].append(feature.name)

    features_data = {key: value for key, value in features_data.items() if value}

    return features_data


def delete_unused_feature_data(room_type):
    """Удаляет неиспользуемые удобства и их типы,
      которые не связаны ни с одним другим элементом."""
    for association in room_type.room_feature_associations:
        feature = RoomFeature.query.get(association.feature_id)

        if not feature.room_feature_associations:
            feature_type = RoomFeatureType.query.get(feature.type_id)

            db.session.delete(feature)
            db.session.commit()

            if not feature_type.features:
                db.session.delete(feature_type)
                db.session.commit()
