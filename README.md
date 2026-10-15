# Cloud Media & Auth Microservice Platform

A containerized full-stack microservices web platform built to demonstrate modern backend engineering, JWT authentication, persistent data storage, Redis caching, reverse proxy gateway routing, and a Google Drive-style web frontend.

---

### Core Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

---

## 🚀 Key Architecture & Features

- **Frontend Dashboard:** A Google Drive-style Web UI served on Port 80 for logging in, uploading images, viewing uploaded file grids, thumbnail rendering, and live data-source detection (Cache vs. Database).
- **API Gateway (Nginx):** Public entry point on Port 80 routing static frontend traffic (`/`), Auth requests (`/api/v1/auth/`), and File service requests (`/api/v1/files/`).
- **Auth Microservice:** FastAPI microservice handling bcrypt password hashing and PyJWT token generation.
- **File Upload Microservice:** Protected by JWT Bearer security; handles image uploads, local host bind-mount storage (`./uploads`), and static image serving.
- **Metadata Persistence:** PostgreSQL 15 relational database storing user records (`users`) and file upload metadata (`file_metadata`).
- **In-Memory Caching (Redis):** Caching file list responses for `GET /my-files` with a 60-second TTL to accelerate response times (<1ms) and reduce database query load, featuring automated cache invalidation upon new file upload (`POST /upload`).

---

### Architecture & Traffic Flow

```mermaid
graph TD
    User["User / Web Browser"] -->|Port 80| Gateway["Nginx API Gateway\n(Port 80)"]

    Gateway -->|/| Frontend["Frontend Static Assets\n(/public_html)"]
    Gateway -->|/api/v1/auth/| AuthSvc["Auth Service\n(FastAPI - Port 3000)"]
    Gateway -->|/api/v1/files/| FileSvc["File Service\n(FastAPI - Port 4000)"]

    AuthSvc -->|bcrypt / JWT| DB[("PostgreSQL Database\n(Port 5432 / mediadb)")]
    FileSvc -->|Metadata Tracking| DB
    FileSvc -->|Lookups & Invalidation| Cache[("Redis In-Memory Cache\n(Port 6379)")]
    FileSvc -->|File Storage| Volume[("Host Bind Mount\n(./uploads)")]

    style Gateway fill:#ffcc00,stroke:#333,stroke-width:2px,color:#000
    style AuthSvc fill:#3776AB,stroke:#333,stroke-width:2px,color:#fff
    style FileSvc fill:#009688,stroke:#333,stroke-width:2px,color:#fff
    style DB fill:#336791,stroke:#333,stroke-width:2px,color:#fff
    style Cache fill:#dc382d,stroke:#333,stroke-width:2px,color:#fff
    style Frontend fill:#e34f26,stroke:#333,stroke-width:2px,color:#fff
```

---

## 📂 Project Structure

```text
cloud-media-project/
├── docker-compose.yml        # Docker Compose multi-container orchestration
├── README.md                 # Project documentation
├── frontend/
│   └── index.html            # Google Drive-style web dashboard frontend
├── gateway/
│   └── nginx.conf            # Nginx API Gateway reverse proxy configuration
├── services/
│   ├── auth-service/         # User registration & JWT authentication service
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   └── requirements.txt
│   └── file-service/         # Media upload, static file serving, & metadata tracking
│       ├── Dockerfile
│       ├── main.py
│       └── requirements.txt
└── uploads/                  # Host directory bind-mounted for image persistence
```

---

## ⚙️ Getting Started Locally

### Prerequisites

- [Docker Desktop](https://www.docker.com/) installed and running.
- [Git](https://git-scm.com/) installed on your machine.

### Installation & Running

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AsherFerdinand/docker-fastapi-microservice-stack.git
   cd docker-fastapi-microservice-stack
   ```

2. **Spin up the multi-container stack using Docker Compose:**
   ```bash
   docker compose up --build -d
   ```

3. **Verify running containers:**
   ```bash
   docker ps
   ```

---

## 🔗 Endpoints & Web Access

| Service / Interface | Local URL | Description |
| :--- | :--- | :--- |
| **Web Dashboard** | [http://localhost/](http://localhost/) | Main Google Drive-style web page for authentication and uploads |
| **Auth API Docs** | [http://localhost/api/v1/auth/docs](http://localhost/api/v1/auth/docs) | OpenAPI/Swagger interface for Auth endpoints |
| **File Service Docs** | [http://localhost/api/v1/files/docs](http://localhost/api/v1/files/docs) | OpenAPI/Swagger interface for File processing endpoints |

### Key API Endpoints

- **`POST /api/v1/auth/register`**: Registers a new user with bcrypt-hashed credentials.
- **`POST /api/v1/auth/login`**: Authenticates user and generates a Bearer JWT access token.
- **`POST /api/v1/files/upload`**: Uploads an image file (JWT required), saves file to disk, persists metadata to PostgreSQL, and invalidates user cache.
- **`GET /api/v1/files/my-files`**: Fetches user uploaded files metadata list (JWT required). Queries Redis cache first (<1ms TTL: 60s); falls back to PostgreSQL on cache miss.
- **`GET /api/v1/files/static/{filename}`**: Serves stored images statically for frontend thumbnail rendering.

---

## 🧪 Database & Cache Verification

To inspect stored user records and file metadata directly inside the PostgreSQL container:

```bash
docker exec -it local_postgres psql -U admin -d mediadb -c "SELECT * FROM users;"
docker exec -it local_postgres psql -U admin -d mediadb -c "SELECT * FROM file_metadata;"
```

To verify cached keys inside the Redis container:

```bash
docker exec -it local_redis redis-cli KEYS "*"
```

---

## 🛠️ Project Roadmap & Status

- [x] **Phase 1: Core Foundation & Auth Service**
  - Containerized PostgreSQL and Redis using Docker Compose.
  - Developed Python FastAPI Auth Service with bcrypt password hashing and JWT issuance.
  - Verified persistent database storage and initial OpenAPI Swagger integration.

- [x] **Phase 2: Gateway Routing, Media Storage & Caching**
  - Integrated Nginx API Gateway on port `80` to proxy auth and file traffic dynamically.
  - Built File Upload Microservice handling image files and host bind-mount storage.
  - Added PostgreSQL metadata tracking (`file_metadata`) and Redis caching with automatic invalidation.
  - Implemented Google Drive-style web frontend on Port 80 with thumbnail rendering.

- [ ] **Phase 3: GitOps, CI/CD & Cloud Deployment**
  - Set up **GitHub Actions** CI/CD pipeline for automated testing and container build checks.
  - Provision cloud infrastructure and deploy containerized stack to Linux VPS.
