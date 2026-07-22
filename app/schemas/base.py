from marshmallow import Schema, EXCLUDE


class BaseSchema(Schema):
    """Base schema that ignores extra form fields (csrf_token, tags[], etc.)
    instead of raising 'Unknown field' errors."""

    class Meta:
        unknown = EXCLUDE
