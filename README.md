# Nexa E-Commerce API 🛍️

A modern, fully-functional RESTful e-commerce backend built with **Django** and **Django REST Framework**. Nexa provides a scalable, production-ready API with JWT authentication, comprehensive product management, shopping cart functionality, and order processing.

---

## 🌟 Key Features

- ✅ **JWT Authentication** - Secure token-based authentication with refresh tokens
- ✅ **Product Management** - Browse, filter, and manage products with collections
- ✅ **Shopping Cart** - Anonymous-friendly UUID-based shopping carts with item management
- ✅ **Order Management** - Complete order lifecycle with payment status tracking
- ✅ **Product Reviews** - Nested reviews with reply functionality
- ✅ **Customer Profiles** - Customer management with membership tiers (Bronze, Silver, Gold)
- ✅ **Advanced Filtering** - Filter products by collection, price, and inventory
- ✅ **Pagination** - Optimized pagination for large datasets (10 items per page)
- ✅ **Admin Panel** - Django admin interface for complete data management
- ✅ **Role-Based Access Control** - Fine-grained permissions for admin and regular users

---

## 🏗️ Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | Django | 5.2+ |
| **API** | Django REST Framework | Latest |
| **Authentication** | JWT (djangorestframework-simplejwt) | Latest |
| **Database** | MySQL | 8.0+ |
| **User Management** | Djoser | Latest |
| **Social Auth** | social-auth-app-django | Latest |
| **Filtering** | django-filter | Latest |
| **Nested Routes** | drf-nested-routers | Latest |

---

## 📋 Installation & Setup

### Prerequisites
- Python 3.12+
- MySQL 8.0+
- pip or pipenv

### Step 1: Clone & Install Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd Nexa

# Install dependencies using pipenv
pipenv install
pipenv install --dev

# Or using pip
pip install -r requirements.txt
```

### Step 2: Configure Database

Update `nexa/settings.py` with your MySQL credentials:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "nexa",
        "HOST": "localhost",
        "USER": "your_username",
        "PASSWORD": "your_password",
    }
}
```

### Step 3: Run Migrations

```bash
python manage.py migrate
```

### Step 4: Create Superuser

```bash
python manage.py createsuperuser
```

### Step 5: Load Sample Data (Optional)

```bash
python manage.py seed_data
```

### Step 6: Start Development Server

```bash
python manage.py runserver
```

Server runs at `http://localhost:8000`

---

## 🔐 Authentication

Nexa uses **JWT (JSON Web Token)** authentication. All protected endpoints require a valid JWT token in the `Authorization` header.

### Token Lifecycle

1. **Access Token**: Expires after **24 hours**
2. **Refresh Token**: Expires after **7 days**

### Getting Started with Authentication

#### 1. Create a New User

```http
POST /auth/users/
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### 2. Obtain JWT Tokens

```http
POST /auth/jwt/create/
Content-Type: application/json

{
  "username": "john_doe",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### 3. Refresh Access Token

```http
POST /auth/jwt/refresh/
Content-Type: application/json

{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### 4. Use Token in Requests

```http
GET /store/customers/me/
Authorization: JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 📚 API Endpoints

### Authentication Endpoints (Djoser)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|-----------------|
| `POST` | `/auth/users/` | Register a new user | ❌ |
| `GET` | `/auth/users/` | List all users | ✅ Admin |
| `GET` | `/auth/users/{id}/` | Get user details | ✅ Admin |
| `POST` | `/auth/jwt/create/` | Obtain JWT tokens | ❌ |
| `POST` | `/auth/jwt/refresh/` | Refresh access token | ❌ |
| `POST` | `/auth/jwt/verify/` | Verify token validity | ❌ |

---

### Products Endpoints

#### List All Products

```http
GET /store/products/
```

**Query Parameters:**
- `collection_id` - Filter by collection
- `collection__title` - Filter by collection title
- `search` - Search product title
- `min_price` - Minimum price filter
- `max_price` - Maximum price filter
- `page` - Pagination (10 items per page)

**Example:**
```http
GET /store/products/?collection_id=1&min_price=50&max_price=500&page=1
```

**Response:**
```json
{
  "count": 150,
  "next": "http://localhost:8000/store/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Laptop",
      "slug": "laptop",
      "description": "High-performance laptop",
      "price": "999.99",
      "inventory": 25,
      "collection": {
        "id": 1,
        "title": "Electronics",
        "product_count": 45
      },
      "last_update": "2024-11-15T10:30:00Z"
    }
  ]
}
```

#### Retrieve Single Product

```http
GET /store/products/{id}/
```

#### Create Product (Admin Only)

```http
POST /store/products/
Authorization: JWT {token}
Content-Type: application/json

{
  "title": "New Laptop",
  "description": "Latest model with 16GB RAM",
  "price": "1299.99",
  "inventory": 50,
  "collection": 1
}
```

#### Update Product (Admin Only)

```http
PATCH /store/products/{id}/
Authorization: JWT {token}
Content-Type: application/json

{
  "price": "1199.99",
  "inventory": 45
}
```

#### Delete Product (Admin Only)

```http
DELETE /store/products/{id}/
Authorization: JWT {token}
```

**Note:** Products cannot be deleted if associated with order items.

---

### Collections Endpoints

#### List All Collections

```http
GET /store/collections/
```

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "title": "Electronics",
      "product_count": 45,
      "featured_product": {
        "id": 5,
        "title": "Featured Item",
        "slug": "featured-item",
        "price": "299.99"
      }
    }
  ]
}
```

#### Create Collection (Admin Only)

```http
POST /store/collections/
Authorization: JWT {token}
Content-Type: application/json

