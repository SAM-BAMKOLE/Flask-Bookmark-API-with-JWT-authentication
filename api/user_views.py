from flask import Blueprint, jsonify, request
from .models import User
from .constants import RESPONSE, STATUS
from typing import List
from flask_jwt_extended import jwt_required
from . import db

user_views = Blueprint("user_views", __name__)

@user_views.route("/details/<userId>")
@jwt_required()
def get_user(userId):
    found_user = User.query.get(userId)


    if not found_user:
        return jsonify({ "status": STATUS.ERROR, "message": "Invalid user id, user not found" }), RESPONSE.NOT_FOUND
    
    tasks = []
    for task in found_user.tasks:
        tasks.append(task.to_json())

    found_user = found_user.to_json()
    found_user['tasks'] = tasks
    

    del found_user['password']

    return jsonify({ "status": STATUS.SUCCESS, "data": found_user })

@user_views.route("/details/<userId>", methods=["PATCH"])
@jwt_required()
def update_user(userId):
    found_user = User.query.get(userId)

    if not found_user:
        return jsonify({ "status": STATUS.ERROR, "message": "Invalid user id, user not found" }), RESPONSE.NOT_FOUND
    
    name = request.form.get("name") if request.content_type == "application/x-www-form-urlencoded" or request.content_type == "application/form-data" else request.get_json().get("name")
    value = request.form.get("value") if request.content_type == "application/x-www-form-urlencoded" or request.content_type == "application/form-data" else request.get_json().get("value")

    if not hasattr(found_user, name):
        return jsonify({ "status": STATUS.ERROR, "message": "Invalid data, not found in object" }), RESPONSE.BAD_REQUEST
    
    # found_user.__dict__[name] = value
    if name == "firstname":
        found_user.firstname = value
    elif name == "lastname":
        found_user.lastname = value
    elif name == "email":
        found_user.email = value
    else:
        return jsonify({ "status": STATUS.ERROR, "message": "Cannot update this property" }), RESPONSE.BAD_REQUEST

    db.session.commit()

    return jsonify({ "status": STATUS.SUCCESS, "message": f"{name} updated" })
