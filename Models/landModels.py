from mongoengine import Document, StringField, IntField, ListField, DateTimeField, ReferenceField
from datetime import datetime, timezone
from Models.adminModels import Admin_And_User


class Land(Document):
    # User who created this land
    user = ReferenceField(Admin_And_User, required=True)
    
    title = StringField(required=True, max_length=200)
    location = StringField(required=True, max_length=500)
    size = IntField(required=True, min_value=1) 
    price = IntField(required=True, min_value=0)
    status = StringField(required=True, choices=['pending', 'available', 'sold', 'rejected'], default='pending')
    description = StringField(required=True, max_length=2000)
    images_urls = ListField(StringField(), default=list)
    features = ListField(StringField(choices=['residential', 'commercial', 'agricultural', 'Coconut Farm']), default=list)
    
    # Timestamps
    created_at = DateTimeField(default=datetime.now(timezone.utc))
    updated_at = DateTimeField(default=datetime.now(timezone.utc))
    
    # Additional fields for better land management
    property_type = StringField(required=True, choices=['land', 'farm', 'commercial', 'residential'])
    address = StringField(required=True, max_length=1000)
    contact_phone = StringField(max_length=20)
    contact_email = StringField(max_length=100)

    def to_json(self):
        return {
            "id": str(self.id),
            "user": {
                "id": str(self.user.id),
                "username": self.user.username,
                "full_name": self.user.full_name
            } if self.user else None,
            "title": self.title,
            "location": self.location,
            "size": self.size,
            "price": self.price,
            "status": self.status,
            "description": self.description,
            "images_urls": self.images_urls,
            "features": self.features,
            "property_type": self.property_type,
            "address": self.address,
            "contact_phone": self.contact_phone,
            "contact_email": self.contact_email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def clean(self):
        """Custom validation"""
        if self.price < 0:
            raise ValueError("Price cannot be negative")
        if self.size <= 0:
            raise ValueError("Size must be positive")

