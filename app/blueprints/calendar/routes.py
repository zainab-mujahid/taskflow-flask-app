import calendar as pycalendar
from datetime import datetime, date, timedelta, timezone

from flask import render_template, request, g

from app.blueprints.calendar import calendar_bp
from app.models import Task
from app.utils.decorators import web_login_required


@calendar_bp.before_request
@web_login_required
def _require_login():
    pass


@calendar_bp.route("/")
def index():
    today = date.today()
    year = request.args.get("year", today.year, type=int)
    month = request.args.get("month", today.month, type=int)

    first_of_month = date(year, month, 1)
    prev_month = (first_of_month - timedelta(days=1)).replace(day=1)
    days_in_month = pycalendar.monthrange(year, month)[1]
    next_month = first_of_month + timedelta(days=days_in_month)

    cal = pycalendar.Calendar(firstweekday=6)
    weeks = cal.monthdatescalendar(year, month)

    range_start = weeks[0][0]
    range_end = weeks[-1][-1]

    tasks_in_range = (
        Task.query.filter(
            Task.user_id == g.current_user.id,
            Task.due_date.isnot(None),
            Task.due_date >= datetime(range_start.year, range_start.month, range_start.day, tzinfo=timezone.utc),
            Task.due_date < datetime(range_end.year, range_end.month, range_end.day, tzinfo=timezone.utc) + timedelta(days=1),
        )
        .order_by(Task.due_date.asc())
        .all()
    )

    tasks_by_day = {}
    for task in tasks_in_range:
        day_key = task.due_date.date()
        tasks_by_day.setdefault(day_key, []).append(task)

    now = datetime.now(timezone.utc)
    today_start = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)

    todays_tasks = (
        Task.query.filter(
            Task.user_id == g.current_user.id,
            Task.due_date >= today_start,
            Task.due_date < today_start + timedelta(days=1),
        )
        .order_by(Task.due_date.asc())
        .all()
    )

    upcoming_tasks = (
        Task.query.filter(
            Task.user_id == g.current_user.id,
            Task.is_completed.is_(False),
            Task.due_date >= today_start + timedelta(days=1),
            Task.due_date < today_start + timedelta(days=8),
        )
        .order_by(Task.due_date.asc())
        .all()
    )

    overdue_tasks = (
        Task.query.filter(
            Task.user_id == g.current_user.id,
            Task.is_completed.is_(False),
            Task.due_date.isnot(None),
            Task.due_date < now,
        )
        .order_by(Task.due_date.asc())
        .all()
    )

    return render_template(
        "calendar/index.html",
        weeks=weeks,
        tasks_by_day=tasks_by_day,
        current_month=first_of_month,
        prev_month=prev_month,
        next_month=next_month,
        today=today,
        todays_tasks=todays_tasks,
        upcoming_tasks=upcoming_tasks,
        overdue_tasks=overdue_tasks,
    )
