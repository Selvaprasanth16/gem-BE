# Sell Your Land - Implementation Summary

## Files Created

### Models
- **`Models/sellLandModel.py`** - SellLandSubmission model for form submissions

### Controllers
- **`Controllers/sellLandUserController.py`** - User-side operations (create, view, update, delete)
- **`Controllers/sellLandAdminController.py`** - Admin-side operations (approve, reject, move to Land, bulk operations)

### Routes
- **`Routes/sellLandUserRoutes.py`** - User endpoints under `/api/user/sell-land`
- **`Routes/sellLandAdminRoutes.py`** - Admin endpoints under `/api/admin/sell-land`

### Documentation
- **`SELL_LAND_API_DOCS.md`** - Complete API documentation with examples

### Updated Files
- **`app.py`** - Registered new blueprints

---

## API Endpoints

### User Endpoints (`/api/user/sell-land`)
1. `POST /create` - Submit form
2. `GET /my-submissions` - View own submissions
3. `GET /submission?id=<id>` - View specific submission
4. `PUT /update?id=<id>` - Update pending submission
5. `DELETE /delete?id=<id>` - Delete submission

### Admin Endpoints (`/api/admin/sell-land`)
1. `GET /all` - View all submissions (with filters)
2. `GET /pending` - View pending submissions
3. `GET /submission?id=<id>` - View any submission
4. `POST /approve` - Approve submission
5. `POST /reject` - Reject submission
6. `POST /move-to-land` ⭐ - Move to Land model
7. `PUT /update?id=<id>` - Update any submission
8. `DELETE /delete?id=<id>` - Delete any submission
9. `GET /dashboard-stats` - Get statistics
10. `POST /bulk-approve` - Approve multiple
11. `POST /bulk-delete` - Delete multiple

---

## Key Features

### ✅ Authentication
- Uses existing `CheckAuthorization.VerifyToken()` for all protected routes
- Consistent with existing `/api/user` and `/api/admin` patterns

### ✅ Form Field Mapping
Frontend → Backend:
- `name` → `owner_name`
- `phone` → `contact_phone`
- `location` → `location`
- `price` → `price`
- `area` → `area`
- `landType` → `land_type`

### ✅ Status Workflow
```
pending → approved/rejected → moved_to_land
```

### ✅ Admin Move to Land Feature
Admins can move approved submissions to the main Land model with automatic mapping:
- **Coconut Land** → farm property with agricultural features
- **Empty Land** → land property
- **Commercial Land** → commercial property
- **House** → residential property

### ✅ Data Validation
- Phone: minimum 10 digits
- Price: must be positive
- Area: must be positive
- Land Type: must be one of 4 valid types

---

## Frontend Integration

### Submit Form Example
```javascript
const response = await fetch('/api/user/sell-land/create', {
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
    landType: selectedLandType,
    description: formData.description
  })
});
```

---

## Database Collections

### `sell_land_submissions`
Stores all form submissions with:
- User reference
- Form data (owner_name, contact_phone, location, price, area, land_type)
- Status tracking (pending, approved, rejected, moved_to_land)
- Timestamps (created, updated, approved, rejected)
- Reference to Land model if moved

### Indexes
- `user`
- `status`
- `land_type`
- `-created_at` (descending)

---

## Testing the API

### 1. Start the server
```bash
cd gem-BE
.\venv\Scripts\Activate.ps1
python app.py
```

### 2. Test user submission (requires user token)
```bash
curl -X POST http://localhost:5000/api/user/sell-land/create \
  -H "Content-Type: application/json" \
  -H "token: YOUR_USER_TOKEN" \
  -d '{
    "name": "John Doe",
    "phone": "9876543210",
    "location": "Chennai, Tamil Nadu",
    "price": 5000000,
    "area": 2400,
    "landType": "Coconut Land"
  }'
```

### 3. Test admin approval (requires admin token)
```bash
curl -X POST http://localhost:5000/api/admin/sell-land/approve \
  -H "Content-Type: application/json" \
  -H "token: YOUR_ADMIN_TOKEN" \
  -d '{
    "submission_id": "SUBMISSION_ID"
  }'
```

### 4. Test move to Land (requires admin token)
```bash
curl -X POST http://localhost:5000/api/admin/sell-land/move-to-land \
  -H "Content-Type: application/json" \
  -H "token: YOUR_ADMIN_TOKEN" \
  -d '{
    "submission_id": "SUBMISSION_ID",
    "title": "Premium Coconut Farm"
  }'
```

---

## Next Steps

1. **Frontend Integration**
   - Update `SellLandForm.js` to call `/api/user/sell-land/create`
   - Create user dashboard to view submissions
   - Create admin panel to manage submissions

2. **Testing**
   - Test all user endpoints
   - Test all admin endpoints
   - Test move-to-land functionality

3. **Enhancements** (Optional)
   - Add image upload support
   - Add email notifications on approval/rejection
   - Add search and filtering in frontend
   - Add pagination for large datasets

---

## Architecture Benefits

✅ **Separation of Concerns**: Separate model for form submissions vs final Land listings
✅ **Admin Control**: Admins can review before adding to main Land database
✅ **Data Integrity**: Original submission data preserved even after moving
✅ **Consistent Auth**: Uses existing CheckAuthorization utility
✅ **RESTful Design**: Clear, predictable endpoint structure
✅ **Scalable**: Easy to add more features (notifications, analytics, etc.)
