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
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email=%s", (field.data,))
            user = cursor.fetchone()
        connection.close()
        if user:
            raise ValidationError('Email Already Taken')

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

# Route to render the home page
@app.route('/')
def home():
    title = 'Harvestify - Home'
    return render_template('home1.html', title=title)

# Route to render the crop recommendation form page
@app.route('/crop-recommend')
def crop_recommend():
    return render_template('crop.html', title='Harvestify - Crop Recommendation')

# Route to handle crop prediction using data from MySQL
@app.route('/crop-predict', methods=['GET'])
def crop_prediction():
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT nitrogen, phosphorous, potassium, temperature, humidity, ph, rainfall FROM crop_recommendation WHERE id = 1")
        result = cursor.fetchone()
    connection.close()

    if result:
        # Retrieve data from the database row
        N = result['nitrogen']
        P = result['phosphorous']
        K = result['potassium']
        temperature = result['temperature']
        humidity = result['humidity']
        ph = result['ph']
        rainfall = result['rainfall']

        # Predict the crop using the retrieved values
        data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
        crop_probabilities = crop_recommendation_model.predict_proba(data)[0]

        # Get top 3 predictions (crop names only)
        top_3_indices = np.argsort(crop_probabilities)[-3:][::-1]
        top_3_crops = [crop_recommendation_model.classes_[index] for index in top_3_indices]

        # Render the result template with prediction
        return render_template('result_img.html', top_crops=top_3_crops, title='Harvestify - Crop Recommendation')

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

        return redirect(url_for('login'))

    return render_template('register.html', form=form)

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
            return redirect(url_for('login'))

    return render_template('login.html', form=form)

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