{
  "title": "New Collection",
  "featured_product": 1
}
```

#### Delete Collection (Admin Only)

```http
DELETE /store/collections/{id}/
Authorization: JWT {token}
```

**Note:** Collections cannot be deleted if they contain products.

---

### Product Reviews Endpoints

#### List Reviews for a Product

```http
GET /store/products/{product_id}/reviews/
```

**Response:**
```json
[
  {
    "id": 1,
    "description": "Excellent product! Highly recommended.",
    "date": "2024-11-15",
    "customer": {
      "id": 1,
      "user": {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com"
      },
      "phone": "+1-555-0123",
      "membership": "G"
    },
    "parent": null,
    "children": [
      {
        "id": 2,
        "description": "Thanks for the review!",
        "date": "2024-11-16",
        "customer": {...}
      }
    ]
  }
]
```

#### Create a Review

```http
POST /store/products/{product_id}/reviews/
Authorization: JWT {token}
Content-Type: application/json

{
  "description": "Great product with fast shipping!"
}
```

#### Reply to a Review (Nested Reply)

```http
POST /store/products/{product_id}/reviews/
Authorization: JWT {token}
Content-Type: application/json

{
  "description": "Thank you for the feedback!",
  "parent": 1
}
```

#### Update a Review

```http
PATCH /store/products/{product_id}/reviews/{review_id}/
Authorization: JWT {token}
Content-Type: application/json

{
  "description": "Updated review content"
}
```

#### Delete a Review

```http
DELETE /store/products/{product_id}/reviews/{review_id}/
Authorization: JWT {token}
```

---

### Shopping Cart Endpoints

#### Create a New Cart

```http
POST /store/carts/
Content-Type: application/json
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "create_at": "2024-11-15T10:30:00Z",
  "items": []
}
```

#### Retrieve Cart

```http
GET /store/carts/{cart_id}/
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "create_at": "2024-11-15T10:30:00Z",
  "items": [
    {
      "id": 1,
      "cart": "550e8400-e29b-41d4-a716-446655440000",
      "product": {
        "id": 1,
        "title": "Laptop",
        "price": "999.99"
      },
      "quantity": 1
    }
  ]
}
```

#### Delete Cart

```http
DELETE /store/carts/{cart_id}/
```

---

### Cart Items Endpoints

#### Add Item to Cart

```http
POST /store/carts/{cart_id}/items/
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 2
}
```

**Response:**
```json
{
  "id": 1,
  "cart": "550e8400-e29b-41d4-a716-446655440000",
  "product": {
    "id": 1,
    "title": "Laptop",
    "price": "999.99"
  },
  "quantity": 2
}
```

#### Update Cart Item Quantity

```http
PATCH /store/carts/{cart_id}/items/{item_id}/
Content-Type: application/json

{
  "quantity": 5
}
```

#### Remove Item from Cart

```http
DELETE /store/carts/{cart_id}/items/{item_id}/
```

#### List Cart Items

```http
GET /store/carts/{cart_id}/items/
```

---

### Orders Endpoints

#### Create an Order

```http
POST /store/orders/
Authorization: JWT {token}
Content-Type: application/json

