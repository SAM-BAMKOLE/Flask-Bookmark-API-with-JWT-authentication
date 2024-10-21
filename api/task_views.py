from flask import Blueprint, request, jsonify
from .constants import RESPONSE, STATUS
from .models import Task
from flask_jwt_extended import get_jwt_identity, jwt_required
from . import db
from datetime import datetime
from .decorators import verify_ownership

task_views = Blueprint("task_views", __name__)

@task_views.route("/create", methods=["POST"])
@jwt_required()
def create_task():

    title = request.form.get("title") if request.content_type == "application/x-www-form-urlencoded"  or request.content_type == "application/form-data" else request.get_json().get("name")
    description = request.form.get("description") if request.content_type == "application/x-www-form-urlencoded"  or request.content_type == "application/form-data" else request.get_json().get("description")
    date = request.form.get("datetime") if request.content_type == "application/x-www-form-urlencoded"  or request.content_type == "application/form-data" else request.get_json().get("datetime")

    if not title or not description or not date:
        return jsonify({ "status": STATUS.ERROR, "message": "Title, description and date are required"}), RESPONSE.BAD_REQUEST
    
    new_task = Task(title=title, description=description, datetime=datetime.fromisoformat(date), creator=get_jwt_identity())

    db.session.add(new_task)
    db.session.commit()

    return jsonify({ "status": STATUS.SUCCESS, "message": "New task created" }), RESPONSE.CREATED

@task_views.route("/<taskId>")
@jwt_required()
@verify_ownership
def get_task(taskId):
    task = Task.query.get(taskId)

    if not task:
        return jsonify({ "status": STATUS.ERROR, "message": "Invalid task id, does not exist" }), RESPONSE.BAD_REQUEST
    
    return jsonify({ "status": STATUS.SUCCESS, "task": task.to_json() })

@task_views.route("/<taskId>")
@jwt_required()
def delete_task(taskId):
    task = Task.query.get(taskId)

    if not task:
        return jsonify({ "status": STATUS.ERROR, "message": "Invalid task id, does not exist" }), RESPONSE.BAD_REQUEST
    
    deleted = Task.query.delete(id=taskId)

    if not deleted:
        return jsonify({ "status": STATUS.ERROR, "message": f"Unable to delete task with id {taskId}" }), RESPONSE.INTERNAL_SERVER_ERROR
    
    db.session.commit()
    return jsonify({ "status": STATUS.SUCCESS, "message": "Task deleted" })

@task_views.route("/get-all")
def get_all_tasks():
    all_tasks = Task.query.all()

    tasks = [task.to_json() for task in all_tasks]

    return jsonify({ "tasks": tasks })