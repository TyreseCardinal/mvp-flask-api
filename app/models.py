from app import db

class Users(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationship to Projects
    projects = db.relationship('Projects', back_populates='user')
    
    # Relationship to UserProfile (One-to-One)
    profile = db.relationship('UserProfile', back_populates='user', uselist=False)

    # Relationship to UserSettings (One-to-One)
    settings = db.relationship('UserSettings', back_populates='user', uselist=False)
    
    # Relationship to Notifications
    notifications = db.relationship('Notifications', back_populates='user')

    # Relationship to CalendarEvents
    calendar_events = db.relationship('CalendarEvents', back_populates='user')

class Projects(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationship to Tasks
    tasks = db.relationship('Tasks', back_populates='project')
    
    # Relationship to Users
    user = db.relationship('Users', back_populates='projects')

class Tasks(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.Enum('To Do', 'In Progress', 'Done'), default='To Do')
    due_date = db.Column(db.Date)
    priority = db.Column(db.Enum('Low', 'Medium', 'High'), default='Medium')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationship to Projects
    project = db.relationship('Projects', back_populates='tasks')

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'priority': self.priority,
            'created_at': self.created_at.isoformat()
        }

class UserProfile(db.Model):
    __tablename__ = 'user_profile'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    profile_picture = db.Column(db.String(255))
    bio = db.Column(db.Text)
    
    # Relationship to Users
    user = db.relationship('Users', back_populates='profile')

class UserSettings(db.Model):
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notifications = db.Column(db.Boolean, default=True)
    theme = db.Column(db.String(20), default='light')
    language = db.Column(db.String(10), default='en')
    
    # Relationship to Users
    user = db.relationship('Users', back_populates='settings')

class Notifications(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('unread', 'read'), default='unread')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationship to Users
    user = db.relationship('Users', back_populates='notifications')

class CalendarEvents(db.Model):
    __tablename__ = 'calendar_events'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    
    # Relationship to Users
    user = db.relationship('Users', back_populates='calendar_events')


