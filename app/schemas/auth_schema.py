from marshmallow import fields, validate, validates_schema, ValidationError

from app.schemas.base import BaseSchema


class RegisterSchema(BaseSchema):
    name = fields.String(required=True, validate=validate.Length(min=2, max=120))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8, max=128))
    confirm_password = fields.String(required=True, load_only=True)

    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        if data.get("password") != data.get("confirm_password"):
            raise ValidationError("Passwords do not match.", field_name="confirm_password")


class LoginSchema(BaseSchema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=1))


class ForgotPasswordSchema(BaseSchema):
    email = fields.Email(required=True)


class ResetPasswordSchema(BaseSchema):
    password = fields.String(required=True, validate=validate.Length(min=8, max=128))
    confirm_password = fields.String(required=True)

    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        if data.get("password") != data.get("confirm_password"):
            raise ValidationError("Passwords do not match.", field_name="confirm_password")


class ChangePasswordSchema(BaseSchema):
    current_password = fields.String(required=True)
    new_password = fields.String(required=True, validate=validate.Length(min=8, max=128))
    confirm_password = fields.String(required=True)

    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        if data.get("new_password") != data.get("confirm_password"):
            raise ValidationError("Passwords do not match.", field_name="confirm_password")
