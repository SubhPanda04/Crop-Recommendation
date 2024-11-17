# Importing essential libraries and modules
from flask import Flask, render_template, request, redirect, url_for, session, flash
import numpy as np
import pickle
import bcrypt
import pymysql
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError

# Initialize Flask app
app = Flask(__name__)

# Loading the crop recommendation model
crop_recommendation_model_path = 'models/RandomForest.pkl'
crop_recommendation_model = pickle.load(open(crop_recommendation_model_path, 'rb'))

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'soil'
app.secret_key = 'your_secret_key_here'


# Function to get a database connection
def get_db_connection():
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/test-db')
def test_db():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT DATABASE()")
            db = cursor.fetchone()
        connection.close()
        return f"Connected to database: {db['DATABASE()']}"
    except Exception as e:
        return f"Error: {e}"


# WTForms classes for user registration and login
class RegisterForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired()])
    email = StringField("Email or Username", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign Up")

    def validate_email(self, field):
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email=%s", (field.data,))
            user = cursor.fetchone()
        connection.close()
        if user:
            raise ValidationError('Email Already Taken')
        

class LoginForm(FlaskForm):
    email = StringField("Email or Username", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")


# Route to render the home page
@app.route('/')
def home():
    title = 'Harvestify - Home'
    return render_template('index.html', title=title)



# Route to render the crop recommendation form page
@app.route('/crop-recommend')
def crop_recommend():
    if 'user_id' not in session:
        flash("Please log in to access crop recommendations.")
        return redirect(url_for('login'))
    return render_template('input.html', title='Harvestify - Crop Recommendation')

@app.route('/crop-predict', methods=['POST'])
def crop_prediction():
    if 'user_id' not in session:
        flash("Please log in to get crop recommendations.")
        return redirect(url_for('login'))
    if request.method == 'POST':
        N = float(request.form['nitrogen'])
        P = float(request.form['phosphorus'])
        K = float(request.form['potassium'])
        temperature = float(request.form['temperature'])
        humidity = float(request.form['humidity'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])

        # Remove city and state dependency
        # Predict the crop
        data = np.array([[N, P, K,temperature, humidity, ph, rainfall]])
        crop_probabilities = crop_recommendation_model.predict_proba(data)[0]
        
        # Get top 3 predictions with their probability
        top_3_indices = np.argsort(crop_probabilities)[-3:][::-1]
        top_3_crops = [(crop_recommendation_model.classes_[index], crop_probabilities[index]) for index in top_3_indices]

        # Render the result template with top 3 predictions
        return render_template('dashboard.html', top_crops=top_3_crops, title='Harvestify - Crop Recommendation', nitrogen=N,
                               phosphorus=P,
                               potassium=K,
                               temperature=temperature,
                               humidity=humidity,
                               ph=ph,
                               rainfall=rainfall)


    else:
        return "No data found", 404


# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Store data in the database
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
            connection.commit()
        connection.close()

        return redirect(url_for('login'))  # Redirect to the login page after successful signup
    else:
        print(form.errors)  # Print out form errors for debugging
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cursor.fetchone()
        connection.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['user_id'] = user['id']
            return redirect(url_for('crop_recommend'))
        else:
            flash("Login failed. Please check your email and password.")
            return render_template('signup.html', form=form)
            #return redirect(url_for('login'))

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out successfully.")
    return redirect('/')



# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
