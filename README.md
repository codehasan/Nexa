# Nexa E-Commerce API 🛍️

A production-ready RESTful e-commerce backend built with **Django** and **Django REST Framework**.

## 🌟 Key Features

- **JWT Authentication** with refresh token lifecycle
- **Product Management** with advanced filtering (collection, price range, search)
- **Shopping Cart System** - UUID-based anonymous carts
- **Order Management** with payment status tracking
- **Nested Reviews** with parent-child reply functionality
- **Role-Based Access Control** - Admin & customer permissions
- **Customer Profiles** with membership tiers
- **Pagination & Optimization** - Query optimization with `select_related()` and `prefetch_related()`

## 🏗️ Tech Stack

**Backend:** Django 5.2+ | **API:** Django REST Framework | **Auth:** JWT (djangorestframework-simplejwt)  
**Database:** MySQL 8.0+ | **Routing:** drf-nested-routers | **Filtering:** django-filter | **Config:** python-dotenv

## 🚀 Quick Start

```bash
# Clone & install
git clone https://github.com/codehasan/Nexa.git && cd Nexa
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your database credentials and settings

# Run migrations & start server
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Server runs at `http://localhost:8000`

**Note:** All sensitive configuration is managed via `.env` file (see `.env.example` for template)

---

## 🔐 API Endpoints Overview

| Category | Endpoint | Purpose |
|----------|----------|---------|
| **Auth** | `POST /auth/users/` | Register new user |
| | `POST /auth/jwt/create/` | Get JWT tokens |
| | `POST /auth/jwt/refresh/` | Refresh access token |
| **Products** | `GET /store/products/` | List products with filters |
| | `GET /store/collections/` | Browse collections |
| **Orders** | `POST /store/orders/` | Create order from cart |
| | `GET /store/orders/` | View user's orders |
| **Cart** | `POST /store/carts/` | Create new cart |
| | `POST /store/carts/{id}/items/` | Add items to cart |
| **Reviews** | `GET /store/products/{id}/reviews/` | View product reviews |
| | `POST /store/products/{id}/reviews/` | Create review or reply |
| **Profile** | `GET /store/customers/me/` | View own profile |
| | `PUT /store/customers/me/` | Update profile |

## 📦 Project Structure

```
Nexa/
├── nexa/              # Main Django config
├── store/             # Core e-commerce app
│   ├── models.py      # Product, Cart, Order, Review
│   ├── views.py       # DRF ViewSets
│   ├── serializers.py # Nested serializers
│   ├── filters.py     # Advanced filtering
│   └── signals/       # Auto-customer creation
├── core/              # User auth app
├── manage.py
└── requirements.txt
```

## 🔒 Access Control

- **Anonymous:** View products, browse collections, manage carts
- **Authenticated:** Create orders, write reviews, manage profile
- **Admin:** Full CRUD on products, collections, orders

---

## 🎯 Key Highlights

- **Query Optimization** - `select_related()` and `prefetch_related()` to prevent N+1 queries
- **Nested Reviews** - Self-referencing replies for threaded discussions  
- **UUID-Based Carts** - Anonymous-friendly shopping experience
- **Role-Based Permissions** - Custom permission classes for admin/user access
- **Advanced Filtering** - Filter by collection, price range, and search terms
- **Pagination** - Efficient data loading with 10 items per page

---

## 🎓 Learning Outcomes

This project demonstrates:
- RESTful API design with Django REST Framework
- JWT authentication with refresh token lifecycle
- Complex database relationships and signals
- Custom permissions and role-based access control
- Query optimization techniques
- Professional project structure


