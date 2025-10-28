# ZigoPay API - Complete Endpoint Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication
All endpoints except `/auth/login/` and `/cargo/track/` require JWT authentication.

---

## 1. AUTHENTICATION ENDPOINTS

### Login
```
POST /api/auth/login/
```
**Request Body:**
```json
{
  "username": "admin@zigopay.com",
  "password": "admin123"
}
```
**Response:**
```json
{
  "success": true,
  "tokens": {
    "access": "eyJ0eXAi...",
    "refresh": "eyJ0eXAi..."
  },
  "user": {
    "user_id": 1,
    "username": "admin@zigopay.com",
    "full_name": "John Admin",
    "role": "admin",
    "organization_id": 1,
    "warehouse_id": null
  }
}
```

### Refresh Token
```
POST /api/auth/refresh/
```
**Request Body:**
```json
{
  "refresh": "refresh_token_here"
}
```

### Logout
```
POST /api/auth/logout/
```
**Request Body:**
```json
{
  "refresh": "refresh_token_here"
}
```

---

## 2. ORGANIZATIONS

### List Organizations
```
GET /api/organizations/
Query Params: ?search=keyword
```
**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "organization_id": 1,
      "name": "ZigoPay Logistics Ltd",
      "address": "123 Main Street",
      "contact_phone": "+255123456789",
      "status": "active"
    }
  ]
}
```

### Create Organization
```
POST /api/organizations/
Request Body:
{
  "name": "ZigoPay Logistics Ltd",
  "address": "123 Main Street",
  "contact_phone": "+255123456789"
}
```

### Get Organization Details
```
GET /api/organizations/{id}/
```

### Update Organization
```
PUT/PATCH /api/organizations/{id}/
```

### Delete Organization
```
DELETE /api/organizations/{id}/
```

---

## 3. USERS

### List Users
```
GET /api/users/
Query Params: 
  ?organization_id=1
  ?warehouse_id=1
  ?role=admin
  ?search=keyword
```
**Response:**
```json
{
  "count": 12,
  "results": [
    {
      "user_id": 1,
      "full_name": "John Admin",
      "username": "admin@zigopay.com",
      "role": "admin",
      "organization_name": "ZigoPay Logistics Ltd",
      "warehouse_name": null
    }
  ]
}
```

### Create User
```
POST /api/users/
Request Body:
{
  "full_name": "John Admin",
  "username": "admin@zigopay.com",
  "email": "admin@zigopay.com",
  "password": "admin123",
  "role": "admin",
  "organization_id": 1
}
```

### Get User Details
```
GET /api/users/{id}/
```

### Update User
```
PUT/PATCH /api/users/{id}/
```

### Delete User
```
DELETE /api/users/{id}/
```

---

## 4. CUSTOMERS

### List Customers
```
GET /api/customers/
Query Params:
  ?organization_id=1
  ?search=keyword
```

### Create Customer
```
POST /api/customers/
Request Body:
{
  "customer_name": "ABC Trading Company",
  "phone_number": "+255712345678",
  "email": "info@abctrading.com",
  "address": "Industrial Area, Dar es Salaam",
  "preferred_communication": "whatsapp",
  "organization_id": 1
}
```

### Get/Update/Delete Customer
```
GET /api/customers/{id}/
PUT/PATCH /api/customers/{id}/
DELETE /api/customers/{id}/
```

---

## 5. WAREHOUSES

### List Warehouses
```
GET /api/warehouses/
Query Params:
  ?organization_id=1
  ?search=keyword
```

### Create Warehouse
```
POST /api/warehouses/
Request Body:
{
  "warehouse_name": "Dar es Salaam Main Warehouse",
  "location": "Port Area, Dar es Salaam",
  "organization_id": 1,
  "capacity": 1000
}
```

### Get/Update/Delete Warehouse
```
GET /api/warehouses/{id}/
PUT/PATCH /api/warehouses/{id}/
DELETE /api/warehouses/{id}/
```

---

## 6. CARGO

### List Cargo
```
GET /api/cargo/
Query Params:
  ?status=pending
  ?warehouse_id=1
  ?customer_id=1
  ?search=tracking_number
