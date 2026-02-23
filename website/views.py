from flask import Blueprint,render_template, request


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
            pass
        elif len(firstName) < 2:
            pass
        elif len(lastName) < 2:
            pass
        elif len(password1) < 7:
            pass
    return render_template('signup.html')



