from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   
from flask_login import login_user, login_required, logout_user, current_user


views = Blueprint('views', __name__)


@views.route('/')
def home():
    first_name = current_user.first_name if current_user.is_authenticated else None
    last_name = current_user.last_name if current_user.is_authenticated else None
    return render_template('home.html', user=current_user, first_name=first_name, last_name=last_name)

@views.route('/aboutus')
def aboutus():
    return render_template('about.html',  user=current_user)

@views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@views.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.login'))



@views.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 4 characters.', category='error')
        elif len(firstName) < 2:
            flash('First name must be greater than 2 characters.', category='error')
        elif len(lastName) < 1:
            flash('Last name must be greater than 1 character.', category='error')    
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
           
            is_admin = False
            if User.query.count() == 0:
                is_admin = True

            new_user = User(
                email=email,
                first_name=firstName,
                last_name=lastName,
                password=generate_password_hash(password1, method='pbkdf2:sha256'),
                is_admin=is_admin
            )
            db.session.add(new_user)
            db.session.commit()

            if is_admin:
                flash('First account created as admin! Please log in.', category='success')
            else:
                flash('Account created! Please log in.', category='success')

            return redirect(url_for('views.login'))

    return render_template('signup.html', user=current_user)


#from flask import session, redirect, url_for

@views.route('/booking', methods=['GET', 'POST'])
@login_required
def booking():
    if request.method == 'POST':
        import datetime
        booking_date_str = request.form.get('date')
        adults = request.form.get('adults', type=int)
        children = request.form.get('children', type=int)

        if not booking_date_str:
            flash('Please select a booking date.', 'error')
            return redirect(url_for('views.booking'))

        total_price = adults*17.50 + children*14.50


        session['booking'] = {
            'type': 'ticket',
            'bookingdate': booking_date_str,
            'adults': adults,
            'children': children,
            'total_price': total_price
        }

        return redirect(url_for('views.payment'))

    return render_template('booking.html', user=current_user)

@views.route('/hotelbooking', methods=['GET', 'POST'])
@login_required
def hotelbooking():
    from datetime import datetime
    from .models import Room, HotelBooking

    if request.method == 'POST':
        checkin_str = request.form.get('checkin')
        checkout_str = request.form.get('checkout')
        adults = request.form.get('adulthotelticket', type=int)
        children = request.form.get('childrenthotelticket', type=int)

        checkin = datetime.strptime(checkin_str, '%Y-%m-%d').date()
        checkout = datetime.strptime(checkout_str, '%Y-%m-%d').date()

        if checkout <= checkin:
            flash("Checkout must be after checkin.", "error")
            return redirect(url_for('views.hotelbooking'))

        suitable_rooms = Room.query.filter(
            Room.max_adults >= adults,
            Room.max_children >= children
        ).all()

        available_rooms = []
        for room in suitable_rooms:
            overlapping = HotelBooking.query.filter(
                HotelBooking.room_id == room.id,
                HotelBooking.checkout > checkin,
                HotelBooking.checkin < checkout
            ).first()
            if not overlapping:
                available_rooms.append(room)

        return render_template(
            'available_rooms.html',
            rooms=available_rooms,
            checkin=checkin,
            checkout=checkout,
            adults=adults,
            children=children
        )

    return render_template('hotelbooking.html', user=current_user)





@views.route('/confirm-booking/<int:room_id>', methods=['POST'])
@login_required
def confirm_booking(room_id):
    from datetime import datetime
    from .models import Room

    checkin = datetime.strptime(request.form.get('checkin'), '%Y-%m-%d').date()
    checkout = datetime.strptime(request.form.get('checkout'), '%Y-%m-%d').date()
    adults = int(request.form.get('adults'))
    children = int(request.form.get('children'))

    room = Room.query.get_or_404(room_id)

    total_price = ((checkout - checkin).days) * room.price_per_night


    session['booking'] = {
        'type': 'hotel',
        'room_id': room.id,
        'checkin': checkin.strftime('%Y-%m-%d'),
        'checkout': checkout.strftime('%Y-%m-%d'),
        'adults': adults,
        'children': children,
        
    }

    return redirect(url_for('views.payment'))


from flask import session, flash, redirect, url_for

