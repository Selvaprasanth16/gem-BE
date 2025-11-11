from mongoengine import Document, StringField, IntField, DateTimeField, ReferenceField, BooleanField
from datetime import datetime, timezone
from Models.adminModels import Admin_And_User
from Models.landModels import Land


class Enquiry(Document):
    """
    Model for Buy/Interest Enquiries
    Stores all purchase interest and enquiry details
    """
    # User who made the enquiry (optional for guest enquiries)
    user = ReferenceField(Admin_And_User, required=False)
    
    # Land being enquired about
    land = ReferenceField(Land, required=True)
    
    # Flag to identify guest enquiries
    is_guest = BooleanField(default=False)
    
    # Enquiry details
    enquiry_type = StringField(required=True, choices=['buy_interest', 'site_visit', 'price_negotiation', 'general_enquiry'], default='buy_interest')
    
    # Contact information
    contact_name = StringField(required=False, max_length=200)
    contact_phone = StringField(required=True, max_length=20)
    contact_email = StringField(required=False, max_length=100)
    
    # Enquiry message
    message = StringField(max_length=1000)
    
    # Budget and preferences
    budget = IntField(min_value=0)
    preferred_contact_time = StringField(max_length=100)
    
    # Status tracking
    status = StringField(required=True, choices=['pending', 'contacted', 'in_progress', 'completed', 'cancelled'], default='pending')
    
    # Admin notes
    admin_notes = StringField(max_length=2000)
    
    # Follow-up tracking
    is_followed_up = BooleanField(default=False)
    follow_up_date = DateTimeField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.now(timezone.utc))
    updated_at = DateTimeField(default=datetime.now(timezone.utc))
    contacted_at = DateTimeField()
    completed_at = DateTimeField()
    
    # Metadata
    meta = {
        'collection': 'enquiries',
        'indexes': [
            'user',
            'land',
            'status',
            'enquiry_type',
            '-created_at',
            'is_followed_up'
        ]
    }
    
    def to_json(self):
        """Convert to JSON for API responses"""
        return {
            "id": str(self.id),
            "is_guest": self.is_guest,
            "user": {
                "id": str(self.user.id),
                "username": self.user.username,
                "full_name": self.user.full_name,
                "email": self.user.email
            } if self.user else None,
            "land": {
                "id": str(self.land.id),
                "title": self.land.title,
                "location": self.land.location,
                "price": self.land.price,
                "size": self.land.size,
                "property_type": self.land.property_type,
                "status": self.land.status,
                "address": self.land.address,
                "latitude": self.land.latitude,
                "longitude": self.land.longitude
            } if self.land else None,
            "enquiry_type": self.enquiry_type,
            "contact_name": self.contact_name,
            "contact_phone": self.contact_phone,
            "contact_email": self.contact_email,
            "message": self.message,
            "budget": self.budget,
            "preferred_contact_time": self.preferred_contact_time,
            "status": self.status,
            "admin_notes": self.admin_notes,
            "is_followed_up": self.is_followed_up,
            "follow_up_date": self.follow_up_date.isoformat() if self.follow_up_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "contacted_at": self.contacted_at.isoformat() if self.contacted_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
    
    def clean(self):
        """Custom validation"""
        if self.budget and self.budget < 0:
            raise ValueError("Budget cannot be negative")
