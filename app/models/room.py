from ..extensions import db

class RoomType(db.Model):
    __tablename__ = 'room_type'

    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False)

class Room(db.Model):
    __tablename__ = 'room'

    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    room_type_id = db.Column(db.Integer, db.ForeignKey('room_type.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    number = db.Column(db.String(10), nullable=False)

class RoomFeatureType(db.Model):
    __tablename__ = 'room_feature_type'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

class RoomFeature(db.Model):
    __tablename__ = 'room_feature'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    type_id = db.Column(db.Integer, db.ForeignKey('room_feature_type.id'), nullable=False)

class RoomFeatureAssociation(db.Model):
    __tablename__ = 'room_feature_association'
    
    room_type_id = db.Column(db.Integer, db.ForeignKey('room_type.id'), primary_key=True)
    feature_id = db.Column(db.Integer, db.ForeignKey('room_feature.id'), primary_key=True)

