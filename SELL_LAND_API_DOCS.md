# Sell Your Land API Documentation

## Overview
This API manages the "Sell Your Land" form submissions. It provides separate endpoints for users and admins, with admin capabilities to move approved submissions to the main Land model.

## Authentication
All endpoints (except public ones) require a `token` header for authentication using the `CheckAuthorization` utility.

```
Headers:
  token: <JWT_TOKEN>
```

---

## Frontend Form Fields Mapping

### Frontend Form (SellLandForm.js)
```javascript
{
  name: "Owner Name",           // -> owner_name
  phone: "Contact Number",      // -> contact_phone
  location: "Location",         // -> location
  price: "Expected Price (₹)",  // -> price
  area: "Land Size (sqft)",     // -> area
  landType: "Land Type"         // -> land_type
}
```

### Land Types
- **Coconut Land** - Agricultural coconut plantation
- **Empty Land** - Vacant land ready for development
- **Commercial Land** - Business and commercial use
- **House** - Residential property with structure

---

## User Endpoints

### 1. Create Submission
**POST** `/api/user/sell-land/create`

Create a new sell land form submission.

**Headers:**
```
token: <JWT_TOKEN>
```

**Request Body:**
```json
{
  "name": "John Doe",
  "phone": "9876543210",
  "location": "Chennai, Tamil Nadu",
  "price": 5000000,
  "area": 2400,
  "landType": "Coconut Land",
  "description": "Beautiful coconut farm with 100 trees" // Optional
}
```

**Response (201):**
```json
{
  "message": "Land submission created successfully and pending admin approval",
  "submission": {
    "id": "507f1f77bcf86cd799439011",
    "user": {
      "id": "507f191e810c19729de860ea",
      "username": "johndoe",
      "full_name": "John Doe",
      "email": "john@example.com"
    },
    "owner_name": "John Doe",
    "contact_phone": "9876543210",
    "location": "Chennai, Tamil Nadu",
    "price": 5000000,
    "area": 2400,
    "land_type": "Coconut Land",
    "status": "pending",
    "description": "Beautiful coconut farm with 100 trees",
    "created_at": "2025-11-05T15:30:00Z",
    "updated_at": "2025-11-05T15:30:00Z"
  }
}
```

---

### 2. Get My Submissions
**GET** `/api/user/sell-land/my-submissions`

Get all submissions created by the authenticated user.

**Headers:**
```
token: <JWT_TOKEN>
```

**Response (200):**
```json
{
  "total": 5,
  "grouped": {
    "pending": [...],
    "approved": [...],
    "rejected": [...],
    "moved_to_land": [...]
  },
  "all_submissions": [...]
}
```

---

### 3. Get Submission by ID
**GET** `/api/user/sell-land/submission?id=<submission_id>`

Get a specific submission (user can only view their own).

**Headers:**
```
token: <JWT_TOKEN>
```

**Query Parameters:**
- `id` (required): Submission ID

**Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "owner_name": "John Doe",
  ...
}
```

---

### 4. Update Submission
**PUT** `/api/user/sell-land/update?id=<submission_id>`

Update user's own pending submission.

**Headers:**
```
token: <JWT_TOKEN>
```

**Query Parameters:**
- `id` (required): Submission ID

**Request Body:**
```json
{
  "name": "John Doe Updated",
  "phone": "9876543211",
  "location": "Updated Location",
  "price": 5500000,
  "area": 2500,
  "description": "Updated description"
}
```

**Response (200):**
```json
{
  "message": "Submission updated successfully",
  "submission": {...}
}
```

---

### 5. Delete Submission
**DELETE** `/api/user/sell-land/delete?id=<submission_id>`

Delete user's own submission.

**Headers:**
```
token: <JWT_TOKEN>
```

**Query Parameters:**
- `id` (required): Submission ID

**Response (200):**
```json
{
  "message": "Submission deleted successfully"
}
```

---

## Admin Endpoints

### 1. Get All Submissions
**GET** `/api/admin/sell-land/all`

Get all submissions with optional filters.

**Headers:**
```
token: <ADMIN_JWT_TOKEN>
```

**Query Parameters (all optional):**
- `status`: Filter by status (pending, approved, rejected, moved_to_land)
- `land_type`: Filter by land type
- `user_id`: Filter by user ID
- `start_date`: Filter by start date (ISO format)
- `end_date`: Filter by end date (ISO format)

**Response (200):**
```json
{
  "total": 50,
  "grouped": {
    "pending": [...],
    "approved": [...],
    "rejected": [...],
    "moved_to_land": [...]
  },
  "all_submissions": [...]
}
```

---

### 2. Get Pending Submissions
**GET** `/api/admin/sell-land/pending`

Get all pending submissions awaiting approval.

**Headers:**
```
token: <ADMIN_JWT_TOKEN>
```

**Response (200):**
```json
{
  "total": 10,
  "submissions": [...]
}
```

---

### 3. Get Submission by ID
**GET** `/api/admin/sell-land/submission?id=<submission_id>`

Get any submission by ID (admin can view all).

**Headers:**
```
token: <ADMIN_JWT_TOKEN>
```

**Query Parameters:**
- `id` (required): Submission ID

**Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  ...
}
```

