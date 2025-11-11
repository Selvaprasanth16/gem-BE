from mongoengine import Document, StringField, IntField, DateTimeField, ReferenceField
from datetime import datetime, timezone
from Models.adminModels import Admin_And_User


class SellLandSubmission(Document):
    """
    Model for Sell Your Land form submissions
    Maps directly to frontend form fields: name, phone, location, price, area, landType
    """
    # User who submitted this form
    user = ReferenceField(Admin_And_User, required=True)
    
    # Form fields from frontend
    owner_name = StringField(required=True, max_length=200)  # name from form
    contact_phone = StringField(required=True, max_length=20)  # phone from form
    location = StringField(required=True, max_length=500)  # location from form
    price = IntField(required=True, min_value=0)  # price from form
    area = IntField(required=True, min_value=1)  # area (sqft) from form
    land_type = StringField(required=True, choices=['Coconut Land', 'Empty Land', 'Commercial Land', 'House'])  # landType from form
    
    # Status tracking
    status = StringField(required=True, choices=['pending', 'approved', 'rejected', 'moved_to_land'], default='pending')
    
    # Optional fields
    description = StringField(max_length=2000)
    rejection_reason = StringField(max_length=500)
    
    # If moved to Land model, store the reference
    moved_to_land_id = StringField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.now(timezone.utc))
    updated_at = DateTimeField(default=datetime.now(timezone.utc))
    approved_at = DateTimeField()
    rejected_at = DateTimeField()
    
    # Metadata
    meta = {
        'collection': 'sell_land_submissions',
        'indexes': [
            'user',
            'status',
            'land_type',
            '-created_at'
        ]
    }
    
    def to_json(self):
        """Convert to JSON for API responses"""
        return {
            "id": str(self.id),
            "user": {
                "id": str(self.user.id),
                "username": self.user.username,
                "full_name": self.user.full_name,
                "email": self.user.email
            } if self.user else None,
            "owner_name": self.owner_name,
            "contact_phone": self.contact_phone,
            "location": self.location,
            "price": self.price,
            "area": self.area,
            "land_type": self.land_type,
            "status": self.status,
            "description": self.description,
            "rejection_reason": self.rejection_reason,
            "moved_to_land_id": self.moved_to_land_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "rejected_at": self.rejected_at.isoformat() if self.rejected_at else None
        }
    
    def clean(self):
        """Custom validation"""
        if self.price < 0:
            raise ValueError("Price cannot be negative")
        if self.area <= 0:
            raise ValueError("Area must be positive")
        if len(self.contact_phone) < 10:
            raise ValueError("Contact phone must be at least 10 digits")
