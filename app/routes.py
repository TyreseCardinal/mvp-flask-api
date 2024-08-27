from flask import Blueprint, jsonify, request
from app import db
from app.models import Users, Projects, Tasks, UserProfile, UserSettings, Notifications, CalendarEvents
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_cors import cross_origin

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
    
    # Check for missing fields
    if not all(key in data for key in ("username", "email", "password")):
        return jsonify({"message": "Missing required fields"}), 400

    # Check for duplicate username or email
    if Users.query.filter_by(username=data["username"]).first():
        return jsonify({"message": "Username already exists"}), 409
    
    if Users.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email already registered"}), 409

    # Hash the password
    hashed_password = generate_password_hash(data["password"], method="pbkdf2:sha256")
    
    # Create new user
    new_user = Users(
        username=data["username"], email=data["email"], password=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()

    # Create a default UserProfile for the new user
    new_profile = UserProfile(user_id=new_user.id)
    db.session.add(new_profile)
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


@api.route('/user_profile', methods=['GET'])
@jwt_required()
@cross_origin()
def get_user_profile():
    user_id = get_jwt_identity()
    user = profile.user_id  # Access the related Users object
    
    # Fetch the UserProfile for the current user
    profile = session.execute(select(UserProfile).filter_by(user_id=user_id)).scalar()

    
    if not profile:
        return jsonify({"message": "Profile not found"}), 404
    
    if user:
        return jsonify({
            "email": "user.email",
            "username": "user.username",  # Correctly retrieve the username
            "first_name": "profile.first_name",
            "last_name": "profile.last_name",
            "profile_picture": "profile.profile_picture",
            "bio": "profile.bio",
            "address": "profile.address",
            "phone_number": "profile.phone_number",
            "profile_picture": "profile.profile_picture",
            "date_of_birth": "profile.date_of_birth"
        }), 200

    else:
        return jsonify({'msg': 'User not found'}), 404


@api.route("/user_profile", methods=["POST"])
@jwt_required()
def update_user_profile():
    user_id = get_jwt_identity()['id']
    data = request.get_json()
    
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    user = Users.query.get(user_id)

    if not profile or not user:
        return jsonify({"message": "User profile not found"}), 404

    # Update Users table
    if "email" in data:
        user.email = data["email"]
    if "username" in data:
        user.username = data["username"]

    # Update UserProfile table
    if "first_name" in data:
        profile.first_name = data["first_name"]
    if "last_name" in data:
        profile.last_name = data["last_name"]
    if "bio" in data:
        profile.bio = data["bio"]
    if "profile_picture" in data:
        profile.profile_picture = data["profile_picture"]

    db.session.commit()

    return jsonify({"message": "Profile updated successfully"}), 200




@api.route('/user_settings', methods=['GET', 'POST'])
@jwt_required()
def manage_user_settings():
    user_id = get_jwt_identity()

    if request.method == 'GET':
        settings = UserSettings.query.filter_by(user_id=user_id).first()
        if settings:
            return jsonify({
                'notifications': settings.notifications,
                'theme': settings.theme,
                'language': settings.language
            })
        else:
            return jsonify({'error': 'Settings not found'}), 404

    if request.method == 'POST':
        data = request.json
        settings = UserSettings.query.filter_by(user_id=user_id).first()
        if not settings:
            settings = UserSettings(
                user_id=user_id,
                notifications=data.get('notifications', True),
                theme=data.get('theme', 'light'),
                language=data.get('language', 'en')
            )
            db.session.add(settings)
        else:
            settings.notifications = data.get('notifications', settings.notifications)
            settings.theme = data.get('theme', settings.theme)
            settings.language = data.get('language', settings.language)

        db.session.commit()
        return jsonify({'message': 'Settings updated successfully'})


@api.route('/notifications', methods=['GET', 'POST'])
@jwt_required()
def manage_notifications():
    user_id = get_jwt_identity()

    if request.method == 'GET':
        notifications = Notifications.query.filter_by(user_id=user_id).all()
        return jsonify([{
            'message': notification.message,
            'status': notification.status,
            'created_at': notification.created_at.isoformat()
        } for notification in notifications])

    if request.method == 'POST':
        data = request.json
        notification = Notifications(
            user_id=user_id,
            message=data['message'],
            status='unread'
        )
        db.session.add(notification)
        db.session.commit()
        return jsonify({'message': 'Notification created successfully'})


@api.route('/notifications/<int:notification_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def update_delete_notification(notification_id):
    user_id = get_jwt_identity()
    notification = Notifications.query.filter_by(id=notification_id, user_id=user_id).first()

    if not notification:
        return jsonify({'error': 'Notification not found'}), 404

    if request.method == 'PUT':
        data = request.json
        notification.status = data.get('status', notification.status)
        db.session.commit()
        return jsonify({'message': 'Notification updated successfully'})

    if request.method == 'DELETE':
        db.session.delete(notification)
        db.session.commit()
        return jsonify({'message': 'Notification deleted successfully'})


@api.route('/calendar_events', methods=['GET', 'POST'])
@jwt_required()
def manage_calendar_events():
    user_id = get_jwt_identity()

    if request.method == 'GET':
        events = CalendarEvents.query.filter_by(user_id=user_id).all()
        return jsonify([{
            'title': event.title,
            'date': event.date.isoformat(),
            'description': event.description
        } for event in events])

    if request.method == 'POST':
        data = request.json
        event = CalendarEvents(
            user_id=user_id,
            title=data['title'],
            date=data['date'],
            description=data.get('description')
        )
        db.session.add(event)
        db.session.commit()
        return jsonify({'message': 'Event created successfully'})


@api.route('/calendar_events/<int:event_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def update_delete_calendar_event(event_id):
    user_id = get_jwt_identity()
    event = CalendarEvents.query.filter_by(id=event_id, user_id=user_id).first()

    if not event:
        return jsonify({'error': 'Event not found'}), 404

    if request.method == 'PUT':
        data = request.json
        event.title = data.get('title', event.title)
        event.date = data.get('date', event.date)
        event.description = data.get('description', event.description)
        db.session.commit()
        return jsonify({'message': 'Event updated successfully'})

    if request.method == 'DELETE':
        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': 'Event deleted successfully'})