@views.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    from .models import Booking, HotelBooking, Room
    import datetime

    booking = session.get('booking')
    if not booking:
        flash("No booking found.", "error")
        return redirect(url_for('views.booking'))

    room = None
    if booking['type'] == 'hotel':
        room = Room.query.get(booking['room_id'])
   
        checkin = datetime.datetime.strptime(booking['checkin'], '%Y-%m-%d').date()
        checkout = datetime.datetime.strptime(booking['checkout'], '%Y-%m-%d').date()
        total_price = (checkout - checkin).days * room.price_per_night
        booking['total_price'] = total_price

    if request.method == 'POST':
        card_number = request.form.get('card_number', '').replace(' ', '')
        expiry = request.form.get('expiry')
        cvc = request.form.get('cvc')

        if len(card_number) != 16 or len(cvc) != 3:
            flash("Invalid card details.", "error")
            return redirect(url_for('views.payment'))


        if booking['type'] == 'ticket':
            new_booking = Booking(
                bookingdate=datetime.datetime.strptime(booking['bookingdate'], '%Y-%m-%d').date(),
                adultticket=booking['adults'],
                childticket=booking['children'],
                total_price=booking['total_price'],
                paid=True,
                user_id=current_user.id
            )
        else:  
            new_booking = HotelBooking(
                checkin=datetime.datetime.strptime(booking['checkin'], '%Y-%m-%d').date(),
                checkout=datetime.datetime.strptime(booking['checkout'], '%Y-%m-%d').date(),
                adults=booking['adults'],
                children=booking['children'],
                total_price=booking['total_price'],
                paid=True,
                room_id=room.id,
                user_id=current_user.id
            )

        db.session.add(new_booking)
        db.session.commit()
        session.pop('booking')

        flash("Booking successfully completed and paid!", "success")
        return redirect(url_for('views.my_bookings'))

    return render_template("payment.html", booking=booking, room=room)



@views.route('/my-bookings')
@login_required
def my_bookings():
    from .models import Booking, HotelBooking


    ticket_bookings = Booking.query.filter_by(user_id=current_user.id).all()

    hotel_bookings = HotelBooking.query.filter_by(user_id=current_user.id).all()

    return render_template('my_bookings.html', ticket_bookings=ticket_bookings, hotel_bookings=hotel_bookings, user=current_user)


#Admin functions

@views.route('/admin')
@login_required
def admin():

    if not current_user.is_admin:
        flash('You are not authorized to view that page.', 'error')
        return redirect(url_for('views.home'))

    from .models import Booking, HotelBooking, Room

    users = User.query.all()
    bookings = Booking.query.all()
    hotel_bookings = HotelBooking.query.all()
    rooms = Room.query.all()

    return render_template('admin.html', users=users, bookings=bookings,
                           hotel_bookings=hotel_bookings, rooms=rooms,
                           user=current_user)


@views.route('/toggle-admin/<int:user_id>', methods=['POST'])
@login_required
def toggle_admin(user_id):
    if not current_user.is_admin:
        flash('Unauthorized', 'error')
        return redirect(url_for('views.home'))

    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f"{user.email} admin status changed.", "success")
    return redirect(url_for('views.admin'))

@views.route('/add-room', methods=['GET', 'POST'])
@login_required
def add_room():

    if not current_user.is_admin:
        flash('You are not authorized to view that page.', 'error')
        return redirect(url_for('views.home'))

    from .models import Room

    

    if request.method == 'POST':

        room_type = request.form.get('room_type')
        room_number = request.form.get('room_number') 
        max_adults = request.form.get('max_adults', type=int)
        max_children = request.form.get('max_children', type=int)
        price = request.form.get('price', type=float)

      
        if not room_number or not room_type:
            flash("Room number and room type are required.", "error")
            return redirect(url_for('views.add_room'))

        if max_adults is None or max_adults <= 0:
            flash("Max adults must be a positive number.", "error")
            return redirect(url_for('views.add_room'))

        if max_children is None or max_children < 0:
            flash("Max children must be zero or a positive number.", "error")
            return redirect(url_for('views.add_room'))

        if price is None or price <= 0:
            flash("Price per night must be a positive number.", "error")
            return redirect(url_for('views.add_room'))

        existing_room = Room.query.filter_by(room_number=room_number).first()
        if existing_room:
            flash("Room number already exists.", "error")
            return redirect(url_for('views.add_room'))


        new_room = Room(
            room_number=room_number,
            room_type=room_type,
            max_adults=max_adults,
            max_children=max_children,
            price_per_night=price
        )
        db.session.add(new_room)
        db.session.commit()

        flash("Room added successfully!", "success")
        return redirect(url_for('views.add_room'))


    return render_template('add_room.html' , user=current_user )