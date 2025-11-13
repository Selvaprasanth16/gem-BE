from mongoengine import Document, StringField, IntField, ListField, DictField
from datetime import datetime, timezone

class LandingContent(Document):
    # Single-document settings for landing page
    stats = DictField(default=lambda: {
        "premium_properties": 50,
        "happy_clients": 500,
        "years_experience": 10,
        "client_satisfaction": 98
    })

    features = ListField(DictField(), default=lambda: [
        {"key": "trusted_secure", "text": "Every transaction is protected with the highest security standards. Your investment is safe with us."},
        {"key": "premium_quality", "text": "We carefully curate only the finest properties with pristine natural environments and clear titles."},
        {"key": "expert_guidance", "text": "Our experienced team provides personalized support throughout your land acquisition journey."},
        {"key": "nature_first", "text": "We believe in sustainable development that preserves the natural beauty of the land."}
    ])

    testimonials = ListField(DictField(), default=lambda: [
        {"initials": "SJ", "name": "Sarah Johnson", "title": "Montana Landowner", "text": "Found my perfect mountain retreat through Gem Realstate. The process was seamless and completely professional.", "stars": 5, "avatar_url": ""},
        {"initials": "MC", "name": "Michael Chen", "title": "Colorado Investor", "text": "Exceptional service and truly beautiful properties. Highly recommend for anyone looking for premium land investments.", "stars": 5, "avatar_url": ""},
        {"initials": "ER", "name": "Emily Rodriguez", "title": "Vermont Homesteader", "text": "The team helped me find exactly what I was looking for. Great communication and support throughout the entire process.", "stars": 5, "avatar_url": ""}
    ])

    instagram = DictField(default=lambda: {
        "description": "Join our community of land enthusiasts! Get daily inspiration, property showcases, and exclusive deals. Share your land journey with us!",
        "handle": "gem_realestate_",
        "followers": "10K+",
        "posts": "500+",
        "properties": "50+",
        "url": "https://instagram.com/gem_realestate_"
    })

    images = DictField(default=lambda: {
        "why_image": "/assests/gemlogof.jpg"
    })

    # Up to five urgent sale items; each item may reference a land_id and overrides
    urgent_sales = ListField(DictField(), default=list)  # [{ land_id, title, location, size_text, price, image_url, status }]

    created_at = StringField(default=lambda: datetime.now(timezone.utc).isoformat())
    updated_at = StringField(default=lambda: datetime.now(timezone.utc).isoformat())

    def to_json(self):
        return {
            "id": str(self.id),
            "stats": self.stats or {},
            "features": self.features or [],
            "testimonials": self.testimonials or [],
            "instagram": self.instagram or {},
            "images": self.images or {},
            "urgent_sales": (self.urgent_sales or [])[:5]
        }
