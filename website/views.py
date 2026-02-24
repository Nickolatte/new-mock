from flask import Blueprint, render_template, request, flash, redirect, url_for
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
        email= request.form.get('email')
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
            new_user = User(email=email, first_name=firstName, last_name=lastName, password=generate_password_hash(
                password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.signup'))

    return render_template('signup.html')


@views.route('/booking', methods=['GET', 'POST'])
@login_required
def booking():
    if request.method == 'POST':
        import datetime
        booking_date_str = request.form.get('date')
        adults = request.form.get('adults', type=int)
        children = request.form.get('children', type=int)
        if not booking_date_str:
            flash('Please select a booking date.', category='error')
        elif (adults is None or adults < 0) or (children is None or children < 0):
            flash('Ticket numbers must be zero or positive.', category='error')
        else:
            from .models import Booking
            try:
                booking_date = datetime.datetime.strptime(booking_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format.', category='error')
                return render_template('booking.html', user=current_user)
            new_booking = Booking(
                bookingdate=booking_date,
                adultticket=adults,
                childticket=children,
                user_id=current_user.id
            )
            db.session.add(new_booking)
            db.session.commit()
            flash('Booking successful!', category='success')
            return redirect(url_for('views.booking'))
    return render_template('booking.html', user=current_user)



