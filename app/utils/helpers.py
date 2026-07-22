import os
import uuid

from flask import current_app

PROJECT_ICONS = [
    "folder", "briefcase", "rocket", "target", "book", "code", "heart", "star",
]

PROJECT_COLORS = [
    "#6366f1", "#22c55e", "#f59e0b", "#ef4444",
    "#06b6d4", "#ec4899", "#8b5cf6", "#14b8a6",
]


def allowed_avatar_file(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_AVATAR_EXTENSIONS"]


def save_avatar(file_storage):
    ext = file_storage.filename.rsplit(".", 1)[-1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, filename)
    file_storage.save(file_path)
    return f"/static/uploads/avatars/{filename}"


def delete_avatar(avatar_url):
    if not avatar_url or not avatar_url.startswith("/static/uploads/avatars/"):
        return
    filename = avatar_url.rsplit("/", 1)[-1]
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass


def paginate_query(query, page, per_page=10, max_per_page=100):
    page = max(page, 1)
    per_page = min(max(per_page, 1), max_per_page)
    return query.paginate(page=page, per_page=per_page, error_out=False)
