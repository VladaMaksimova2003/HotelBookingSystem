from ..extensions import db


class HotelPhoto(db.Model):
    __tablename__ = 'hotel_photo'
    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    url = db.Column(db.String(255), nullable=False)

class RoomTypePhoto(db.Model):
    __tablename__ = 'room_type_photo'

    id = db.Column(db.Integer, primary_key=True)
    room_type_id = db.Column(db.Integer, db.ForeignKey('room_type.id'), nullable=False)
    url = db.Column(db.String(255), nullable=False)