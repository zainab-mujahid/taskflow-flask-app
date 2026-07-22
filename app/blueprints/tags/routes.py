from flask import render_template, request, redirect, url_for, flash, g
from marshmallow import ValidationError

from app.blueprints.tags import tags_bp
from app.extensions import db
from app.models import Tag
from app.schemas.task_schema import TagSchema
from app.utils.decorators import web_login_required
from app.utils.helpers import PROJECT_COLORS


@tags_bp.before_request
@web_login_required
def _require_login():
    pass


@tags_bp.route("/")
def index():
    tags = Tag.query.filter_by(user_id=g.current_user.id).order_by(Tag.name).all()
    return render_template("tags/index.html", tags=tags, errors={}, form_data={}, colors=PROJECT_COLORS)


@tags_bp.route("/create", methods=["POST"])
def create():
    schema = TagSchema()
    tags = Tag.query.filter_by(user_id=g.current_user.id).order_by(Tag.name).all()
    try:
        data = schema.load(request.form)
    except ValidationError as err:
        return render_template(
            "tags/index.html", tags=tags, errors=err.messages, form_data=request.form, colors=PROJECT_COLORS
        ), 400

    if Tag.query.filter_by(user_id=g.current_user.id, name=data["name"]).first():
        return render_template(
            "tags/index.html", tags=tags,
            errors={"name": ["You already have a tag with this name."]},
            form_data=request.form, colors=PROJECT_COLORS,
        ), 400

    tag = Tag(user_id=g.current_user.id, name=data["name"].strip(), color=data["color"])
    db.session.add(tag)
    db.session.commit()
    flash(f'Tag "{tag.name}" created.', "success")
    return redirect(url_for("tags.index"))


@tags_bp.route("/<int:tag_id>/edit", methods=["POST"])
def edit(tag_id):
    tag = Tag.query.filter_by(id=tag_id, user_id=g.current_user.id).first_or_404()
    schema = TagSchema()
    try:
        data = schema.load(request.form)
    except ValidationError as err:
        flash(next(iter(err.messages.values()))[0], "error")
        return redirect(url_for("tags.index"))

    duplicate = Tag.query.filter(
        Tag.user_id == g.current_user.id, Tag.name == data["name"], Tag.id != tag.id
    ).first()
    if duplicate:
        flash("You already have a tag with this name.", "error")
        return redirect(url_for("tags.index"))

    tag.name = data["name"].strip()
    tag.color = data["color"]
    db.session.commit()
    flash(f'Tag "{tag.name}" updated.', "success")
    return redirect(url_for("tags.index"))


@tags_bp.route("/<int:tag_id>/delete", methods=["POST"])
def delete(tag_id):
    tag = Tag.query.filter_by(id=tag_id, user_id=g.current_user.id).first_or_404()
    name = tag.name
    db.session.delete(tag)
    db.session.commit()
    flash(f'Tag "{name}" deleted.', "success")
    return redirect(url_for("tags.index"))
