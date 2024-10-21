from functools import wraps
from flask import  jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from .models import Task
from .constants import STATUS, RESPONSE


# Mock function to simulate database query
def get_data_owner_id(task_id):
    task = Task.query.get(task_id)

    if not task:
        return jsonify({ "status": STATUS.ERROR, "message": "Invalid task id, does not exist" }), RESPONSE.BAD_REQUEST
    

    return task.creator

def verify_ownership(f):
    @wraps(f)
    # @jwt_required()
    def decorated_function(*args, **kwargs):
        # Get the current user ID from the JWT token
        current_user_id = get_jwt_identity()

        # Get the data ID from the URL parameters 
        task_id = kwargs.get('taskId')

        # Get the owner ID of the data from the database
        owner_id = get_data_owner_id(task_id)

        # Compare the current user ID with the owner ID
        if current_user_id != owner_id:
            return jsonify({ "status": STATUS.ERROR, "message": "Unauthorized, not allowed to access this resource because it was not created by you" }), RESPONSE.UNAUTHORIZED
    

        return f(*args, **kwargs)
    
    return decorated_function
