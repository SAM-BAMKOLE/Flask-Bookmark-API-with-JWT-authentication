from flask import Blueprint, jsonify, request
from .constants import STATUS, RESPONSE
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, jwt
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity, unset_jwt_cookies

auth = Blueprint("auth", __name__)

@auth.route("/signup", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        # if request.is_json
        if request.content_type == "application/x-www-form-urlencoded" or request.content_type == "multipart/form-data":
            firstname = request.form.get("firstname")
            lastname = request.form.get("lastname")
            email = request.form.get("email")
            password = request.form.get("password")
            confirmPassword = request.form.get("confirmPassword")
        else:
            data = request.get_json()
            firstname = data.get("firstname")
            lastname = data.get("lastname")
            email = data.get("email")
            password = data.get("password")
            confirmPassword = data.get("confirmPassword")
        
        # Validate
        if not firstname or not lastname or not email or not password:
            return jsonify({ "status": STATUS.ERROR, "message": "All fields are required" }), RESPONSE.BAD_REQUEST
        elif confirmPassword != password:
            return jsonify({ "status": STATUS.ERROR, "message": "Passwords do not match" }), RESPONSE.BAD_REQUEST
        
        # check if user already exists
        foundUser = User.query.filter(email==email)
        
        if isinstance(foundUser, User) :
            return jsonify({ "status": STATUS.ERROR, "message": "User already exists" }), RESPONSE.FORBIDDEN
        # hash user password
        hashed_password = generate_password_hash(password=password, method="scrypt", salt_length=16)
        new_user = User(firstname=firstname, lastname=lastname, password=hashed_password, email=email)
        # add to database
        db.session.add(new_user)
        db.session.commit()

        return jsonify({ "status": STATUS.SUCCESS, "message": "User created successfully" }), RESPONSE.CREATED

@auth.route("/signin", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        email = request.form.get("email") if request.content_type == "application/x-www-form-urlencoded" or request.content_type == "application/form-data" else request.get_json().get("email")
        password = request.form.get("email") if request.content_type == "application/x-www-form-urlencoded" or request.content_type == "application/form-data" else request.get_json().get("password")

        if not email or not password: return jsonify({ "status": STATUS.ERROR, "message": "All fields required" }), RESPONSE.BAD_REQUEST
        foundUser = User.query.filter_by(email=email).first()

        if not foundUser: return jsonify({ "status": STATUS.ERROR, "message": "Invalid email, user not found" }), RESPONSE.NOT_FOUND

        if check_password_hash(password=password, pwhash=foundUser.password):
            return jsonify({ "status": STATUS.ERROR, "message": "Incorrect password" }), RESPONSE.FORBIDDEN
        access_token = create_access_token(identity=foundUser.id)
        refresh_token = create_refresh_token(identity=foundUser.id)
        
        return jsonify({ "status": STATUS.SUCCESS, "message": "Logged in successfully", "accessToken": access_token })

@auth.route("/refresh", methods=["POST"])
@jwt_required()
def handle_refresh():
    user_identity = get_jwt_identity()
    access_token = create_access_token(identity=user_identity)
    return jsonify({ "accessToken": access_token })


@auth.route("/logout")
@jwt_required()
def logout():
    response = jsonify({ "message": "Logged out" })
    unset_jwt_cookies(response)
    return response



