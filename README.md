# Product Marketplace API

A comprehensive Django REST API for managing products in a marketplace where businesses can create users, assign roles, and manage product approval workflows.

## Features

### Core Business Rules Implemented
- Any authorized user can create or edit products
- Only users with approval permission can approve products
- Only approved products are visible to the public/external users
- Unauthorized actions must be blocked

### System Features
- JWT Authentication with access/refresh tokens
- Role-based permissions (Admin, Editor, Approver, Viewer)
- Business-level data isolation
- Product approval workflow (draft -> pending_approval -> approved)
- Image upload support for products
- Beautiful web interface with login/dashboard
- Browsable API for easy testing
- Comprehensive testing with pytest
- Pagination and filtering

### AI Chatbot Features
- **Intelligent Product Assistant**: AI-powered chatbot that answers questions about products
- **Context-Aware Responses**: Uses approved products data to provide accurate information
- **Chat History**: Stores conversation history for each user
- **Natural Language Queries**: Supports questions like "What products are available?", "Which products are under $50?, and so on"
- **Privacy-Focused**: Chat messages are protected and only visible to superusers in admin

---

## Quick Start

### Prerequisites
- Python 3.13
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/angelocodes/product_marketplace.git
cd product_marketplace
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Database Migrations
```bash
python manage.py migrate
```

### 5. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 6. Start the Development Server
```bash
python manage.py runserver
```

### 7. Access the Application
- Web Interface: http://127.0.0.1:8000/
- API Documentation: http://127.0.0.1:8000/api/
- Admin Panel: http://127.0.0.1:8000/admin/

---

## User Roles & Test Accounts
You can create the below users as test accounts.

| Username | Password | Role | Permissions |
|----------|----------|------|-------------|
| `business_admin` | `admin123` | Admin | Full access within business |
| `product_editor` | `editor123` | Editor | Create/edit products |
| `product_approver` | `approver123` | Approver | Approve products |
| `product_viewer` | `viewer123` | Viewer | Read-only access |

---

## Authentication

### JWT Token Authentication
```bash
# Get access token
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "business_admin", "password": "admin123"}'

# Use token in requests
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     http://127.0.0.1:8000/api/products/
```

### Web Interface Login
- Visit: http://127.0.0.1:8000/login/
- Use any test credentials above
- Access dashboard at: http://127.0.0.1:8000/

---

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/token/` | Obtain JWT access/refresh tokens |
| `POST` | `/api/token/refresh/` | Refresh access token |

### Business Endpoints

| Method | Endpoint | Description | Permissions |
|--------|----------|-------------|-------------|
| `GET` | `/api/businesses/` | List businesses | Authenticated users |
| `POST` | `/api/businesses/` | Create business | Admin |
| `GET` | `/api/businesses/{id}/` | Get business details | Business members |
| `PUT` | `/api/businesses/{id}/` | Update business | Admin |
| `DELETE` | `/api/businesses/{id}/` | Delete business | Admin |

### User Management Endpoints

| Method | Endpoint | Description | Permissions |
|--------|----------|-------------|-------------|
| `GET` | `/api/users/` | List users in business | Business admin |
| `POST` | `/api/users/` | Create user | Business admin |
| `GET` | `/api/users/{id}/` | Get user details | Business admin |
| `PUT` | `/api/users/{id}/` | Update user | Business admin |
| `DELETE` | `/api/users/{id}/` | Delete user | Business admin |

### Product Endpoints

| Method | Endpoint | Description | Permissions |
|--------|----------|-------------|-------------|
| `GET` | `/api/products/` | List products | Role-based filtering |
| `POST` | `/api/products/` | Create product | Editor/Admin/Approver |
| `GET` | `/api/products/{id}/` | Get product details | Role-based access |
| `PUT` | `/api/products/{id}/` | Update product | Owner/Admin |
| `DELETE` | `/api/products/{id}/` | Delete product | Owner/Admin |
| `POST` | `/api/products/{id}/approve/` | Approve product | Approver only |

### Public Endpoints (No Authentication Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/public/products/` | List approved products |

### 🤖 AI Chatbot Endpoints

| Method | Endpoint | Description | Permissions |
|--------|----------|-------------|-------------|
| `POST` | `/api/chat/` | Send message and get AI response | Authenticated users |
| `GET` | `/api/chat/history/` | Get user's chat history | Authenticated users |

---

## 🤖 AI Chatbot Setup & Usage

The AI chatbot provides intelligent answers about products using Google's Gemini AI. It can answer questions like "What products are available?", "Which products are under $50?", or "Tell me about product X".

