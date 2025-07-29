"""
Marshmallow schemas for data validation and serialization.
Provides input validation for API endpoints and forms.
"""
from marshmallow import Schema, fields, validate, validates_schema, ValidationError

class UserRegistrationSchema(Schema):
    """Schema for user registration validation."""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=20))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    confirm_password = fields.Str(required=True)
    
    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        if data.get('password') != data.get('confirm_password'):
            raise ValidationError('Passwords do not match', 'confirm_password')

class TripSchema(Schema):
    """Schema for trip validation."""
    city = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    region = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    start_date = fields.Date(required=True, format='%Y-%m-%d')
    end_date = fields.Date(required=True, format='%Y-%m-%d')
    activities = fields.List(fields.Str(), load_default=[])
    
    @validates_schema
    def validate_date_range(self, data, **kwargs):
        if 'start_date' in data and 'end_date' in data:
            if data['end_date'] <= data['start_date']:
                raise ValidationError('End date must be after start date', 'end_date')

class ClosetItemSchema(Schema):
    """Schema for closet item validation."""
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    item_type = fields.Str(
        required=True,
        validate=validate.OneOf(['top', 'bottom', 'shoe', 'accessory', 'outerwear', 'dress'])
    )
    price = fields.Str(validate=validate.Length(max=20))
    image_url = fields.Str(validate=validate.Length(max=300))
    source = fields.Str(validate=validate.Length(max=50))

def validate_request_data(schema_class, data):
    """Helper function to validate request data against a schema."""
    schema = schema_class()
    try:
        validated_data = schema.load(data)
        return validated_data, None
    except ValidationError as err:
        return None, err.messages
