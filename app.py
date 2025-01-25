from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
import requests
from datetime import datetime
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///disaster_relief.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_volunteer = db.Column(db.Boolean, default=False)
    skills = db.Column(db.String(500))
    experience = db.Column(db.String(500))
    location = db.Column(db.String(200))

class ResourceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    resource_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    location = db.Column(db.String(200))
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Disaster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gdacs_id = db.Column(db.String(100), unique=True)
    disaster_type = db.Column(db.String(100))
    location = db.Column(db.String(200))
    severity = db.Column(db.String(50))
    description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def home():
    disasters = Disaster.query.order_by(Disaster.created_at.desc()).limit(10).all()
    return render_template('home.html', disasters=disasters)

@app.route('/update_disasters')
def update_disasters():
    # GDACS API endpoint
    gdacs_url = "https://www.gdacs.org/feed.aspx?format=json"
    try:
        response = requests.get(gdacs_url)
        data = response.json()
        # Process and store disaster data
        # You'll need to implement the actual data processing based on GDACS API response
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})