{
  "cart_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**
```json
{
  "id": 1,
  "placed_at": "2024-11-15T10:30:00Z",
  "payment_status": "P",
  "customer": 1,
  "items": [
    {
      "id": 1,
      "product": {
        "id": 1,
        "title": "Laptop",
        "price": "999.99"
      },
      "quantity": 1,
      "unit_price": "999.99"
    }
  ]
}
```

#### List User's Orders

```http
GET /store/orders/
Authorization: JWT {token}
```

**Response:**
```json
[
  {
    "id": 1,
    "placed_at": "2024-11-15T10:30:00Z",
    "payment_status": "P",
    "customer": 1,
    "items": [...]
  }
]
```

**Note:** Regular users see only their orders; admins see all orders.

#### Retrieve Order Details

```http
GET /store/orders/{order_id}/
Authorization: JWT {token}
```

#### Update Order (Admin Only)

```http
PATCH /store/orders/{order_id}/
Authorization: JWT {token}
Content-Type: application/json

{
  "payment_status": "C"
}
```

**Payment Status Codes:**
- `P` - Pending
- `C` - Complete
- `F` - Failed

#### Delete Order (Admin Only)

```http
DELETE /store/orders/{order_id}/
Authorization: JWT {token}
```

---

### Customers Endpoints

#### Get Current User Profile

```http
GET /store/customers/me/
Authorization: JWT {token}
```

**Response:**
```json
{
  "id": 1,
  "phone": "+1-555-0123",
  "birth_date": "1990-01-15",
  "membership": "G",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### Update Current User Profile

```http
PUT /store/customers/me/
Authorization: JWT {token}
Content-Type: application/json

{
  "phone": "+1-555-0124",
  "birth_date": "1990-01-15",
  "membership": "S",
  "user": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "newemail@example.com"
  }
}
```

#### List All Customers (Admin Only)

```http
GET /store/customers/
Authorization: JWT {token}
```

#### Get Customer Details (Admin Only)

```http
GET /store/customers/{customer_id}/
Authorization: JWT {token}
```

---

## 🔒 Permission Levels

### Anonymous Users (No Auth Required)
- ✅ View products with filtering
- ✅ View collections
- ✅ Create/manage shopping carts
- ✅ Register and obtain JWT tokens

### Authenticated Users
- ✅ All anonymous permissions
- ✅ View/update own customer profile
- ✅ Create reviews
- ✅ Create and manage orders
- ✅ Access order history

### Admin Users
- ✅ All authenticated permissions
- ✅ Create/Update/Delete products
- ✅ Create/Update/Delete collections
- ✅ Manage all customers
- ✅ Update order payment status
- ✅ Delete orders

---

## 🎯 Advanced Features

### Product Filtering

Products can be filtered using multiple criteria:

```http
GET /store/products/?collection_id=1&min_price=100&max_price=1000&search=laptop&page=1
```

**Available Filters:**
- `collection_id` - Filter by collection ID
- `collection__title` - Filter by collection name
- `min_price` - Minimum price (decimal)
- `max_price` - Maximum price (decimal)
- `search` - Search in product title

### Pagination

All list endpoints support pagination with **10 items per page**:

```http
GET /store/products/?page=2
```

**Pagination Response:**
```json
{
  "count": 150,
  "next": "http://localhost:8000/store/products/?page=3",
  "previous": "http://localhost:8000/store/products/?page=1",
  "results": [...]
}
```

### Customer Membership Tiers

- **Bronze (B)** - Default tier for new customers
- **Silver (S)** - Mid-tier with benefits
- **Gold (G)** - Premium tier with exclusive perks

---

## 📊 Database Schema Highlights

### Core Models

- **User** - Custom Django User model with unique email
- **Customer** - Extended user profile with membership tier
- **Product** - Core product with pricing and inventory
- **Collection** - Product categorization with featured product
- **Order** - Order management with payment tracking
- **Cart** - Anonymous-friendly cart using UUID
- **Review** - Nested review system with parent-child replies

### Key Relationships

- User → Customer (One-to-One)
- Product → Collection (Foreign Key)
- Cart → CartItem → Product (Nested Structure)
- Order → OrderItem → Product (Nested Structure)
- Review → Review (Self-referencing for nested replies)

---

## 🚀 Performance Optimizations

- 🔄 **Query Optimization** - `select_related()` and `prefetch_related()` for N+1 prevention
- 📄 **Pagination** - Default 10 items per page to reduce payload
- 🔍 **Django Filters** - Efficient filtering without full table scans
- 💾 **Caching** - Implemented for frequently accessed data
- 🛡️ **SQL Constraints** - Unique constraints for data integrity

---

## 🧪 Testing

Run the test suite:

```bash
python manage.py test
```

Test specific app:

```bash
python manage.py test store
python manage.py test core
python manage.py test likes
python manage.py test tags
```

---

## 🔧 Development Tools

### Django Debug Toolbar

Enabled in development mode for performance monitoring:

```http
GET /__debug__/
```

### Admin Panel

Access at `http://localhost:8000/admin/` with superuser credentials.

