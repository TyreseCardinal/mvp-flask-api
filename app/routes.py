from flask import Blueprint, jsonify, request
from app import db
from app.models import Users, Projects, Tasks
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

api = Blueprint("api", __name__)

# Task Routes

# GET Task by ID
@api.route("/tasks", methods=["GET"])
@jwt_required()
def get_tasks():
    tasks = Tasks.query.all()
    return jsonify([task.to_dict() for task in tasks])

# GET All Tasks
@api.route("/tasks/<int:id>", methods=["GET"])
@jwt_required()
def get_task(id):
    task = Tasks.query.get_or_404(id)
    return jsonify(task.to_dict())

# POST Create A New Task
@api.route("/tasks", methods=["POST"])
@jwt_required()
def create_task():
    data = request.get_json()
    if not all(key in data for key in ("title", "project_id")):
        return jsonify({"message": "Missing required fields"}), 400
    try:
        due_date = (
            datetime.strptime(data.get("due_date"), "%Y-%m-%d")
            if data.get("due_date")
            else None
        )
        task = Tasks(
            title=data["title"],
            description=data.get("description"),
            status=data.get("status", "To Do"),
            due_date=due_date,
            priority=data.get("priority", "Medium"),
            project_id=data["project_id"],
        )
        db.session.add(task)
        db.session.commit()
        return jsonify(task.to_dict()), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400

# PUT Update existing tasks
@api.route("/tasks/<int:id>", methods=["PUT"])
@jwt_required()
def update_task(id):
    data = request.get_json()
    task = Tasks.query.get_or_404(id)
    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.status = data.get("status", task.status)
    task.due_date = (
        datetime.strptime(data.get("due_date"), "%Y-%m-%d")
        if data.get("due_date")
        else task.due_date
    )
    task.priority = data.get("priority", task.priority)
    task.project_id = data.get("project_id", task.project_id)
    db.session.commit()
    return jsonify(task.to_dict())

# DELETE Task by ID
@api.route("/tasks/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_task(id):
    task = Tasks.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return "", 204

# Project Routes

# GET All Projects
@api.route("/projects", methods=["GET"])
@jwt_required()
def get_projects():
    projects = Projects.query.all()
    return jsonify(
        [
            {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "created_at": (
                    project.created_at.isoformat() if project.created_at else None
                ),
            }
            for project in projects
        ]
    )

# GET Project by Project ID
@api.route("/projects/<int:project_id>", methods=["GET"])
@jwt_required()
def get_project(project_id):
    project = Projects.query.get_or_404(project_id)
    return jsonify(
        {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "created_at": (
                project.created_at.isoformat() if project.created_at else None
            ),
        }
    )

# POST Create A New Project
@api.route("/projects", methods=["POST"])
@jwt_required()
def create_project():
    data = request.get_json()
    user_id = get_jwt_identity()["id"]  # Get the user ID from the JWT token
    try:
        project = Projects(
            user_id=user_id,
            name=data["name"],
            description=data.get("description"),
        )
        db.session.add(project)
        db.session.commit()
        return jsonify({
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "created_at": project.created_at.isoformat()
        }), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400

# PUT Update existing project details
@api.route("/projects/<int:project_id>", methods=["PUT"])
@jwt_required()
def update_project(project_id):
    data = request.get_json()
    project = Projects.query.get_or_404(project_id)
    project.name = data.get("name", project.name)
    project.description = data.get("description", project.description)
    db.session.commit()
    return jsonify(
        {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "created_at": (
                project.created_at.isoformat() if project.created_at else None
            ),
        }
    )

# DELETE Project by Project ID
@api.route("/projects/<int:project_id>", methods=["DELETE"])
@jwt_required()
def delete_project(project_id):
    project = Projects.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return "Project Successfully deleted.", 204


#  Login and Register Routes

# POST Register New User
@api.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not all(key in data for key in ("username", "email", "password")):
        return jsonify({"message": "Missing required fields"}), 400
    hashed_password = generate_password_hash(data["password"], method="pbkdf2:sha256")
    new_user = Users(
        username=data["username"], email=data["email"], password=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201

# POST Login User with authenticated credentials
@api.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not all(key in data for key in ("email", "password")):
        return jsonify({"message": "Missing required fields"}), 400
    user = Users.query.filter_by(email=data["email"]).first()
    if user and check_password_hash(user.password, data["password"]):
        access_token = create_access_token(
            identity={"id": user.id, "username": user.username}
        )
        return jsonify({
            "access_token": access_token,
            "user_id": user.id
        }), 200
    return jsonify({"message": "Invalid credentials"}), 401