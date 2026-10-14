# Cloud Media & Auth Microservice Platform

A lightweight, containerized microservices application built to demonstrate modern backend engineering, user authentication, persistent data storage, and container orchestration using Docker, Python FastAPI, PostgreSQL, and Redis.

---

### Core Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)

---

## 🚀 Architecture & Features

* **Backend Framework:** Python (FastAPI) with auto-generated interactive OpenAPI/Swagger documentation.
* **Database:** PostgreSQL 15 (Relational data & user credential persistence).
* **Caching Layer:** Redis (In-memory session & cache management).
* **Containerization:** Docker & Docker Compose (Multi-container orchestration on a single isolated network).

---

## 📂 Project Structure

```text
cloud-media-project/
├── README.md                # Project documentation
├── docker-compose.yml       # Docker Compose multi-container orchestration
├── gateway/                 # Nginx API Gateway / Load Balancer configs
└── services/
    ├── auth-service/        # FastAPI user registration & authentication service
    │   ├── Dockerfile
    │   ├── main.py
    │   └── requirements.txt
    └── file-service/        # Media processing & upload service (In development)
```

---

## ⚙️ Getting Started Locally

### Prerequisites

* [Docker Desktop](https://www.docker.com/) installed and running.
* [Git](https://git-scm.com/) installed on your machine.

### Installation & Running

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AsherFerdinand/docker-fastapi-microservice-stack.git
   cd docker-fastapi-microservice-stack
   ```

2. **Spin up the stack using Docker Compose:**
   ```bash
   docker compose up --build -d
   ```

3. **Verify running containers:**
   ```bash
   docker ps
   ```

---

## 🔗 Interactive API Documentation & Testing

Once the services are up and running, interact directly with the **FastAPI Swagger UI**:

* **Auth Service Interactive Docs:** [http://localhost:3000/docs](http://localhost:3000/docs)

### Endpoints

* `POST /register`: Registers a new user. Passwords are encrypted using `bcrypt` before storing them in PostgreSQL.

---

## 🧪 Database Verification

To verify that registered users are successfully saved inside the PostgreSQL container, run:

```bash
docker exec -it local_postgres psql -U admin -d mediadb -c "SELECT id, username FROM users;"
```

---

## 🛠️ Project Roadmap & Status

> ⚠️ **Status:** *Work in Progress (Active Development)*

This project is currently under active development. Below is the step-by-step roadmap for full microservices implementation:

* [x] **Phase 1: Core Foundation & Auth Service** *(Completed)*
  * Containerized PostgreSQL and Redis using Docker Compose.
  * Developed Python FastAPI Auth Service with bcrypt password hashing.
  * Verified persistent data storage inside the PostgreSQL container.
  * Added Swagger UI documentation and initial Git integration.

* [ ] **Phase 2: Gateway Routing & Media Storage** *(Next Step)*
  * Integrate an **Nginx API Gateway / Load Balancer** on port `80` to route traffic dynamically to backend microservices.
  * Build the **File Microservice** to handle media uploads (Images/PDFs) and URL shortening.
  * Integrate object storage for file persistence and Redis caching for quick URL lookups.

* [ ] **Phase 3: GitOps, CI/CD & Deployment** *(Future)*
  * Set up **GitHub Actions** CI/CD pipeline for automated testing and container image checks.
  * Write **Terraform** scripts to provision cloud infrastructure ($0 tier / low-spec VPS).
  * Deploy the entire stack to the cloud using Docker Compose on Linux.
```