---

### 4. Approve Submission
**POST** `/api/admin/sell-land/approve`

Approve a submission (changes status to approved).

**Headers:**
```
token: <ADMIN_JWT_TOKEN>
```

**Request Body:**
```json
{
  "submission_id": "507f1f77bcf86cd799439011"
}
```

**Response (200):**
```json
{
  "message": "Submission approved successfully",
  "submission": {
    "id": "507f1f77bcf86cd799439011",
    "status": "approved",
    "approved_at": "2025-11-05T16:00:00Z",
    ...
  }
}
```

---

### 5. Reject Submission
**POST** `/api/admin/sell-land/reject`

Reject a submission with optional reason.

**Headers:**
```
token: <ADMIN_JWT_TOKEN>
```

**Request Body:**
```json
{
  "submission_id": "507f1f77bcf86cd799439011",
  "reason": "Incomplete information provided"
}
```

**Response (200):**
```json
{
  "message": "Submission rejected",
  "reason": "Incomplete information provided",
  "submission": {
    "id": "507f1f77bcf86cd799439011",
    "status": "rejected",
    "rejection_reason": "Incomplete information provided",
    "rejected_at": "2025-11-05T16:00:00Z",
    ...
  }
}
```

---

### 6. Move to Land Model ⭐
**POST** `/api/admin/sell-land/move-to-land`

Move an approved submission to the main Land model. This creates a new Land entry and marks the submission as moved.

**Headers:**
```
token: <ADMIN_JWT_TOKEN>
```

**Request Body:**
```json
{
  "submission_id": "507f1f77bcf86cd799439011",
  "title": "Premium Coconut Farm in Chennai",  // Optional, auto-generated if not provided
  "description": "Custom description",          // Optional, uses submission description if not provided
  "images_urls": ["url1", "url2"]              // Optional, empty array if not provided
}
```

**Land Type Mapping:**
- **Coconut Land** → `property_type: "farm"`, `features: ["agricultural", "Coconut Farm"]`
- **Empty Land** → `property_type: "land"`, `features: []`
- **Commercial Land** → `property_type: "commercial"`, `features: ["commercial"]`
- **House** → `property_type: "residential"`, `features: ["residential"]`

**Response (201):**
```json
{
  "message": "Submission successfully moved to Land model",
  "submission": {
    "id": "507f1f77bcf86cd799439011",
    "status": "moved_to_land",
    "moved_to_land_id": "507f191e810c19729de860ea",
    ...
  },
  "land": {
    "id": "507f191e810c19729de860ea",
    "title": "Premium Coconut Farm in Chennai",
    "location": "Chennai, Tamil Nadu",
    "size": 2400,
    "price": 5000000,
    "status": "available",
    "property_type": "farm",
    "features": ["agricultural", "Coconut Farm"],
    ...
  }
}
```

---

### 7. Update Submission
**PUT** `/api/admin/sell-land/update?id=<submission_id>`

Update any field of a submission (admin can update any submission).

**Headers:**
```
token: <ADMIN_JWT_TOKEN>
```

**Query Parameters:**
- `id` (required): Submission ID

**Request Body:**
```json
{
  "owner_name": "Updated Name",
  "contact_phone": "9999999999",
  "location": "Updated Location",
  "price": 6000000,
  "area": 3000,
  "land_type": "Commercial Land",
  "status": "approved",
  "description": "Updated description",
  "rejection_reason": "Some reason"
}
```

**Response (200):**
```json
{
  "message": "Submission updated successfully",
  "submission": {...}
}
```

---

### 8. Delete Submission
**DELETE** `/api/admin/sell-land/delete?id=<submission_id>`

Delete any submission (admin can delete any submission).

**Headers:**
```
token: <ADMIN_JWT_TOKEN>
```

**Query Parameters:**
- `id` (required): Submission ID

