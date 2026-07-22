from datetime import datetime, timedelta, timezone

from flask import render_template, request, redirect, url_for, flash, g
from marshmallow import ValidationError
from sqlalchemy import or_, case

from app.blueprints.tasks import tasks_bp
from app.extensions import db
from app.models import Task, Project, Tag, TaskStatus, TaskPriority
from app.schemas.task_schema import TaskSchema
from app.utils.decorators import web_login_required
from app.utils.helpers import paginate_query

STATUS_VALUES = ["TODO", "IN_PROGRESS", "COMPLETED"]
PRIORITY_VALUES = ["LOW", "MEDIUM", "HIGH"]


@tasks_bp.before_request
@web_login_required
def _require_login():
    pass


def _user_projects():
    return Project.query.filter_by(user_id=g.current_user.id, is_archived=False).order_by(Project.name).all()


def _user_tags():
    return Tag.query.filter_by(user_id=g.current_user.id).order_by(Tag.name).all()


def _apply_filters(query, args):
    search = (args.get("search") or "").strip()
    if search:
        like = f"%{search}%"
        query = query.filter(or_(Task.title.ilike(like), Task.description.ilike(like)))

    project_id = args.get("project")
    if project_id and project_id.isdigit():
        query = query.filter(Task.project_id == int(project_id))

    priority = args.get("priority")
    if priority in PRIORITY_VALUES:
        query = query.filter(Task.priority == TaskPriority[priority])

    status = args.get("status")
    if status in STATUS_VALUES:
        query = query.filter(Task.status == TaskStatus[status])

    tag_id = args.get("tag")
    if tag_id and tag_id.isdigit():
        query = query.filter(Task.tags.any(Tag.id == int(tag_id)))

    due = args.get("due")
    now = datetime.now(timezone.utc)
    if due == "today":
        start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
        query = query.filter(Task.due_date >= start, Task.due_date < start + timedelta(days=1))
    elif due == "week":
        query = query.filter(Task.due_date >= now, Task.due_date <= now + timedelta(days=7))
    elif due == "overdue":
        query = query.filter(Task.due_date < now, Task.is_completed.is_(False))
    elif due == "no_date":
        query = query.filter(Task.due_date.is_(None))

    return query


def _apply_sort(query, sort):
    if sort == "oldest":
        return query.order_by(Task.created_at.asc())
    if sort == "due_date":
        return query.order_by(Task.due_date.is_(None), Task.due_date.asc())
    if sort == "priority":
        order = case((Task.priority == TaskPriority.HIGH, 0), (Task.priority == TaskPriority.MEDIUM, 1), else_=2)
        return query.order_by(order, Task.created_at.desc())
    return query.order_by(Task.created_at.desc())


def _sync_completion(task):
    task.is_completed = task.status == TaskStatus.COMPLETED
    task.completed_at = datetime.now(timezone.utc) if task.is_completed else None


def _selected_tags(user_id):
    tag_ids = [int(t) for t in request.form.getlist("tags") if t.isdigit()]
    if not tag_ids:
        return []
    return Tag.query.filter(Tag.user_id == user_id, Tag.id.in_(tag_ids)).all()


@tasks_bp.route("/")
def index():
    view = request.args.get("view", "kanban")
    args = request.args
    base_query = Task.query.filter_by(user_id=g.current_user.id)
    filtered = _apply_filters(base_query, args)

    context = dict(
        view=view,
        projects=_user_projects(),
        tags=_user_tags(),
        filters=args,
        highlight_id=args.get("highlight", type=int),
    )

    if view == "list":
        sort = args.get("sort", "newest")
        sorted_q = _apply_sort(filtered, sort)
        page = args.get("page", 1, type=int)
        pagination = paginate_query(sorted_q, page, per_page=10)
        context.update(pagination=pagination, tasks=pagination.items)
        return render_template("tasks/index.html", **context)

    columns = {}
    for status in TaskStatus:
        columns[status.value] = (
            filtered.filter(Task.status == status)
            .order_by(Task.position.asc(), Task.created_at.desc())
            .all()
        )
    context.update(columns=columns)
    return render_template("tasks/index.html", **context)


