from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from datetime import datetime
from functools import wraps
from flask_wtf.csrf import CSRFProtect

from extensions import db, login_manager
from models import User, VolunteerApplication, Disaster, DisasterResource, Activity

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///disaster_relief.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
csrf = CSRFProtect(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_volunteers': User.query.filter_by(is_volunteer=True).count(),
        'pending_applications': VolunteerApplication.query.filter_by(status='pending').count(),
        'active_disasters': Disaster.query.filter_by(status='active').count()
    }
    
    recent_activities = get_recent_activities()
    pending_applications = VolunteerApplication.query.filter_by(status='pending').all()
    active_disasters = Disaster.query.filter_by(status='active').all()
    
    return render_template('admin_dashboard.html',
                         stats=stats,
                         recent_activities=recent_activities,
                         pending_applications=pending_applications,
                         active_disasters=active_disasters)

@app.route('/admin/approve-volunteer/<int:id>', methods=['POST'])
@login_required
@admin_required
def approve_volunteer(id):
    try:
        application = VolunteerApplication.query.get_or_404(id)
        application.status = 'approved'
        application.user.is_volunteer = True
        db.session.commit()
        return jsonify({'success': True, 'message': 'Volunteer approved successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/reject-volunteer/<int:id>', methods=['POST'])
@login_required
@admin_required
def reject_volunteer(id):
    try:
        application = VolunteerApplication.query.get_or_404(id)
        application.status = 'rejected'
        db.session.commit()
        return jsonify({'success': True, 'message': 'Volunteer rejected successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/edit-disaster/<int:id>', methods=['GET'])
@login_required
def edit_disaster(id):
    if not current_user.is_admin:
        flash('Unauthorized access', 'error')
        return redirect(url_for('admin_dashboard'))
    
    disaster = Disaster.query.get_or_404(id)
    return render_template('edit_disaster.html', disaster=disaster)

@app.route('/admin/delete-disaster/<int:id>', methods=['POST'])
@login_required
def delete_disaster(id):
    if not current_user.is_admin:
        flash('Unauthorized access', 'error')
        return redirect(url_for('admin_dashboard'))
    
    try:
        disaster = Disaster.query.get_or_404(id)
        db.session.delete(disaster)
        db.session.commit()
        flash('Disaster zone deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting disaster zone: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add-disaster')
@login_required
def add_disaster():
    if not current_user.is_admin:
        flash('Unauthorized access', 'error')
        return redirect(url_for('admin_dashboard'))
        
    return render_template('add_disaster.html')

# Helper functions
def get_recent_activities(limit=5):
    # Implement your activity logging logic here
    return []

# Create all database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
