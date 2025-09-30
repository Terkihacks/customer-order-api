# Customer Order API

## 📌 Project Overview

**Customer Order API** is a robust RESTful service built with Django and Django REST Framework. It provides a seamless interface for **customers**, **orders**, and **notifications**, ensuring efficient order handling in business environments. The API is designed for scalability, security, and maintainability, making it suitable for small businesses and enterprise-level applications.

---

##  Features

- **Customer Management**  
  - Create, read, update, and delete customer profiles.  
  - Validate customer information with strict field checks (email, phone, address).  

- **Order Management**  
  - Create and manage customer orders.  
  - Track order status (pending, processing, completed, canceled).  
  - Link orders to specific customers for efficient tracking.  

- **Notifications**  
  - Automatic notifications via email or SMS when an order status changes.  
  - Event-driven architecture for future scalability.  

- **Authentication & Authorization**  
  - JWT-based authentication for secure API access.  
  - Role-based access control for admin and regular users.  

- **Logging & Monitoring**  
  - Track API usage and error logs for auditing and debugging.  
  - Ready for integration with monitoring tools (e.g., Prometheus, Sentry).  

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.9+, Django 4.x, Django REST Framework |
| Database | PostgreSQL (primary), SQLite (for development) |
| Authentication | JWT (JSON Web Tokens) |
| Containerization | Docker, Docker Compose |
| Testing | Pytest, Django Test Framework |
| CI/CD | GitHub Actions (optional) |

---

## 📂 API Structure

---

## ⚡ API Endpoints

### Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register/` | POST | Register a new user |
| `/api/auth/login/` | POST | Login user and receive JWT token |
| `/api/auth/logout/` | POST | Logout user and invalidate token |

### Customers
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/customers/` | GET | List all customers |
| `/api/customers/` | POST | Create a new customer |
| `/api/customers/{id}/` | GET | Retrieve a specific customer |
| `/api/customers/{id}/` | PUT | Update customer details |
| `/api/customers/{id}/` | DELETE | Delete a customer |

### Orders
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/orders/` | GET | List all orders |
| `/api/orders/` | POST | Create a new order |
| `/api/orders/{id}/` | GET | Retrieve specific order details |
| `/api/orders/{id}/` | PUT | Update order details |
| `/api/orders/{id}/` | DELETE | Cancel/delete order |

### Example Request

```bash
POST /api/customers/
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

{
  "name": "John Doe",
  "code": "JD001",
  "email": "john@example.com",
  "phone": "+254712345678",
}


## Installation & Setup

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- Git

### Steps

1. **Clone the repository:**

```bash
git clone https://github.com/Terkihacks/customer-order-api.git
cd customer-order-api

2. **Set up environment variables:**

```bash
cp .env.example .env

3. **Build and start Docker containers::**

```bash
docker-compose up --build

4. **Run database migrations:**

```bash
docker-compose exec web python manage.py migrate

4. **Running Tests**

```bash
docker-compose exec web python manage.py test



