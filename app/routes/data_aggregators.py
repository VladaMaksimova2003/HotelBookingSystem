from ..models.hotel import *
from ..models.room import *

def get_hotel_features():
    hotel_features_dict = {}
    hotel_features = db.session.query(
        HotelFeatureAssociation.hotel_id,
        HotelFeature.name.label('feature_name'),
        HotelFeatureType.name.label('type_name')
    ).join(HotelFeature, HotelFeatureAssociation.feature_id == HotelFeature.id)\
     .join(HotelFeatureType, HotelFeature.type_id == HotelFeatureType.id).all()

    for feature in hotel_features:
        hotel_id = feature.hotel_id
        type_name = feature.type_name
        feature_name = feature.feature_name
        if hotel_id not in hotel_features_dict:
            hotel_features_dict[hotel_id] = {}
        if type_name not in hotel_features_dict[hotel_id]:
            hotel_features_dict[hotel_id][type_name] = []
        hotel_features_dict[hotel_id][type_name].append(feature_name)

    return hotel_features_dict

def get_room_features():
    room_features_dict = {}
    room_features = db.session.query(
        RoomFeatureAssociation.room_type_id,
        RoomFeature.name.label('feature_name'),
        RoomFeatureType.name.label('type_name')
    ).join(RoomFeature, RoomFeatureAssociation.feature_id == RoomFeature.id)\
     .join(RoomFeatureType, RoomFeature.type_id == RoomFeatureType.id).all()

    for feature in room_features:
        room_id = feature.room_type_id
        type_name = feature.type_name
        feature_name = feature.feature_name
        if room_id not in room_features_dict:
            room_features_dict[room_id] = {}
        if type_name not in room_features_dict[room_id]:
            room_features_dict[room_id][type_name] = []
        room_features_dict[room_id][type_name].append(feature_name)

    return room_features_dict

def get_features_data():
    feature_types = db.session.query(HotelFeatureType).all()

    features_data = {}
    for feature_type in feature_types:
        features = db.session.query(HotelFeature).filter_by(type_id=feature_type.id).all()
        features_data[feature_type.name] = [feature.name for feature in features]
    
    return features_data

def get_features_data_room():
    feature_types = db.session.query(RoomFeatureType).all()

    features_data = {}
    for feature_type in feature_types:
        features = db.session.query(RoomFeature).filter_by(type_id=feature_type.id).all()
        features_data[feature_type.name] = [feature.name for feature in features]
    
    return features_data

