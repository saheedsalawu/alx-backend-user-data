#!/usr/bin/env python3

"""
Module for testing all functionalities
"""

import requests

url = 'http://127.0.0.1:5000/'
EMAIL = "guillaume@holberton.io"
PASSWD = "b4l0u"
NEW_PASSWD = "t4rt1fl3tt3"


def register_user(email: str, password: str) -> None:
    """
    Test for registering a new user
    """
    data = {
            'email': email,
            'password': password
    }
    response = requests.post(url + 'users', data=data)
    assert response.status_code == 200
    assert response.json() == {
        'email': email,
        'message': 'user created'
    }


def log_in_wrong_password(email: str, password: str) -> None:
    """
    Test for user log in with wrong password
    """
    data = {
            'email': email,
            'password': password
    }
    response = requests.post(url + 'sessions', data=data)
    assert response.status_code == 401


def log_in(email: str, password: str) -> None:
    """
    Test for user log in
    """
    data = {
            'email': email,
            'password': password
    }
    response = requests.post(url + 'sessions', data=data)
    assert response.json() == {'email': email, 'message': 'logged in'}
    assert response.status_code == 200
    return response.cookies.get_dict()['session_id']


def profile_unlogged() -> None:
    """
    Checks for route `/profile` when no user is logged in
    """
    response = requests.get(url + 'profile')
    assert response.status_code == 403


def profile_logged(session_id: str) -> None:
    """
    Checks for route `/profile` when no user is logged in
    """
    cookie = {'session_id': session_id}
    response = requests.get(url + 'profile', cookies=cookie)
    assert response.status_code == 200
    assert response.json() == {'email': EMAIL}


def log_out(session_id: str) -> None:
    """
    Test for user log out
    """
    cookie = {'session_id': session_id}
    response = requests.delete(url + 'sessions', cookies=cookie)
    assert response.status_code == 200
    assert response.json() == {'message': 'Bienvenue'}


def reset_password_token(email: str) -> str:
    """
    Returns the reset_password token
    for the user specified by `email`
    """
    response = requests.post(url + 'reset_password', data={'email': email})
    json_res = response.json()
    assert response.status_code == 200
    assert response.json() == {
        "email": email,
        "reset_token": json_res['reset_token']
    }
    return json_res['reset_token']


def update_password(email: str, reset_token: str, password: str) -> None:
    """
    Test for updating user password
    """
    data = {
        'email': email,
        'reset_token': reset_token,
        'new_password': password
    }
    response = requests.put(url + 'reset_password', data)
    assert response.status_code == 200
    assert response.json() == {
        'email': email,
        'message': 'Password updated'
    }


if __name__ == "__main__":

    register_user(EMAIL, PASSWD)
    log_in_wrong_password(EMAIL, NEW_PASSWD)
    profile_unlogged()
    session_id = log_in(EMAIL, PASSWD)
    profile_logged(session_id)
    log_out(session_id)
    reset_token = reset_password_token(EMAIL)
    update_password(EMAIL, reset_token, NEW_PASSWD)
    log_in(EMAIL, NEW_PASSWD)
