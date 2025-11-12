# Spendo Project: Local Development with Docker Compose

This guide explains how to set up your local development environment using Docker and Docker Compose.

## Table of Contents

- [Installing Docker](#-installing-docker)
- [Quick Start: Using Docker Compose for Local Development](#-quick-start-using-docker-compose-for-local-development)
- [Project Structure](#project-structure)
- [Environment Files](#environment-files)
- [Database Persistence with Docker Volumes](#-database-persistence-with-docker-volumes)
- [Deployment](#-deployment)
  - [Heroku Deployment](#heroku-deployment)

---

## 🐳 Installing Docker

To use Docker, you must first install it on your system. Follow the official instructions for your operating system:

- [Get Docker](https://docs.docker.com/get-docker/)

---

## ⚡️ Quick Start: Using Docker Compose for Local Development

1. **Clone the repository**
2. **Copy `.env.example` files to `.env` and fill in any required values**
3. **Build and start all services:**
   ```bash
   docker compose -f config/docker-compose.yml up --build
   ```
4. **To run Django management commands inside the backend container:**
   ```bash
   docker compose -f config/docker-compose.yml exec backend python manage.py makemigrations
   docker compose -f config/docker-compose.yml exec backend python manage.py migrate
   ```

---

## Project Structure

This project uses a monorepo structure:

```
Spendo/
├── frontend/          # React frontend (Vite)
├── backend/           # Django backend
│   └── spendo/        # Django project
├── config/            # Configuration files
│   ├── docker-compose.yml
│   └── postgres.env
└── docs/              # Documentation
```

**Note:** For Heroku deployment, symlinks exist in the root:

- `requirements.txt` → `backend/requirements.txt`
- `.python-version` → `backend/.python-version`

---

## Environment Files

- `config/postgres.env` (for the database)
- `backend/spendo/.env` (for Django backend)
- `frontend/.env` (for frontend)

See the `.env.example` files for required variables.

---

## 🗄️ Database Persistence with Docker Volumes

- **Database data is persisted using Docker volumes.**
- The line:
  ```yaml
  - postgres_data:/var/lib/postgresql/data
  ```
  in the `db` service ensures that all PostgreSQL data is stored in a Docker-managed volume called `postgres_data`.
- **Data in Docker volumes is persistent:**
  - Stopping or removing containers with `docker compose down` does NOT delete your database data.
  - Data will be available again when you restart your containers with `docker compose up`.
  - To permanently delete the data, use `docker compose down -v` to remove the volume as well.

---

## 🚀 Deployment

### Heroku Deployment

For detailed Heroku deployment instructions, see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

**Quick deploy:**

```bash
# Configure buildpacks (first time only)
heroku buildpacks:clear -a your-app-name
heroku buildpacks:add heroku/nodejs -a your-app-name
heroku buildpacks:add heroku/python -a your-app-name

# Deploy (push to Heroku)
git push heroku main
# or
git push heroku master
```

Migrations run automatically via the `release` command in your Procfile.

**Important:** This project uses symlinks in the root directory (`requirements.txt` and `.python-version`) that point to `backend/` for Heroku buildpack detection. These must be committed to git.

---

For more details, see:

- `docs/DEPLOYMENT.md` - Deployment guide
