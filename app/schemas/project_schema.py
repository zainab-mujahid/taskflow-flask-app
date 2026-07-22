from marshmallow import fields, validate

from app.schemas.base import BaseSchema
from app.utils.helpers import PROJECT_ICONS


class ProjectSchema(BaseSchema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    description = fields.String(required=False, allow_none=True, validate=validate.Length(max=2000))
    color = fields.String(required=True, validate=validate.Regexp(r"^#[0-9a-fA-F]{6}$"))
    icon = fields.String(required=True, validate=validate.OneOf(PROJECT_ICONS))
