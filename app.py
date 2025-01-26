from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
import requests
from datetime import datetime
from functools import wraps

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

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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

@app.route('/admin')
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_volunteers = User.query.filter_by(is_volunteer=True).count()
    pending_applications = VolunteerApplication.query.filter_by(status='pending').count()
    active_disasters = Disaster.query.filter_by(status='active').count()
    
    recent_activities = [
        {
            'icon': 'fas fa-user-plus',
            'description': 'New user registered',
            'timestamp': '2 minutes ago'
        },
        # Add more activities
    ]
    
    users = User.query.all()
    volunteer_applications = VolunteerApplication.query.filter_by(status='pending').all()
    disasters = Disaster.query.all()
    
    return render_template('admin_dashboard.html',
                         total_users=total_users,
                         total_volunteers=total_volunteers,
                         pending_applications=pending_applications,
                         active_disasters=active_disasters,
                         recent_activities=recent_activities,
                         users=users,
                         volunteer_applications=volunteer_applications,
                         disasters=disasters)

@app.route('/admin/approve-volunteer/<int:id>', methods=['POST'])
@admin_required
def approve_volunteer(id):
    application = VolunteerApplication.query.get_or_404(id)
    application.status = 'approved'
    application.user.is_volunteer = True
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/reject-volunteer/<int:id>', methods=['POST'])
@admin_required
def reject_volunteer(id):
    application = VolunteerApplication.query.get_or_404(id)
    application.status = 'rejected'
    db.session.commit()
    return jsonify({'success': True})