---

## 📦 Project Structure

```
Nexa/
├── nexa/                 # Main project config
│   ├── settings.py       # Django settings with DRF config
│   ├── urls.py           # URL routing and API endpoints
│   ├── asgi.py          # ASGI configuration
│   └── wsgi.py          # WSGI configuration
│
├── store/               # E-commerce core app
│   ├── models.py        # Product, Cart, Order, Review models
│   ├── views.py         # DRF ViewSets for all endpoints
│   ├── serializers.py   # Serializers for all models
│   ├── urls.py          # Nested routes configuration
│   ├── filters.py       # Advanced filtering logic
│   ├── pagination.py    # Custom pagination class
│   ├── permissions.py   # Custom permission classes
│   └── signals/         # Django signals for automation
│
├── core/                # User & authentication app
│   ├── models.py        # Custom User model
│   ├── serializers.py   # User serializers
│   └── signals/         # Signal handlers for auto-customer creation
│
├── tags/                # Tags management (extensible)
├── likes/               # Likes/favorites feature (extensible)
│
├── manage.py            # Django management
├── Pipfile              # Dependency management
└── README.md            # This file
```

---

## 🛠️ Configuration

### JWT Settings

Edit `nexa/settings.py`:

```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("JWT",),
}
```

### REST Framework Settings

```python
REST_FRAMEWORK = {
    "COERCE_DECIMAL_TO_STRING": False,
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}
```

---

## 🌐 CORS & Security (For Production)

### Enable CORS

```bash
pip install django-cors-headers
```

Add to `MIDDLEWARE`:
```python
"corsheaders.middleware.CorsMiddleware",
```

Configure in `settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://yourdomain.com",
]
```

### Security Headers

For production, enable:
- HTTPS Only
- SECURE_SSL_REDIRECT = True
- SECURE_HSTS_SECONDS
- SECURE_BROWSER_XSS_FILTER
- X_FRAME_OPTIONS

---

## 📝 Third-Party Libraries & Their Contributions

| Library | Purpose | Endpoints/Features |
|---------|---------|-------------|
| **djangorestframework** | REST API framework | All API endpoints and serialization |
| **djoser** | Authentication system | `/auth/users/`, `/auth/jwt/create/`, `/auth/jwt/refresh/` |
| **djangorestframework-simplejwt** | JWT tokens | Token creation, refresh, and verification |
| **drf-nested-routers** | Nested API routes | `/products/{id}/reviews/`, `/carts/{id}/items/` |
| **django-filter** | Advanced filtering | Query filtering on products (price, collection, etc.) |
| **social-auth-app-django** | Social authentication | OAuth integration (extensible for Google, GitHub, etc.) |
| **mysqlclient** | MySQL adapter | Database connectivity |
| **django-debug-toolbar** | Development debugging | Performance monitoring in development |

---

## 🎓 What You'll Learn

This project demonstrates:

- ✅ RESTful API design with Django REST Framework
- ✅ JWT authentication and token management
- ✅ Database design with complex relationships
- ✅ Custom permissions and role-based access control
- ✅ Advanced filtering and pagination
- ✅ Nested serializers and ViewSets
- ✅ Signal handlers for automation
- ✅ Query optimization (N+1 prevention)
- ✅ Professional project structure
- ✅ Production-ready error handling

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📧 Contact & Support

For questions or support, please open an issue on the repository or contact the development team.

---

**Built with ❤️ using Django & Django REST Framework**

**Last Updated:** November 2024  
**Version:** 1.0.0

