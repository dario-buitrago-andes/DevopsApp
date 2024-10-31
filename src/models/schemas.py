from marshmallow import Schema, fields, validate


class ToBlacklistSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=255, min=1))
    app_uuid = fields.UUID(required=True)
    blocked_reason = fields.Str(required=True)