```

### Register New Cargo
```
POST /api/cargo/
Request Body:
{
  "customer_id": 1,
  "warehouse_id": 1,
  "cargo_name": "Electronics Shipment",
  "description": "Consumer electronics from China",
  "origin_location": "Shanghai, China",
  "destination_location": "Dar es Salaam, Tanzania",
  "origin_tracking_number": "CN400123",
  "container_id": "CN400123",
  "cargo_weight": 500,
  "cargo_value": 5000,
  "length": 200,
  "width": 150,
  "height": 100
}
```
**Response:**
```json
{
  "success": true,
  "message": "Cargo registered successfully",
  "cargo": {
    "cargo_id": 1,
    "tracking_number": "ZP-2024-001523",
    "status": "pending",
    "cbm": 3.0
  }
}
```

### Get Cargo Details
```
GET /api/cargo/{id}/
```

### Update Cargo Status
```
PATCH /api/cargo/{id}/status/
Request Body:
{
  "status": "in_transit",
  "remarks": "Cargo loaded on vessel"
}
```

### Get Cargo History
```
GET /api/cargo/{id}/history/
```
**Response:**
```json
{
  "success": true,
  "cargo_id": 1,
  "tracking_number": "ZP-2024-001523",
  "history": [
    {
      "previous_status": null,
      "new_status": "pending",
      "remarks": "Cargo registered",
      "updated_at": "2024-01-16T10:00:00Z"
    }
  ]
}
```

### Public Tracking
```
GET /api/cargo/track/{tracking_number}/
```
**No authentication required**

---

## 7. INVOICES

### List Invoices
```
GET /api/invoices/
Query Params:
  ?status=pending
  ?cargo_id=1
```

### Get Invoice Details
```
GET /api/invoices/{id}/
Response:
{
  "success": true,
  "data": {
    "invoice_id": 1,
    "control_number": "ZP-2024-001523-INV",
    "amount": 1500,
    "currency": "USD",
    "due_date": "2024-01-24",
    "status": "pending",
    "cargo_tracking": "ZP-2024-001523",
    "customer_name": "ABC Trading Company"
  }
}
```

### Generate Invoice
```
POST /api/invoices/generate/
Request Body:
{
  "cargo_id": 1,
  "amount": 1500
}
```

---

## 8. PAYMENTS

### List Payments
```
GET /api/payments/
```

### Get Payment Details
```
GET /api/payments/{id}/
```

### Process Payment
```
POST /api/payments/process/
Request Body:
{
  "invoice_id": 1,
  "control_number": "ZP-2024-001523-INV",
  "amount_paid": 1500,
  "payment_method": "mobile_money",
  "payment_reference": "MTN42358912345",
  "transaction_details": {
    "paid_from": {
      "bank_name": "M-Pesa",
      "account_number": "+255712345678"
    }
  }
}
```
**Response:**
```json
{
  "success": true,
  "message": "Payment processed successfully",
  "payment": {
    "payment_id": 1,
    "payment_reference": "MTN42358912345",
    "amount_paid": 1500,
    "status": "completed"
  },
  "release_order": {
    "release_order_id": 1,
    "release_code": "RO-ZP-240118-001",
    "status": "active"
  }
}
```

### Get Release Order by Code
```
GET /api/payments/release-orders/{code}/
```

### Complete Release Order (Mark as Collected)
```
PATCH /api/payments/release-orders/{id}/complete/
```

---

## 9. NOTIFICATIONS

### List Notifications
```
GET /api/notifications/
Query Params:
  ?customer_id=1
  ?cargo_id=1
```

### Send Notification
```
POST /api/notifications/send/
Request Body:
{
  "customer_id": 1,
  "cargo_id": 1,
  "notification_type": "arrival",
  "content": "Your cargo has arrived at the warehouse",
  "delivery_method": "whatsapp"
}
```

---

## COMPLETE WORKFLOW EXAMPLE

### Step 1: Login
```
POST /api/auth/login/
→ Get access token
```

### Step 2: Create Customer
```
POST /api/customers/
```

### Step 3: Register Cargo
```
POST /api/cargo/
→ Generate tracking number
→ Create cargo history
→ Send notification
```

### Step 4: Update Cargo Status to "In Transit"
```
PATCH /api/cargo/{id}/status/
Body: {"status": "in_transit", "remarks": "Loaded"}
```

### Step 5: Update Cargo Status to "Arrived"
```
PATCH /api/cargo/{id}/status/
Body: {"status": "arrived", "remarks": "Arrived at warehouse"}
→ Auto-generates invoice
```

### Step 6: Process Payment
```
POST /api/payments/process/
Body: {invoice_id, control_number, amount_paid, payment_reference}
→ Updates invoice status
→ Generates release order
```

### Step 7: Complete Collection (Mark as Delivered)
```
PATCH /api/payments/release-orders/{id}/complete/
→ Updates cargo status to "delivered"
→ Creates cargo history
```

---

## ERROR RESPONSES

**Authentication Error:**
```json
{
  "success": false,
  "error": "Authentication credentials were not provided."
}
```

**Not Found:**
```json
{
  "success": false,
  "error": "Resource not found"
}
```

**Validation Error:**
```json
{
  "success": false,
  "errors": {
    "field": ["error message"]
  }
}
```

---

## NOTES

- All dates use ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)
- All monetary values use USD as default
- Pagination: Use `?page=1&page_size=20`
- Search: Use `?search=keyword`
- All timestamps are in UTC

