# Grocery Store Backend API

This is a Django REST API for an online grocery store. Customers can browse, buy, and manage products, while store managers can add/edit inventory and view sales.

# Features

# User
- Register/Login (JWT Authentication)
- Role: `customer` or `manager`

# Customer
- Browse products (filter by category/popularity)
- Add/Remove from Cart
- Wishlist support
- Checkout (with promo code support)

# Manager
- Add/Edit/Delete Products
- View Sales Reports (most/least sold)
- Get Low Stock Alerts

# Enhancements
- Promo Code Discount System
- Low Stock Notifications

# Authentication
Use JWT Token: `POST /api/token/`

# API Documentation
Postman Collection is included in the repo: [`Grocery_store.postman_collection.json`](Grocery_store.postman_collection.json)

# Tech Stack
- Python 3
- Django & Django REST Framework
- SQLite (can upgrade to PostgreSQL)

# Setup

``bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
