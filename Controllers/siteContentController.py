from flask import request, jsonify
from Models.siteContentModels import LandingContent
from Models.landModels import Land
from datetime import datetime, timezone
import jwt
import os

class SiteContentController:
    @staticmethod
    def _get_singleton():
        doc = LandingContent.objects().first()
        if not doc:
            doc = LandingContent()
            doc.save()
        return doc

    @staticmethod
    def _verify_admin():
        token = request.headers.get('token')
        if not token:
            return None, (jsonify({"success": False, "error": "Token required"}), 401)
        try:
            payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
            if payload.get('role') != 'admin':
                return None, (jsonify({"success": False, "error": "Admin access required"}), 403)
            return payload, None
        except jwt.ExpiredSignatureError:
            return None, (jsonify({"success": False, "error": "Token expired"}), 401)
        except jwt.InvalidTokenError:
            return None, (jsonify({"success": False, "error": "Invalid token"}), 401)

    @staticmethod
    def get_public_landing():
        try:
            doc = SiteContentController._get_singleton()
            data = doc.to_json()
            urgent_list = data.get('urgent_sales', [])

            # If manual list is empty, fall back to Lands marked as urgent
            if not urgent_list:
                lands = Land.objects(is_urgent=True).order_by('+urgent_priority', '-updated_at')[:5]
                fallback = []
                for land in lands:
                    lj = land.to_json()
                    fallback.append({
                        'land_id': lj.get('id'),
                        'title': lj.get('urgent_title') or lj.get('title'),
                        'description': lj.get('urgent_description') or lj.get('description'),
                        'image_url': lj.get('urgent_image_url') or ((lj.get('images_urls') or [None])[0]),
                        'price': lj.get('price'),
                        'location': lj.get('location'),
                        'size_text': f"{lj.get('size')} {lj.get('size_unit','sqft')}" if lj.get('size') else '',
                        'status': lj.get('status') or 'available'
                    })
                data['urgent_sales'] = fallback

            # resolve urgent sales with land data when land_id is provided (manual list)
            resolved = []
            for item in data.get('urgent_sales', [])[:5]:
                enriched = dict(item)
                land_id = item.get('land_id')
                try:
                    if land_id:
                        land = Land.objects(id=land_id).first()
                        if land:
                            lj = land.to_json()
                            enriched.setdefault('title', lj.get('title'))
                            enriched.setdefault('location', lj.get('location'))
                            enriched.setdefault('size_text', f"{lj.get('size')} {lj.get('size_unit','sqft')}" if lj.get('size') else '')
                            enriched.setdefault('price', lj.get('price'))
                            enriched.setdefault('status', lj.get('status'))
                            # Prefer override image_url else land first image
                            if not enriched.get('image_url'):
                                imgs = lj.get('images_urls') or []
                                enriched['image_url'] = imgs[0] if imgs else ''
                except Exception:
                    pass
                resolved.append(enriched)
            data['urgent_sales'] = resolved
            return jsonify({"success": True, "data": data}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @staticmethod
    def get_admin_landing():
        try:
            _, error = SiteContentController._verify_admin()
            if error:
                return error
            doc = SiteContentController._get_singleton()
            return jsonify({"success": True, "data": doc.to_json()}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @staticmethod
    def update_landing():
        try:
            _, error = SiteContentController._verify_admin()
            if error:
                return error

            payload = request.get_json() or {}
            doc = SiteContentController._get_singleton()

            # Update only allowed fields
            if 'stats' in payload and isinstance(payload['stats'], dict):
                doc.stats.update(payload['stats'])
            if 'features' in payload and isinstance(payload['features'], list):
                doc.features = payload['features']
            if 'testimonials' in payload and isinstance(payload['testimonials'], list):
                doc.testimonials = payload['testimonials']
            if 'instagram' in payload and isinstance(payload['instagram'], dict):
                doc.instagram.update(payload['instagram'])
            if 'images' in payload and isinstance(payload['images'], dict):
                doc.images.update(payload['images'])
            if 'urgent_sales' in payload and isinstance(payload['urgent_sales'], list):
                # keep max 5 entries
                doc.urgent_sales = payload['urgent_sales'][:5]

            doc.updated_at = datetime.now(timezone.utc).isoformat()
            doc.save()

            return jsonify({"success": True, "message": "Landing content updated", "data": doc.to_json()}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
