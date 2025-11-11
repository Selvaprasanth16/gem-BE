# Enquiry Management API Documentation

## Overview
This API manages buy/interest enquiries for land listings. When users show interest in purchasing land, their enquiries are automatically recorded and displayed in the admin portal for tracking and management.

## Authentication
All endpoints require a `token` header for authentication using the `CheckAuthorization` utility.

```
Headers:
  token: <JWT_TOKEN>
```

---

## Enquiry Types

- **buy_interest** - User interested in buying the land
- **site_visit** - User wants to schedule a site visit
- **price_negotiation** - User wants to negotiate the price
- **general_enquiry** - General questions about the land

---

## User Endpoints

### 1. Create Enquiry
**POST** `/api/user/enquiries/create`

Create a new enquiry for a land listing.

**Headers:**
```
token: <JWT_TOKEN>
```

**Request Body:**
```json
{
  "land_id": "507f1f77bcf86cd799439011",
  "enquiry_type": "buy_interest",
  "contact_name": "John Doe",
  "contact_phone": "9876543210",
  "contact_email": "john@example.com",
  "message": "I'm interested in purchasing this land",
  "budget": 5000000,
  "preferred_contact_time": "Weekdays 10 AM - 5 PM"
}
```

**Response (201):**
```json
{
  "message": "Enquiry submitted successfully",
  "enquiry": {
    "id": "507f1f77bcf86cd799439012",
    "user": {
      "id": "507f191e810c19729de860ea",
      "username": "johndoe",
      "full_name": "John Doe",
      "email": "john@example.com"
    },
    "land": {
      "id": "507f1f77bcf86cd799439011",
      "title": "Premium Coconut Farm",
      "location": "Chennai, Tamil Nadu",
      "price": 5000000,
      "size": 2400,
      "property_type": "farm",
      "status": "available"
    },
    "enquiry_type": "buy_interest",
    "contact_name": "John Doe",
    "contact_phone": "9876543210",
    "contact_email": "john@example.com",
    "message": "I'm interested in purchasing this land",
    "budget": 5000000,
    "preferred_contact_time": "Weekdays 10 AM - 5 PM",
    "status": "pending",
    "is_followed_up": false,
    "created_at": "2025-11-05T16:00:00Z",
    "updated_at": "2025-11-05T16:00:00Z"
  }
}
```

---

### 2. Get My Enquiries
**GET** `/api/user/enquiries/my-enquiries`

Get all enquiries created by the authenticated user.

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
    "contacted": [...],
    "in_progress": [...],
    "completed": [...],
    "cancelled": [...]
  },
  "all_enquiries": [...]
}
```

---

### 3. Get Enquiry by ID
**GET** `/api/user/enquiries/enquiry?id=<enquiry_id>`

Get a specific enquiry (user can only view their own).

**Headers:**
```
token: <JWT_TOKEN>
```

**Query Parameters:**
- `id` (required): Enquiry ID

---

### 4. Update Enquiry
**PUT** `/api/user/enquiries/update?id=<enquiry_id>`

Update user's own pending enquiry.

**Headers:**
```
token: <JWT_TOKEN>
```

**Query Parameters:**
- `id` (required): Enquiry ID

**Request Body:**
```json
{
  "contact_name": "John Doe Updated",
  "contact_phone": "9876543211",
  "contact_email": "john.updated@example.com",
  "message": "Updated message",
  "budget": 5500000,
  "preferred_contact_time": "Anytime"
}
```

---

### 5. Cancel Enquiry
**PUT** `/api/user/enquiries/cancel?id=<enquiry_id>`

Cancel user's own enquiry.

**Headers:**
```
token: <JWT_TOKEN>
```

**Query Parameters:**
- `id` (required): Enquiry ID

---

### 6. Get Available Lands
**GET** `/api/user/enquiries/available-lands`

Get all available lands for browsing.

**Query Parameters (all optional):**
- `property_type`: Filter by property type
- `location`: Filter by location (partial match)
- `min_price`: Minimum price
- `max_price`: Maximum price
- `min_size`: Minimum size
- `max_size`: Maximum size

**Response (200):**
```json
{
  "total": 50,
  "lands": [...]
}
```

---

## Admin Endpoints

### 1. Get All Enquiries
**GET** `/api/admin/enquiries/all`

Get all enquiries with optional filters.

**Headers:**
```
token: <ADMIN_JWT_TOKEN>
```

**Query Parameters (all optional):**
- `status`: Filter by status
- `enquiry_type`: Filter by enquiry type
- `user_id`: Filter by user ID
- `land_id`: Filter by land ID
- `start_date`: Filter by start date (ISO format)
- `end_date`: Filter by end date (ISO format)
- `is_followed_up`: Filter by follow-up status (true/false)

**Response (200):**
```json
{
  "total": 100,
  "grouped": {
    "pending": [...],
    "contacted": [...],
    "in_progress": [...],
    "completed": [...],
    "cancelled": [...]
  },
  "all_enquiries": [...]
}
```

---

### 2. Get Pending Enquiries
**GET** `/api/admin/enquiries/pending`

Get all pending enquiries awaiting action.

**Headers:**
```
token: <ADMIN_JWT_TOKEN>
```

---

### 3. Update Enquiry Status
**PUT** `/api/admin/enquiries/update-status`

Update enquiry status.

**Headers:**
```
token: <ADMIN_JWT_TOKEN>
```

**Request Body:**
```json
{
  "enquiry_id": "507f1f77bcf86cd799439012",
  "status": "contacted"
}
```

**Valid Statuses:**
- `pending`
- `contacted`
- `in_progress`
- `completed`
- `cancelled`

---

### 4. Add Admin Notes
**PUT** `/api/admin/enquiries/add-notes`

Add or update admin notes for an enquiry.

**Headers:**
```
token: <ADMIN_JWT_TOKEN>
```

**Request Body:**
```json
{
  "enquiry_id": "507f1f77bcf86cd799439012",
  "admin_notes": "Called the customer. Scheduled site visit for next week."
}
```

---

### 5. Mark as Followed Up
**PUT** `/api/admin/enquiries/mark-followed-up`

Mark enquiry as followed up.

**Headers:**
```
token: <ADMIN_JWT_TOKEN>
```

**Request Body:**
```json
{
  "enquiry_id": "507f1f77bcf86cd799439012",
  "follow_up_date": "2025-11-10T10:00:00Z"
}
```

---

### 6. Get Dashboard Stats
**GET** `/api/admin/enquiries/dashboard-stats`

Get comprehensive dashboard statistics.

**Headers:**
```
token: <ADMIN_JWT_TOKEN>
```

**Response (200):**
```json
{
  "overview": {
    "total_enquiries": 100,
    "pending_enquiries": 20,
    "contacted_enquiries": 30,
    "in_progress_enquiries": 25,
    "completed_enquiries": 20,
    "cancelled_enquiries": 5
  },
  "by_enquiry_type": {
    "buy_interest": 60,
    "site_visit": 20,
    "price_negotiation": 15,
    "general_enquiry": 5
  },
  "follow_up_stats": {
    "followed_up": 70,
    "not_followed_up": 30
  },
  "recent_enquiries": [...],
  "pending_enquiries": [...],
  "most_enquired_lands": [
    {"land_id": "...", "count": 10},
    ...
  ]
}
```

---

### 7. Bulk Update Status
**POST** `/api/admin/enquiries/bulk-update-status`

Update status of multiple enquiries at once.

**Headers:**
```
token: <ADMIN_JWT_TOKEN>
```

**Request Body:**
```json
{
  "enquiry_ids": [
    "507f1f77bcf86cd799439012",
    "507f1f77bcf86cd799439013"
  ],
  "status": "contacted"
}
```

---

## Status Flow

```
User creates enquiry
       ↓
   [pending]
       ↓
