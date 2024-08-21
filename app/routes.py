from flask import Blueprint, jsonify, request
from app import db
from app.models import Users, Projects, Tasks
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash


api = Blueprint('api', __name__)

# Get all tasks
@api.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Tasks.query.all()  # Use the correct model name
    return jsonify([task.to_dict() for task in tasks])

# Get a single task by ID
@api.route('/tasks/<int:id>', methods=['GET'])
def get_task(id):
    task = Tasks.query.get_or_404(id)  # Use the correct model name
    return jsonify(task.to_dict())

# Create a new task
@api.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    task = Tasks(
        title=data['title'],
        description=data['description'],
        status=data.get('status', 'To Do'),
        due_date=data.get('due_date'),
        priority=data.get('priority', 'Medium'),
        project_id=data['project_id']
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201

# Update an existing task by ID
@api.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    data = request.get_json()
    task = Tasks.query.get_or_404(id)  # Use the correct model name
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.status = data.get('status', task.status)
    task.due_date = data.get('due_date', task.due_date)
    task.priority = data.get('priority', task.priority)
    task.project_id = data.get('project_id', task.project_id)
    db.session.commit()
    return jsonify(task.to_dict())

# Delete a task by ID
@api.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Tasks.query.get_or_404(id)  # Use the correct model name
    db.session.delete(task)
    db.session.commit()
    return '', 204



# Get all projects
@api.route('/projects', methods=['GET'])
def get_projects():
    projects = Projects.query.all()  # Use the correct model name
    return jsonify([{
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'start_date': project.start_date,
        'end_date': project.end_date
    } for project in projects])

# Get a single project by ID
@api.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    project = Projects.query.get_or_404(project_id)  # Use the correct model name
    return jsonify({
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'start_date': project.start_date,
        'end_date': project.end_date
    })

# Create a new project
@api.route('/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    project = Projects(
        name=data['name'],
        description=data['description'],
        start_date=data['start_date'],
        end_date=data['end_date']
    )
    db.session.add(project)
    db.session.commit()
    return jsonify({
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'start_date': project.start_date,
        'end_date': project.end_date
    }), 201

# Update an existing project by ID
@api.route('/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    data = request.get_json()
    project = Projects.query.get_or_404(project_id)  # Use the correct model name
    project.name = data.get('name', project.name)
    project.description = data.get('description', project.description)
    project.start_date = data.get('start_date', project.start_date)
    project.end_date = data.get('end_date', project.end_date)
    db.session.commit()
    return jsonify({
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'start_date': project.start_date,
        'end_date': project.end_date
    })

# Delete a project by ID
@api.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    project = Projects.query.get_or_404(project_id)  # Use the correct model name
    db.session.delete(project)
    db.session.commit()
    return '', 204

# User Registration
@api.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = Users(username=data['username'], email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

# User Login
@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = Users.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity={'id': user.id, 'username': user.username})
        return jsonify(access_token=access_token), 200
    return jsonify({'message': 'Invalid credentials'}), 401