@tasks_bp.route("/create", methods=["GET", "POST"])
def create():
    projects = _user_projects()
    tags = _user_tags()

    if request.method == "GET":
        form_data = {
            "status": request.args.get("status", "TODO"),
            "priority": "MEDIUM",
            "project_id": request.args.get("project", ""),
        }
        return render_template(
            "tasks/form.html", errors={}, form_data=form_data, projects=projects,
            tags=tags, selected_tag_ids=[], mode="create",
        )

    schema = TaskSchema()
    try:
        data = schema.load(request.form)
    except ValidationError as err:
        return render_template(
            "tasks/form.html", errors=err.messages, form_data=request.form, projects=projects,
            tags=tags, selected_tag_ids=[int(t) for t in request.form.getlist("tags") if t.isdigit()],
            mode="create",
        ), 400

    project_id = data.get("project_id")
    if project_id and not Project.query.filter_by(id=project_id, user_id=g.current_user.id).first():
        project_id = None

    task = Task(
        user_id=g.current_user.id,
        title=data["title"].strip(),
        description=data.get("description"),
        project_id=project_id,
        priority=TaskPriority[data["priority"]],
        status=TaskStatus[data["status"]],
        start_date=data.get("start_date"),
        due_date=data.get("due_date"),
    )
    task.tags = _selected_tags(g.current_user.id)
    _sync_completion(task)

    existing_count = Task.query.filter_by(user_id=g.current_user.id, status=task.status).count()
    task.position = existing_count

    db.session.add(task)
    db.session.commit()
    flash(f'Task "{task.title}" created.', "success")
    return redirect(url_for("tasks.index"))


@tasks_bp.route("/<int:task_id>/edit", methods=["GET", "POST"])
def edit(task_id):
    task = Task.query.filter_by(id=task_id, user_id=g.current_user.id).first_or_404()
    projects = _user_projects()
    tags = _user_tags()

    if request.method == "GET":
        form_data = {
            "title": task.title,
            "description": task.description or "",
            "project_id": task.project_id or "",
            "priority": task.priority.value,
            "status": task.status.value,
            "start_date": task.start_date.isoformat() if task.start_date else "",
            "due_date": task.due_date.strftime("%Y-%m-%dT%H:%M") if task.due_date else "",
        }
        return render_template(
            "tasks/form.html", errors={}, form_data=form_data, projects=projects, tags=tags,
            selected_tag_ids=[t.id for t in task.tags], mode="edit", task=task,
        )

    schema = TaskSchema()
    try:
        data = schema.load(request.form)
    except ValidationError as err:
        return render_template(
            "tasks/form.html", errors=err.messages, form_data=request.form, projects=projects,
            tags=tags, selected_tag_ids=[int(t) for t in request.form.getlist("tags") if t.isdigit()],
            mode="edit", task=task,
        ), 400

    project_id = data.get("project_id")
    if project_id and not Project.query.filter_by(id=project_id, user_id=g.current_user.id).first():
        project_id = None

    task.title = data["title"].strip()
    task.description = data.get("description")
    task.project_id = project_id
    task.priority = TaskPriority[data["priority"]]
    task.status = TaskStatus[data["status"]]
    task.start_date = data.get("start_date")
    task.due_date = data.get("due_date")
    task.tags = _selected_tags(g.current_user.id)
    _sync_completion(task)

    db.session.commit()
    flash(f'Task "{task.title}" updated.', "success")
    return redirect(url_for("tasks.index"))


@tasks_bp.route("/<int:task_id>/delete", methods=["POST"])
def delete(task_id):
    task = Task.query.filter_by(id=task_id, user_id=g.current_user.id).first_or_404()
    title = task.title
    db.session.delete(task)
    db.session.commit()
    flash(f'Task "{title}" deleted.', "success")
    return redirect(request.referrer or url_for("tasks.index"))


@tasks_bp.route("/<int:task_id>/duplicate", methods=["POST"])
def duplicate(task_id):
    task = Task.query.filter_by(id=task_id, user_id=g.current_user.id).first_or_404()
    copy = Task(
        user_id=g.current_user.id,
        title=f"{task.title} (copy)",
        description=task.description,
        project_id=task.project_id,
        priority=task.priority,
        status=TaskStatus.TODO,
        start_date=task.start_date,
        due_date=task.due_date,
    )
    copy.tags = list(task.tags)
    existing_count = Task.query.filter_by(user_id=g.current_user.id, status=TaskStatus.TODO).count()
    copy.position = existing_count
    db.session.add(copy)
    db.session.commit()
    flash("Task duplicated.", "success")
    return redirect(request.referrer or url_for("tasks.index"))
