from datetime import datetime, timedelta, timezone

from app.models import Task, Project, TaskStatus


def get_dashboard_stats(user_id):
    now = datetime.now(timezone.utc)
    base_query = Task.query.filter_by(user_id=user_id)

    total_tasks = base_query.count()
    completed_tasks = base_query.filter(Task.is_completed.is_(True)).count()
    pending_tasks = total_tasks - completed_tasks
    overdue_tasks = base_query.filter(
        Task.is_completed.is_(False),
        Task.due_date.isnot(None),
        Task.due_date < now,
    ).count()
    in_progress_tasks = base_query.filter(Task.status == TaskStatus.IN_PROGRESS).count()

    productivity = round((completed_tasks / total_tasks) * 100) if total_tasks else 0

    week_start = now - timedelta(days=6)
    week_labels = []
    week_counts = []
    for i in range(7):
        day = (week_start + timedelta(days=i)).date()
        day_start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)
        count = base_query.filter(
            Task.is_completed.is_(True),
            Task.completed_at >= day_start,
            Task.completed_at < day_end,
        ).count()
        week_labels.append(day.strftime("%a"))
        week_counts.append(count)

    active_projects = Project.query.filter_by(user_id=user_id, is_archived=False).count()

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "overdue_tasks": overdue_tasks,
        "in_progress_tasks": in_progress_tasks,
        "productivity": productivity,
        "active_projects": active_projects,
        "week_labels": week_labels,
        "week_counts": week_counts,
    }
