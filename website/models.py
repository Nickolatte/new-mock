from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    is_admin = db.Column(db.Boolean, default=False)
    booking = db.relationship('Booking', backref='user', lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    adultticket = db.Column(db.Integer)
    childticket = db.Column(db.Integer)
    bookingdate = db.Column(db.Date, nullable=False)
    total_price = db.Column(db.Float, nullable=False)   
    paid = db.Column(db.Boolean, default=False)         
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(10), unique=True, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    max_adults = db.Column(db.Integer, nullable=False)
    max_children = db.Column(db.Integer, nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    bookings = db.relationship('HotelBooking', backref='room', lazy=True)

class HotelBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    checkin = db.Column(db.Date, nullable=False)
    checkout = db.Column(db.Date, nullable=False)
    adults = db.Column(db.Integer, nullable=False)
    children = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)   
    paid = db.Column(db.Boolean, default=False)         
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='hotel_bookings', lazy=True)


