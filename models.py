class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    is_volunteer = db.Column(db.Boolean, default=False)

class VolunteerApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    skills = db.Column(db.Text)
    experience = db.Column(db.Text)
    location = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('volunteer_application', lazy=True)) 

class Disaster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # high, medium, low
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, resolved
    assigned_volunteers = db.Column(db.Integer, default=0)
    
    # Relationship with required resources
    required_resources = db.relationship('DisasterResource', backref='disaster', lazy=True)

class DisasterResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    disaster_id = db.Column(db.Integer, db.ForeignKey('disaster.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    fulfilled = db.Column(db.Boolean, default=False) 