### Prerequisites
- **Google Gemini API Key**: Get one from [Google AI Studio](https://aistudio.google.com/)
- **Approved Products**: Chatbot only uses approved products for responses

### Configuration

1. **Set up API Key**:
   ```bash
   # Edit chatbot/.env file
   GEMINI_API_KEY = your_api_key_here
   ```

2. **Install Dependencies**:
   ```bash
   pip install google-genai python-dotenv
   ```

### Using the Chatbot

#### 1. Authentication Required
All chatbot endpoints require JWT authentication:

```bash
# Get access token first
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

#### 2. Send Chat Messages
```bash
# Ask about available products
curl -X POST http://127.0.0.1:8000/api/chat/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "What products are available?"}'

# Response example:
{
    "id": 1,
    "user_message": "What products are available?",
    "ai_response": "Based on our approved products, we currently have: X Product - A great product ($25.00) by Test Business...",
    "timestamp": "2026-01-12T10:45:00Z"
}
```

#### 3. View Chat History
```bash
# Get your conversation history
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     http://127.0.0.1:8000/api/chat/history/

# Response example:
[
    {
        "id": 1,
        "user_message": "What products are available?",
        "ai_response": "Based on our approved products...",
        "timestamp": "2026-01-12T10:45:00Z"
    }
]
```

### Example Conversations

```bash
# Question 1: Available products
curl -X POST http://127.0.0.1:8000/api/chat/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "What products do you have?"}'

# Question 2: Price filtering
curl -X POST http://127.0.0.1:8000/api/chat/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me products under $50"}'

# Question 3: Specific product info
curl -X POST http://127.0.0.1:8000/api/chat/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about the Test Product"}'
```

### How It Works

1. **Product Context**: The chatbot queries only approved products from your database
2. **AI Processing**: Uses Google Gemini 2.5 Flash model for intelligent responses
3. **Privacy**: Chat messages are stored securely and only accessible to the user who created them
4. **Admin Access**: Superusers can view all chat messages in the Django admin for moderation

### Production Scalability Considerations

For production deployments with large product catalogs (millions to hundreds of millions of products), the current context-loading approach may become inefficient. **Recommended Production Enhancement: Semantic Search with Vector Embeddings**

#### Implementation Strategy:
- **Vector Database**: Use Qdrant, pgvector (PostgreSQL) or Pinecone for storing product embeddings
- **Embedding Generation**: Generate embeddings for product descriptions using embedding models like text-embedding-3-small, or similar ones
- **Query Processing**: For each user question, create embeddings and perform similarity search to find top 10-50 most relevant products
- **Context Optimization**: Include only semantically relevant products in AI prompts instead of loading entire catalog
- **Performance Benefits**: Sub-second query times even with billions of products, reduced memory usage, and more accurate AI responses

#### Benefits:
- Scales to massive product catalogs
- Provides more relevant AI responses based on semantic similarity
- Reduces computational overhead and API costs
- Enables advanced features like product recommendations


---

## Business Rules Implementation

### 1. Product Creation & Editing
**Rule**: Any authorized user can create or edit products

**Implementation**:
- Users with roles: `admin`, `editor`, `approver` can create products
- Product owners and admins can edit their products
- Products are automatically assigned to the creator's business

**API Usage**:
```bash
# Create product (Editor/Admin/Approver)
curl -X POST http://127.0.0.1:8000/api/products/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Product",
    "description": "Product description",
    "price": 99.99,
    "image": null
  }'

# Edit product (Owner/Admin only)
curl -X PUT http://127.0.0.1:8000/api/products/1/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Product Name"}'
```

### 2. Product Approval
**Rule**: Only users with approval permission can approve products

**Implementation**:
- Only users with `approver` role can approve products
- Products must be in `pending_approval` status to be approved
- Approval changes status to `approved`

**API Usage**:
```bash
# Submit product for approval (change status)
curl -X PUT http://127.0.0.1:8000/api/products/1/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "pending_approval"}'

# Approve product (Approver only)
curl -X POST http://127.0.0.1:8000/api/products/1/approve/ \
  -H "Authorization: Bearer APPROVER_TOKEN"
```

### 3. Public Product Visibility
**Rule**: Only approved products are visible to the public/external users

**Implementation**:
- Public API (`/api/public/products/`) only shows `approved` products
- No authentication required for public access
- Internal API filters based on user roles

**API Usage**:
```bash
# Public access (no auth required)
curl http://127.0.0.1:8000/api/public/products/

# Authenticated access (role-based filtering)
curl -H "Authorization: Bearer TOKEN" \
     http://127.0.0.1:8000/api/products/
```

### 4. Access Control
**Rule**: Unauthorized actions must be blocked

**Implementation**:
- Role-based permissions on all endpoints
- Object-level permissions for product ownership
- Business-level data isolation
- Superuser overrides for admin access

---

## Image Upload

Products support image uploads:

### Upload via API
```bash
curl -X POST http://127.0.0.1:8000/api/products/ \
  -H "Authorization: Bearer TOKEN" \
  -F "name=Product with Image" \
  -F "description=Description" \
  -F "price=29.99" \
  -F "image=@/path/to/image.jpg"
```

### Access Uploaded Images
- Images stored in: `media/products/`
- URLs accessible at: `/media/products/filename.jpg`

---

## Testing

### Run All Tests
```bash
python -m pytest --ds=product_marketplace.settings api/tests.py -v
```

## Continuous Integration

This project uses CircleCI for automated testing.

### CI Pipeline Features
- **Automated Testing**: Runs all pytest tests on every push
- **Multi-branch Support**: Runs on all branches

### CI Configuration
The CI configuration (`.circleci/config.yml`) runs the same test command locally.

---

## Configuration

### Environment Variables
- `DJANGO_SETTINGS_MODULE`: Set to `product_marketplace.settings`
- `SECRET_KEY`: Change for production
- `DEBUG`: Set to `False` for production

### Media Files
- Images stored in `media/products/`
- Configure web server to serve media files in production

### Database
- Default: SQLite (development)
- Production: PostgreSQL recommended
