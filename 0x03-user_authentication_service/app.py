#!/usr/bin/env python3

"""
Basic flask app
"""

from auth import Auth
from flask import abort, Flask, jsonify, request, redirect

app = Flask(__name__)
AUTH = Auth()


@app.route('/', methods=['GET'], strict_slashes=False)
def index() -> str:
    """
    Root endpoint
    """
    return jsonify({'message': 'Bienvenue'})


@app.route('/users', methods=['POST'], strict_slashes=False)
def users() -> str:
    """
    Creates new user and saves to the database
    """
    email = request.form.get('email')
    password = request.form.get('password')
    if email is None or password is None:
        abort(400)
    try:
        AUTH.register_user(email, password)
        return jsonify({'email': email, 'message': 'user created'})
    except ValueError:
        return jsonify({'message': 'email already registered'}), 400


@app.route('/sessions', methods=['POST'], strict_slashes=False)
def login() -> str:
    """
    Creates a login session for the defined user
    """
    email = request.form.get('email')
    password = request.form.get('password')
    if email is None or password is None:
        abort(400)
    if AUTH.valid_login(email, password):
        session_id = AUTH.create_session(email)
    else:
        abort(401)
    response = jsonify({'email': email, 'message': 'logged in'})
    response.set_cookie('session_id', session_id)
    return response


@app.route('/sessions', methods=['DELETE'], strict_slashes=False)
def logout() -> str:
    """
    DEstroys a login session for the user defined by session_id
    """
    session_id = request.cookies.get('session_id')
    if session_id is None:
        abort(400)
    try:
        user = AUTH.get_user_from_session_id(session_id)
        AUTH.destroy_session(user.id)
    except Exception:
        abort(403)
    return redirect('/'), 302


@app.route('/profile', methods=['GET'], strict_slashes=False)
def profile() -> str:
    """
    Returns profile of user defined by session_id
    """
    session_id = request.cookies.get('session_id')
    if session_id is None:
        abort(403)
    user = AUTH.get_user_from_session_id(session_id)
    if user is None:
        abort(403)
    return jsonify({'email': user.email})


@app.route('/reset_password', methods=['POST'], strict_slashes=False)
def get_reset_password_token() -> str:
    """
    Returns a uniqe token for reseting password
    """
    email = request.form.get('email')
    if email is None:
        abort(403)
    try:
        token = AUTH.get_reset_password_token(email)
        return jsonify({'email': email, 'reset_token': token})
    except ValueError:
        abort(403)


@app.route('/reset_password', methods=['PUT'], strict_slashes=False)
def update_password() -> str:
    """
    Changes user password
    """
    email = request.form.get('email')
    reset_token = request.form.get('reset_token')
    new_password = request.form.get('new_password')
    if email is None or reset_token is None or new_password is None:
        abort(403)
    try:
        AUTH.update_password(reset_token, new_password)
    except Exception:
        abort(403)
    return jsonify({'email': email, 'message': 'Password updated'})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
