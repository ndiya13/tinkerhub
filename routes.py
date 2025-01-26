from flask import render_template, redirect, url_for, flash, request, jsonify, Blueprint
from flask_login import login_required, current_user
from functools import wraps
from __init__ import db
from models import User, VolunteerApplication, Disaster, DisasterResource, Activity

# Create a Blueprint
main = Blueprint('main', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied.', 'error')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/login')
def login():
    return render_template('login.html')

@main.route('/admin')
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

def get_recent_activities(limit=5):
    return Activity.query.order_by(Activity.created_at.desc()).limit(limit).all()

# ... (rest of your routes) 