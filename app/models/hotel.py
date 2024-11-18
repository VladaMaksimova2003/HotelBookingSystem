from ..extensions import db

class Country(db.Model):
    __tablename__ = 'country'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class City(db.Model):
    __tablename__ = 'city'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(150), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'), nullable=False)

class Hotel(db.Model):
    __tablename__ = 'hotel'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Float, default=0.0, nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    review_count = db.Column(db.Integer, default=0, nullable=False) 
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)

class HotelFeatureType(db.Model):
    __tablename__ = 'hotel_feature_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

class HotelFeature(db.Model):
    __tablename__ = 'hotel_feature'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    type_id = db.Column(db.Integer, db.ForeignKey('hotel_feature_type.id'), nullable=False)

class HotelFeatureAssociation(db.Model):
    __tablename__ = 'hotel_feature_association'
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), primary_key=True)
    feature_id = db.Column(db.Integer, db.ForeignKey('hotel_feature.id'), primary_key=True)