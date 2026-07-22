from marshmallow import fields, validate

from app.schemas.base import BaseSchema


class UpdateProfileSchema(BaseSchema):
    name = fields.String(required=True, validate=validate.Length(min=2, max=120))
    email = fields.Email(required=True)
