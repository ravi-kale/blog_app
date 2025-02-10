# Blog API Application 📝
---

> 🚀 A secure blog API built with FastAPI, PostgreSQL, and Cerbos for role-based access control. The application supports user authentication and authorization for managing blog posts.

Note: This document is Notion formatted

## 🌟 Features
- ✅ User authentication with JWT tokens
- 🔐 Role-based access control (Admin, Author, Reader)
- 📝 CRUD operations for blog posts
- 🗄️ PostgreSQL database integration
- 🐳 Docker containerization
- 🛡️ Cerbos policy enforcement

## 🛠️ Prerequisites
| Tool | Purpose |
|------|----------|
| Docker | Containerization |
| Docker Compose | Container orchestration |
| Git | Version control |

## 🚀 Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone <repository-url>
cd blog-api
```

### 2️⃣ Create necessary directories
```bash
mkdir -p data/postgres
```

### 3️⃣ Start the application
```bash
docker-compose up --build -d
OR
docker-compose up -d
```

> 💡 The application will be available at `http://localhost:8000`

## 📚 API Documentation

### 🔑 Authentication

#### Register a new user (Note: Role can be any, even Admin, MVP purpose)
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "secretpassword",
    "role": "author"
  }'
```

#### Login
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "secretpassword"
  }'
```

### 📝 Blog Posts

#### Create a new post
```bash
curl -X POST http://localhost:8000/posts \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Blog Post",
    "content": "This is the content of my first blog post."
  }'
```

#### Get all posts
```bash
curl -X GET http://localhost:8000/posts \
  -H "Authorization: Bearer <your-token>"
```

#### Get a specific post
```bash
curl -X GET http://localhost:8000/posts/{post_id} \
  -H "Authorization: Bearer <your-token>"
```

#### Update a post
```bash
curl -X PUT http://localhost:8000/posts/{post_id} \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "content": "Updated content"
  }'
```

#### Delete a post
```bash
curl -X DELETE http://localhost:8000/posts/{post_id} \
  -H "Authorization: Bearer <your-token>"
```

## 🔧 Technical Specifications

### Tech Stack
| Technology | Purpose |
|------------|----------|
| FastAPI | Modern Python web framework |
| PostgreSQL | Primary database |
| SQLAlchemy | ORM for database operations |
| Cerbos | Policy enforcement engine |
| JWT | Authentication mechanism |
| Docker | Containerization |

### 👥 User Roles
| Role | Permissions |
|------|------------|
| Admin | Full access to all posts |
| Author | Can create, read, update, and delete their own posts |
| Reader | Can only read posts |

### ⚙️ Environment Variables
| Variable | Description |
|----------|-------------|
| POSTGRES_USER | Database user |
| POSTGRES_PASSWORD | Database password |
| POSTGRES_DB | Database name |
| CERBOS_HOST | Cerbos service host |
| DATABASE_URL | PostgreSQL connection string |

### 🔌 Ports
| Service | Port |
|---------|------|
| FastAPI application | 8000 |
| PostgreSQL | 5432 |
| Cerbos | 3592, 3593 |

## 💻 Development

### To make changes to the application:

1️⃣ Stop the containers:
```bash
docker-compose down
```

2️⃣ Rebuild and start the containers:
```bash
docker-compose up --build -d
```

## ❗ Troubleshooting

### Common Issues

#### 🔴 Database Connection Issues
- ✔️ Ensure PostgreSQL container is running
- ✔️ Check database credentials in docker-compose.yml
- ✔️ Verify DATABASE_URL in environment variables

#### 🔴 Authorization Issues
- ✔️ Verify JWT token is valid and not expired
- ✔️ Check user roles and permissions
- ✔️ Ensure Cerbos policies are correctly configured

---
## 📄 License
[Add your license information here]

---
> 📝 **Note**: This documentation is maintained regularly. For the latest updates, please check the repository.
