from datetime import datetime, timezone

from flask import render_template, g

from app.blueprints.dashboard import dashboard_bp
from app.models import Task
from app.utils.decorators import web_login_required
from app.utils.stats import get_dashboard_stats


@dashboard_bp.route("/")
@web_login_required
def index():
    user_id = g.current_user.id
    stats = get_dashboard_stats(user_id)

    recent_activity = (
        Task.query.filter_by(user_id=user_id).order_by(Task.updated_at.desc()).limit(6).all()
    )

    now = datetime.now(timezone.utc)
    upcoming_tasks = (
        Task.query.filter(
            Task.user_id == user_id,
            Task.is_completed.is_(False),
            Task.due_date.isnot(None),
            Task.due_date >= now,
        )
        .order_by(Task.due_date.asc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard/index.html",
        stats=stats,
        recent_activity=recent_activity,
        upcoming_tasks=upcoming_tasks,
    )
