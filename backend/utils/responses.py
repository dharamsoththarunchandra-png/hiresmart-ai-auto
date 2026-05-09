from flask import jsonify


def success(data=None, message='OK', status_code=200):
    payload = {'status': 'success', 'message': message}
    if data is not None:
        payload['data'] = data
    return jsonify(payload), status_code


def error(message='An error occurred', status_code=400):
    return jsonify({'status': 'error', 'message': message}), status_code
