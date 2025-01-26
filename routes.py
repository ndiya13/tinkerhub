from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from __init__ import db
from models import User, VolunteerApplication, Disaster, DisasterResource, Activity

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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

# ... (rest of your routes) 