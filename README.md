# Land Management Backend API

This is a Flask-based backend API for a land management system with user authentication, admin management, and land approval workflows.

## Features

- **User Authentication**: JWT-based authentication with login and registration
- **User Management**: User creation, profile management, and role-based access
- **Land Management**: Land creation, approval workflow, and management
- **Admin Panel**: Dashboard, user management, and land approval system
- **Role-based Access Control**: Admin and user roles with different permissions

## Setup Instructions

### 1. Environment Variables

Copy `env_template.txt` to `.env` and fill in your values:

```bash
cp env_template.txt .env
```

Required environment variables:
- `DB`: Your MongoDB database name
- `DB_CONNECT_STRING`: MongoDB connection string
- `JWT_SECRET`: Secret key for JWT tokens (make it long and secure)
- `JWT_ALGORITHM`: JWT algorithm (default: HS256)
- `JWT_EXPIRATION_MINUTES`: Token expiration time (default: 60)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication (`/api/login`)
- `POST /login` - User login
- `POST /change-password` - Change password

### User Management (`/api/user`)
- `POST /create` - User registration
- `GET /get` - Get user profile
- `PUT /update` - Update user profile
- `DELETE /delete` - Delete user account
- `GET /my-lands` - Get user's lands
- `GET /dashboard` - Get user dashboard stats
- `POST /submit-land` - Submit land for approval
- `PUT /update-land` - Update user's land
- `DELETE /delete-land` - Delete user's land

### Admin Management (`/api/admin`)
- `GET /users` - Get all users
- `GET /dashboard` - Get admin dashboard stats
- `GET /pending-lands` - Get pending lands for approval
- `POST /approve-land` - Approve/reject land
- `PUT /update-user` - Update user (admin only)
- `DELETE /delete-user` - Delete user (admin only)

### Land Management (`/api/land`)
- `POST /create` - Create new land
- `GET /get` - Get lands (with filters)
- `PUT /update` - Update land
- `DELETE /delete` - Delete land

## Authentication

All protected endpoints require a `token` header with a valid JWT token:

```
headers: {
  "token": "your_jwt_token_here"
}
```

## Data Models

### User Model
- `username`: Unique username
- `email`: Unique email address
- `password`: Hashed password
- `role`: User role (admin/user)
- `full_name`: User's full name
- `created_at`: Account creation timestamp

### Land Model
- `user`: Reference to user who created the land
- `title`: Land title
- `location`: Land location
- `size`: Land size
- `price`: Land price
- `status`: Land status (pending/available/sold/rejected)
- `description`: Land description
- `property_type`: Type of property
- `address`: Full address
- `features`: List of land features
- `images_urls`: List of image URLs
- `contact_phone`: Contact phone number
- `contact_email`: Contact email

## Workflow

1. **User Registration**: Users register with username, email, password, and full name
2. **Land Submission**: Users submit land details (status: pending)
3. **Admin Approval**: Admins review and approve/reject lands
4. **Land Management**: Approved lands become available for viewing
5. **User Dashboard**: Users can view their lands and statistics

## Security Features

- JWT-based authentication
- Password hashing with PBKDF2
- Role-based access control
- Input validation and sanitization
- Protected routes with token verification
