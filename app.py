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
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        if User.query.filter_by(username=data['username']).first():
            return jsonify({"error": "Username already exists"}), 400
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Email already exists"}), 400
        
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            is_volunteer=data.get('is_volunteer', False),
            skills=data.get('skills', ''),
            experience=data.get('experience', ''),
            location=data.get('location', '')
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return jsonify({"message": "Registration successful"})
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = User.query.filter_by(username=data['username']).first()
        if user and check_password_hash(user.password_hash, data['password']):
            login_user(user)
            return jsonify({"message": "Login successful"})
        return jsonify({"error": "Invalid credentials"}), 401
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"})

@app.route('/request_resource', methods=['POST'])
@login_required
def request_resource():
    data = request.form
    new_request = ResourceRequest(
        user_id=current_user.id,
        resource_type=data['resource_type'],
        description=data['description'],
        location=data['location']
    )
    db.session.add(new_request)
    db.session.commit()
    return jsonify({"message": "Resource request created successfully"})

@app.route('/view_requests')
@login_required
def view_requests():
    if current_user.is_volunteer:
        requests = ResourceRequest.query.order_by(ResourceRequest.created_at.desc()).all()
    else:
        requests = ResourceRequest.query.filter_by(user_id=current_user.id).all()
    return render_template('requests.html', requests=requests)

@app.route('/update_request_status/<int:request_id>', methods=['POST'])
@login_required
def update_request_status(request_id):
    if not current_user.is_volunteer:
        return jsonify({"error": "Unauthorized"}), 403
    
    request = ResourceRequest.query.get_or_404(request_id)
    request.status = request.form['status']
    db.session.commit()
    return jsonify({"message": "Status updated successfully"})

    