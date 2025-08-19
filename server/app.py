import os
from flask import Flask, jsonify, send_from_directory, redirect
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from .config import load_config
from .db import remove_db_session
from .models import seed_admin_if_needed
from .auth import auth_bp
from .products import products_bp
from .orders import orders_bp
from .admin import admin_bp
from .preferences import preferences_bp


def create_app() -> Flask:
    app = Flask(__name__)
    load_config(app)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    CORS(app, supports_credentials=True)
    JWTManager(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(products_bp, url_prefix="/api/products")
    app.register_blueprint(orders_bp, url_prefix="/api/orders")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(preferences_bp, url_prefix="/api/preferences")

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/uploads/<path:filename>")
    def serve_upload(filename: str):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    # Serve static frontend
    web_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web"))

    @app.get("/")
    def root():
        return redirect("/web/index.html", code=302)

    @app.get("/web/<path:filename>")
    def serve_web(filename: str):
        return send_from_directory(web_dir, filename)

    @app.teardown_appcontext
    @app.teardown_request
    def teardown_request(exception=None):  # noqa: ARG001
        remove_db_session()

    with app.app_context():
        seed_admin_if_needed()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
