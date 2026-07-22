from datetime import datetime, timedelta, timezone

from app.models import Task


def get_notifications(user_id, limit=8):
    now = datetime.now(timezone.utc)
    soon = now + timedelta(hours=24)

    overdue = (
        Task.query.filter(
            Task.user_id == user_id,
            Task.is_completed.is_(False),
            Task.due_date.isnot(None),
            Task.due_date < now,
        )
        .order_by(Task.due_date.asc())
        .limit(limit)
        .all()
    )
    due_soon = (
        Task.query.filter(
            Task.user_id == user_id,
            Task.is_completed.is_(False),
            Task.due_date.isnot(None),
            Task.due_date >= now,
            Task.due_date <= soon,
        )
        .order_by(Task.due_date.asc())
        .limit(limit)
        .all()
    )

    notifications = [{"type": "overdue", "task": t} for t in overdue] + [
        {"type": "due_soon", "task": t} for t in due_soon
    ]
    return notifications[:limit]
