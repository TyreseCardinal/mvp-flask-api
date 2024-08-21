from app import db

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationship to Projects
    projects = db.relationship('Projects', back_populates='user')

class Projects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationship to Tasks
    tasks = db.relationship('Tasks', back_populates='project')
    user = db.relationship('Users', back_populates='projects')

class Tasks(db.Model):
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
