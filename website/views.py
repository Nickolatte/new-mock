from flask import Blueprint,render_template, request, flash


views = Blueprint('views', __name__)


@views.route('/')
def home():
    return render_template('home.html')

@views.route('/aboutus')
def aboutus():
    return render_template('about.html')

@views.route('/login' , methods=['GET', 'POST'])
def login():
    data = request.form
    print(data)
    return render_template('login.html')

@views.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email= request.form.get('email')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(email) < 4:
            flash ('Email must be greater than 4 characters.', category='error')
            pass
        elif len(firstName) < 2:
            flash ('First name must be greater than 2 characters.', category='error')
            pass
        elif len(lastName) < 1:
            flash ('Last name must be greater than 1 character.', category='error')    
            pass
        elif password1 != password2:
            flash ('Passwords don\'t match.', category='error')
            pass
        elif len(password1) < 7:
            flash ('Password must be at least 7 characters.', category='error')
            pass
    return render_template('signup.html')



