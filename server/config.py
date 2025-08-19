import os
from datetime import timedelta


def load_config(app):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sqlite_path = os.path.join(base_dir, "school_store.db")

    app.config.setdefault("SECRET_KEY", os.getenv("SECRET_KEY", "dev-secret"))
    app.config.setdefault("JWT_SECRET_KEY", os.getenv("JWT_SECRET_KEY", "dev-jwt-secret"))

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        db_url = f"sqlite:///{sqlite_path}"
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", db_url)

    app.config.setdefault("SQLALCHEMY_ECHO", False)

    upload_dir = os.getenv("UPLOAD_FOLDER", os.path.join(base_dir, "uploads"))
    app.config.setdefault("UPLOAD_FOLDER", upload_dir)

    app.config.setdefault("JWT_ACCESS_TOKEN_EXPIRES", timedelta(days=7))
    app.config.setdefault("ADMIN_SEED_EMAIL", os.getenv("ADMIN_SEED_EMAIL", "mathias_cheow@students.edu.sg"))
