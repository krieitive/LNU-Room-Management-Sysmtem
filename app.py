from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_manager, LoginManager
from flask_login import login_required, current_user
from sqlalchemy import text

local_server = True
app = Flask(__name__)
app.secret_key = 'management'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/management'
db = SQLAlchemy(app)

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(50), unique = True)
    password = db.Column(db.String(1000))

class Booking(db.Model):
    __tablename__ = 'booking'  # Explicitly specify the table name if needed
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Ensure auto-increment is enabled
    user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    gender = db.Column(db.String(10))
    room = db.Column(db.String(155))
    building = db.Column(db.String(155))
    time = db.Column(db.String(155), nullable=False)
    date = db.Column(db.String(155), nullable=False)
    slot = db.Column(db.String(155))
    description = db.Column(db.String(155))
    classcode = db.Column(db.String(15))
    subjectcode = db.Column(db.String(15))


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/test')
def test():
    try:
        Test.query.all()
        return 'My database is connected'
    except:
        return 'My db is not connected'

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/buildings')
def buildings():
    return render_template('buildings.html')

@app.route('/rooms')
def rooms():
    return render_template('rooms.html')

@app.route('/bookings', methods=['POST', 'GET'])
@login_required
def bookings():
    if request.method == "POST":
        user = request.form.get('user')
        gender = request.form.get('gender')
        room = request.form.get('room')
        building = request.form.get('building')
        time = request.form.get('time')
        date = request.form.get('date')
        slot = request.form.get('slot')
        description = request.form.get('description')
        classcode = request.form.get('classcode')
        subjectcode = request.form.get('subjectcode')

        print(f"Current user ID: {current_user.id}")  # Add this line before creating a booking

        # Create a new Booking instance without specifying 'id'
        new_booking = Booking(
        user=current_user.id,  # Ensure this is set to the current user's ID
        gender=gender,
        room=room,
        building=building,
        time=time,
        date=date,
        slot=slot,
        description=description,
        classcode=classcode,
        subjectcode=subjectcode
)


        try:
            # Add the new booking to the session and commit
            db.session.add(new_booking)
            db.session.commit()
            flash("Booking successful!", "success")  # Success message
        except Exception as e:
            db.session.rollback()  # Rollback the session in case of error
            flash(f"An error occurred: {str(e)}", "danger")  # Flash error message

    # Render the bookings.html template for both GET and POST
    return render_template('bookings.html')


@app.route('/dashboard')  # orig: patient
@login_required
def dashboard():
    userid = current_user.id
    query = db.session.execute(text("SELECT * FROM booking WHERE user=:user"), {'user': userid}).fetchall()
    return render_template('dashboard.html', query=query)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()
        if user:
            flash("Email already exist.", "warning")
            return render_template('/signup.html')
        encpassword = generate_password_hash(password)
        newuser = User(username = username, email = email, password=encpassword)
        db.session.add(newuser)
        db.session.commit()
        flash("Signup success, please login.", "success")
        return render_template('login.html')

    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login Successful", "primary")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials. Please try again.", "danger")
            return redirect(url_for('login'))  # Redirect back to login

    return render_template('login.html')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()  # This will ensure session is cleared after logout
    flash("You have been logged out", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