**Response (200):**
```json
{
  "message": "Submission deleted successfully",
  "deleted_submission": {
    "id": "507f1f77bcf86cd799439011",
    "owner_name": "John Doe",
    "land_type": "Coconut Land"
  }
}
```

---

### 9. Get Dashboard Stats
**GET** `/api/admin/sell-land/dashboard-stats`

Get comprehensive dashboard statistics.

**Headers:**
```
token: <ADMIN_JWT_TOKEN>
```

**Response (200):**
```json
{
  "overview": {
    "total_submissions": 100,
    "pending_submissions": 15,
    "approved_submissions": 50,
    "rejected_submissions": 20,
    "moved_submissions": 15
  },
  "by_land_type": {
    "Coconut Land": 40,
    "Empty Land": 30,
    "Commercial Land": 20,
    "House": 10
  },
  "recent_submissions": [...],
  "pending_approvals": [...]
}
```

---

### 10. Bulk Approve
**POST** `/api/admin/sell-land/bulk-approve`

Approve multiple submissions at once.

**Headers:**
```
token: <ADMIN_JWT_TOKEN>
```

**Request Body:**
```json
{
  "submission_ids": [
    "507f1f77bcf86cd799439011",
    "507f1f77bcf86cd799439012",
    "507f1f77bcf86cd799439013"
  ]
}
```

**Response (200):**
```json
{
  "message": "Bulk approval completed",
  "approved": 3,
  "failed": 0,
  "failed_details": []
}
```

---

### 11. Bulk Delete
**POST** `/api/admin/sell-land/bulk-delete`

Delete multiple submissions at once.

**Headers:**
```
token: <ADMIN_JWT_TOKEN>
```

**Request Body:**
```json
{
  "submission_ids": [
    "507f1f77bcf86cd799439011",
    "507f1f77bcf86cd799439012"
  ]
}
```

**Response (200):**
```json
{
  "message": "Bulk deletion completed",
  "deleted": 2,
  "failed": 0,
  "failed_details": []
}
```

---

## Status Flow

```
User submits form
       ↓
   [pending] ← User can update/delete
       ↓
Admin reviews
       ↓
    ┌──────┴──────┐
    ↓             ↓
[approved]    [rejected]
    ↓
Admin moves to Land
    ↓
[moved_to_land]
```

---

## Error Responses

### 401 Unauthorized
```json
{
  "error": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "error": "Admin access required"
}
```

### 404 Not Found
```json
{
  "error": "Submission not found"
}
```

### 400 Bad Request
```json
{
  "error": "Invalid data: Price cannot be negative"
}
```

---

## Model Schema

### SellLandSubmission
```python
{
  "id": ObjectId,
  "user": Reference(Admin_And_User),
  "owner_name": String (required, max 200),
  "contact_phone": String (required, max 20),
  "location": String (required, max 500),
  "price": Integer (required, min 0),
  "area": Integer (required, min 1),
  "land_type": String (required, choices: ['Coconut Land', 'Empty Land', 'Commercial Land', 'House']),
  "status": String (required, choices: ['pending', 'approved', 'rejected', 'moved_to_land'], default: 'pending'),
  "description": String (max 2000),
  "rejection_reason": String (max 500),
  "moved_to_land_id": String,
  "created_at": DateTime,
  "updated_at": DateTime,
  "approved_at": DateTime,
  "rejected_at": DateTime
}
```

---

## Integration with Frontend

### Example: Submit Form
```javascript
const submitLandForm = async (formData) => {
  try {
    const response = await fetch('http://localhost:5000/api/user/sell-land/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'token': localStorage.getItem('token')
      },
      body: JSON.stringify({
        name: formData.name,
        phone: formData.phone,
        location: formData.location,
        price: formData.price,
        area: formData.area,
        landType: formData.landType,
        description: formData.description
      })
    });
    
    const data = await response.json();
    if (response.ok) {
      console.log('Success:', data);
      // Show success modal
    } else {
      console.error('Error:', data.error);
    }
  } catch (error) {
    console.error('Network error:', error);
  }
};
```

---

## Notes

1. **Authentication**: All endpoints use `CheckAuthorization.VerifyToken()` for token validation
2. **Admin Workflow**: Admins can approve submissions first, then move them to the Land model when ready
3. **Data Preservation**: Original submission data is preserved even after moving to Land model
4. **Validation**: Phone numbers must be at least 10 digits, prices and areas must be positive
5. **Timestamps**: All submissions track creation, update, approval, and rejection times
