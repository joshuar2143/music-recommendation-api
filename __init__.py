from flask import Flask, jsonify
from app.routes.api import api


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        DEBUG=False,
        TESTING=False,
        JSON_SORT_KEYS=False,
    )
    if config:
        app.config.from_mapping(config)

    app.register_blueprint(api)

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad Request", "message": str(e.description)}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not Found", "message": str(e.description)}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal Server Error", "message": str(e.description)}), 500

    return app