Admin reviews
       ↓
   [contacted] → [in_progress] → [completed]
                                      ↓
                                  [cancelled]
```

---

## Model Schema

### Enquiry
```python
{
  "id": ObjectId,
  "user": Reference(Admin_And_User),
  "land": Reference(Land),
  "enquiry_type": String (choices: ['buy_interest', 'site_visit', 'price_negotiation', 'general_enquiry']),
  "contact_name": String (required, max 200),
  "contact_phone": String (required, max 20),
  "contact_email": String (required, max 100),
  "message": String (max 1000),
  "budget": Integer (min 0),
  "preferred_contact_time": String (max 100),
  "status": String (choices: ['pending', 'contacted', 'in_progress', 'completed', 'cancelled'], default: 'pending'),
  "admin_notes": String (max 2000),
  "is_followed_up": Boolean (default: false),
  "follow_up_date": DateTime,
  "created_at": DateTime,
  "updated_at": DateTime,
  "contacted_at": DateTime,
  "completed_at": DateTime
}
```

---

## Integration Example

### User Shows Interest in Land

```javascript
// 1. User browses available lands
const lands = await fetch('/api/user/enquiries/available-lands');

// 2. User clicks "I'm Interested" on a land
const enquiry = {
  land_id: selectedLand.id,
  enquiry_type: 'buy_interest',
  contact_name: currentUser.full_name,
  contact_phone: '9876543210',
  contact_email: currentUser.email,
  message: 'I would like to know more about this property',
  budget: 5000000
};

// 3. Submit enquiry
const response = await fetch('/api/user/enquiries/create', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'token': localStorage.getItem('token')
  },
  body: JSON.stringify(enquiry)
});

// 4. Enquiry automatically appears in admin portal
```

---

## Admin Workflow

1. **View Pending Enquiries** - `/api/admin/enquiries/pending`
2. **Contact Customer** - Update status to 'contacted'
3. **Add Notes** - Record conversation details
4. **Track Progress** - Update to 'in_progress'
5. **Mark Follow-up** - Set follow-up date
6. **Complete** - Mark as 'completed' when deal is done

---

## Notes

1. **Authentication**: All endpoints use `CheckAuthorization.VerifyToken()` for token validation
2. **Auto-Recording**: Enquiries are automatically created when users show interest
3. **Admin Visibility**: All enquiries immediately visible in admin portal
4. **Status Tracking**: Comprehensive status tracking from pending to completion
5. **Follow-up Management**: Built-in follow-up tracking system
6. **Land Validation**: Only available lands can receive enquiries
