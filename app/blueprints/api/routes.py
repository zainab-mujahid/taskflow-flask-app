from datetime import datetime, timezone

from flask import request, jsonify, g

from app.blueprints.api import api_bp
from app.extensions import db
from app.models import Task, TaskStatus
from app.utils.decorators import api_login_required
from app.utils.stats import get_dashboard_stats

VALID_STATUSES = {"TODO", "IN_PROGRESS", "COMPLETED"}


@api_bp.route("/tasks/<int:task_id>/status", methods=["PATCH"])
@api_login_required
def update_status(task_id):
    task = Task.query.filter_by(id=task_id, user_id=g.current_user.id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404

    payload = request.get_json(silent=True) or {}
    status = payload.get("status")
    if status not in VALID_STATUSES:
        return jsonify({"error": "Invalid status"}), 400

    task.status = TaskStatus[status]
    task.is_completed = status == "COMPLETED"
    task.completed_at = datetime.now(timezone.utc) if task.is_completed else None
    if isinstance(payload.get("position"), int):
        task.position = payload["position"]
    db.session.commit()
    return jsonify({"task": task.to_dict()})


@api_bp.route("/tasks/<int:task_id>/complete", methods=["PATCH"])
@api_login_required
def toggle_complete(task_id):
    task = Task.query.filter_by(id=task_id, user_id=g.current_user.id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404

    payload = request.get_json(silent=True) or {}
    is_completed = bool(payload.get("is_completed"))
    task.is_completed = is_completed
    task.status = TaskStatus.COMPLETED if is_completed else TaskStatus.TODO
    task.completed_at = datetime.now(timezone.utc) if is_completed else None
    db.session.commit()
    return jsonify({"task": task.to_dict()})


@api_bp.route("/tasks/reorder", methods=["POST"])
@api_login_required
def reorder():
    payload = request.get_json(silent=True) or {}
    status = payload.get("status")
    ordered_ids = payload.get("ordered_ids") or []
    if status not in VALID_STATUSES:
        return jsonify({"error": "Invalid status"}), 400

    tasks = Task.query.filter(
        Task.id.in_(ordered_ids), Task.user_id == g.current_user.id
    ).all()
    tasks_by_id = {t.id: t for t in tasks}

    for index, task_id in enumerate(ordered_ids):
        task = tasks_by_id.get(task_id)
        if not task:
            continue
        task.status = TaskStatus[status]
        task.position = index
        task.is_completed = status == "COMPLETED"
        task.completed_at = datetime.now(timezone.utc) if task.is_completed else None

    db.session.commit()
    return jsonify({"ok": True})


@api_bp.route("/dashboard/stats", methods=["GET"])
@api_login_required
def dashboard_stats():
    return jsonify(get_dashboard_stats(g.current_user.id))
