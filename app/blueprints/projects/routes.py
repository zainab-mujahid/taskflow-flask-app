from flask import render_template, request, redirect, url_for, flash, g
from marshmallow import ValidationError

from app.blueprints.projects import projects_bp
from app.extensions import db
from app.models import Project
from app.schemas.project_schema import ProjectSchema
from app.utils.decorators import web_login_required
from app.utils.helpers import PROJECT_ICONS, PROJECT_COLORS


@projects_bp.before_request
@web_login_required
def _require_login():
    pass


@projects_bp.route("/")
def index():
    show_archived = request.args.get("archived") == "1"
    query = Project.query.filter_by(user_id=g.current_user.id, is_archived=show_archived)
    projects = query.order_by(Project.created_at.desc()).all()
    return render_template(
        "projects/index.html", projects=projects, show_archived=show_archived
    )


@projects_bp.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "GET":
        return render_template(
            "projects/form.html",
            errors={},
            form_data={"color": PROJECT_COLORS[0], "icon": PROJECT_ICONS[0]},
            icons=PROJECT_ICONS,
            colors=PROJECT_COLORS,
            mode="create",
        )

    schema = ProjectSchema()
    try:
        data = schema.load(request.form)
    except ValidationError as err:
        return render_template(
            "projects/form.html",
            errors=err.messages,
            form_data=request.form,
            icons=PROJECT_ICONS,
            colors=PROJECT_COLORS,
            mode="create",
        ), 400

    project = Project(user_id=g.current_user.id, **data)
    db.session.add(project)
    db.session.commit()
    flash(f'Project "{project.name}" created.', "success")
    return redirect(url_for("projects.index"))


@projects_bp.route("/<int:project_id>/edit", methods=["GET", "POST"])
def edit(project_id):
    project = Project.query.filter_by(id=project_id, user_id=g.current_user.id).first_or_404()

    if request.method == "GET":
        return render_template(
            "projects/form.html",
            errors={},
            form_data={
                "name": project.name,
                "description": project.description or "",
                "color": project.color,
                "icon": project.icon,
            },
            icons=PROJECT_ICONS,
            colors=PROJECT_COLORS,
            mode="edit",
            project=project,
        )

    schema = ProjectSchema()
    try:
        data = schema.load(request.form)
    except ValidationError as err:
        return render_template(
            "projects/form.html",
            errors=err.messages,
            form_data=request.form,
            icons=PROJECT_ICONS,
            colors=PROJECT_COLORS,
            mode="edit",
            project=project,
        ), 400

    project.name = data["name"]
    project.description = data.get("description")
    project.color = data["color"]
    project.icon = data["icon"]
    db.session.commit()
    flash(f'Project "{project.name}" updated.', "success")
    return redirect(url_for("projects.index"))


@projects_bp.route("/<int:project_id>/delete", methods=["POST"])
def delete(project_id):
    project = Project.query.filter_by(id=project_id, user_id=g.current_user.id).first_or_404()
    name = project.name
    db.session.delete(project)
    db.session.commit()
    flash(f'Project "{name}" deleted.', "success")
    return redirect(url_for("projects.index"))


@projects_bp.route("/<int:project_id>/archive", methods=["POST"])
def archive(project_id):
    project = Project.query.filter_by(id=project_id, user_id=g.current_user.id).first_or_404()
    project.is_archived = not project.is_archived
    db.session.commit()
    flash(
        f'Project "{project.name}" {"archived" if project.is_archived else "restored"}.',
        "success",
    )
    return redirect(request.referrer or url_for("projects.index"))
