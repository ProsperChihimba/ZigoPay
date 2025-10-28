# ZigoPay Cargo Delivery & Payment System

A comprehensive cargo delivery and payment collection system built with Django REST Framework.

## Project Structure

```
zigopay/
├── apps/
│   ├── core/              # Core utilities
│   ├── authentication/    # JWT Authentication
│   ├── organizations/     # Organization management
│   ├── users/             # User management
│   ├── customers/         # Customer management
│   ├── warehouses/        # Warehouse management
│   ├── cargo/             # Cargo tracking
│   ├── invoices/          # Invoice management
│   ├── payments/          # Payment processing
│   └── notifications/     # Notification system
├── zigopay/
│   ├── settings.py        # Django settings
│   └── urls.py           # Main URL configuration
└── manage.py
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Seed Data
```bash
python manage.py seed_data
```

### 4. Run Development Server
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Refresh JWT token
- `POST /api/auth/logout/` - User logout

### Organizations
- `GET /api/organizations/` - List all organizations
- `POST /api/organizations/` - Create organization
- `GET /api/organizations/{id}/` - Get organization details
- `PUT/PATCH /api/organizations/{id}/` - Update organization
- `DELETE /api/organizations/{id}/` - Delete organization

### Users
- `GET /api/users/` - List all users
- `POST /api/users/` - Create user
- `GET /api/users/{id}/` - Get user details
- `PUT/PATCH /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Delete user

### Customers
- `GET /api/customers/` - List all customers
- `POST /api/customers/` - Create customer
- `GET /api/customers/{id}/` - Get customer details
- `PUT/PATCH /api/customers/{id}/` - Update customer
- `DELETE /api/customers/{id}/` - Delete customer

### Warehouses
- `GET /api/warehouses/` - List all warehouses
- `POST /api/warehouses/` - Create warehouse
- `GET /api/warehouses/{id}/` - Get warehouse details
- `PUT/PATCH /api/warehouses/{id}/` - Update warehouse
- `DELETE /api/warehouses/{id}/` - Delete warehouse

### Cargo
- `GET /api/cargo/` - List all cargo
- `POST /api/cargo/` - Register new cargo
- `GET /api/cargo/{id}/` - Get cargo details
- `PATCH /api/cargo/{id}/status/` - Update cargo status
- `GET /api/cargo/{id}/history/` - Get cargo history
- `GET /api/cargo/track/{tracking_number}/` - Public tracking

### Invoices
- `GET /api/invoices/` - List all invoices
- `GET /api/invoices/{id}/` - Get invoice details
- `POST /api/invoices/generate/` - Generate invoice

### Payments
- `GET /api/payments/` - List all payments
- `GET /api/payments/{id}/` - Get payment details
- `POST /api/payments/process/` - Process payment
- `GET /api/payments/release-orders/{code}/` - Get release order
- `PATCH /api/payments/release-orders/{id}/complete/` - Complete release order

### Notifications
- `GET /api/notifications/` - List all notifications
- `POST /api/notifications/send/` - Send notification

## Test Users

After running `python manage.py seed_data`, you'll have:

1. **Admin User**
   - Username: `admin@zigopay.com`
   - Password: `admin123`
   - Role: Admin (full access)

2. **Warehouse Manager**
   - Username: `manager@zigopay.com`
   - Password: `manager123`
   - Role: Warehouse Manager

3. **Officer**
   - Username: `officer@zigopay.com`
   - Password: `officer123`
   - Role: Officer

## Getting Started

### 1. Login to get JWT token

```bash
POST /api/auth/login/
{
  "username": "admin@zigopay.com",
  "password": "admin123"
}

Response:
{
  "success": true,
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "user": {
    "user_id": 1,
    "username": "admin@zigopay.com",
    "full_name": "John Admin",
    "role": "admin",
    "organization_id": 1
  }
}
```

### 2. Use the access token in all subsequent requests

```bash
GET /api/cargo/
Authorization: Bearer {access_token}
```

## Features

- ✅ Multi-organization support
- ✅ Role-based authentication (Admin, Warehouse Manager, Officer, Accountant)
- ✅ Cargo tracking with status updates
- ✅ Invoice generation with unique control numbers
- ✅ Payment processing with transaction tracking
- ✅ Release order generation after payment
- ✅ Cargo history tracking
- ✅ Storage fee calculation
- ✅ Notification system (SMS, WhatsApp, Email - dummy implementation)
- ✅ Public tracking endpoint

## API Documentation

The API uses standard REST conventions with JSON responses. All endpoints (except authentication and public tracking) require JWT authentication.

### Common Response Format

**Success:**
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

**Error:**
```json
{
  "success": false,
  "error": "Error message",
  "errors": { "field": ["error details"] }
}
```

### Pagination

List endpoints support pagination:
- `?page=1` - Page number
- `?page_size=20` - Items per page
- `?search=keyword` - Search functionality

## Development

### Running Tests
```bash
python manage.py test
```

### Database Reset
```bash
python manage.py flush
python manage.py migrate
python manage.py seed_data
```

## Production Deployment

1. Set `DEBUG = False` in settings.py
2. Configure proper database (PostgreSQL recommended)
3. Set up Celery for background tasks
4. Configure email/SMS/WhatsApp providers
5. Use environment variables for sensitive data
6. Set up HTTPS with SSL certificates

## Notes

- Currently using SQLite for development
- Notification system uses dummy implementations (integrate with actual SMS/WhatsApp/Email APIs in production)
- Payment processing is simplified (integrate with actual payment gateways in production)
- Storage fees are calculated daily (customize as needed)

