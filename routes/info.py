from flask import Blueprint, Response, jsonify

info_api = Blueprint('info_api', __name__)

@info_api.route('/api/v1.0/appinfo', methods=['GET'])
def get_app_info():
    app_info = {
        "version": "0.1.6",
        "valid": [
            "0.1.6"
        ]
    }

    return jsonify(app_info)
