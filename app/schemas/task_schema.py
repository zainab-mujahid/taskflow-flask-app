from marshmallow import fields, validate, pre_load

from app.schemas.base import BaseSchema

STATUS_CHOICES = ["TODO", "IN_PROGRESS", "COMPLETED"]
PRIORITY_CHOICES = ["LOW", "MEDIUM", "HIGH"]

OPTIONAL_FIELDS = ["project_id", "start_date", "due_date", "description"]


class TaskSchema(BaseSchema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    description = fields.String(required=False, allow_none=True, validate=validate.Length(max=4000))
    project_id = fields.Integer(required=False, allow_none=True)
    priority = fields.String(required=True, validate=validate.OneOf(PRIORITY_CHOICES))
    status = fields.String(required=True, validate=validate.OneOf(STATUS_CHOICES))
    start_date = fields.Date(required=False, allow_none=True)
    due_date = fields.DateTime(required=False, allow_none=True, format="%Y-%m-%dT%H:%M")

    @pre_load
    def blank_strings_to_none(self, data, **kwargs):
        cleaned = data.to_dict() if hasattr(data, "to_dict") else dict(data)
        for field in OPTIONAL_FIELDS:
            if field in cleaned and cleaned[field] == "":
                cleaned[field] = None
        return cleaned


class TagSchema(BaseSchema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=50))
    color = fields.String(required=True, validate=validate.Regexp(r"^#[0-9a-fA-F]{6}$"))
