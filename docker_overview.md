# Docker Overview

Docker is a platform that allows you to package, distribute, and run applications in lightweight, portable containers. Here’s a high-level overview of how Docker works:

---

## 🧑‍💻 Development vs. Deployment: docker-compose and Single-Container

- It is perfectly fine—and often recommended—to use `docker-compose` for local development, even if you deploy to Heroku (or another platform) with a single-container setup.
- With `docker-compose`, you can:
    - Run frontend, backend, and database as separate containers.
    - Use volume mounts for live code changes and hot-reloading.
    - Debug and restart services independently.
    - Mimic a real-world microservices or multi-service environment.
- For deployment (e.g., Heroku), you use a single-container image for simplicity and compatibility with the platform.
- Just ensure your code and environment variables work in both setups (e.g., use `.env` files and environment variable fallbacks).

**Summary:**

- Use `docker-compose` for development convenience and flexibility.
- Use a single-container Dockerfile for simple deployment to platforms like Heroku.
- Keep your configuration and environment files compatible with both approaches for a smooth workflow.

---

## 1. Containerization

Docker uses containers to encapsulate an application and all its dependencies (libraries, code, runtime, etc.) into a single package. This ensures the app runs the same way regardless of where it’s deployed.

## 2. Images

A Docker image is a snapshot of a filesystem and configuration. It’s built from a Dockerfile, which contains instructions for setting up the environment and installing dependencies.

## 3. Containers

A container is a running instance of an image. Containers are isolated from each other and the host system, but they can communicate through defined channels.

## 4. Docker Engine

This is the core part of Docker that creates and manages containers on your system.

## 5. Portability

Because containers include everything needed to run the app, you can move them between different machines (development, testing, production) without worrying about environment differences.

## 6. Workflow

- Write a Dockerfile describing your app’s environment.
- Build an image from the Dockerfile.
- Run a container from the image.
- Share the image via Docker Hub or other registries.

## Key Benefit

With Docker, you don’t need to manually install all the requirements on each PC. You define all dependencies in a Dockerfile, build an image, and anyone can run your app in a container using that image—no need to install dependencies directly on their system. This ensures consistency and saves time when setting up new environments.

---

## 🐳 Installing Docker

To use Docker, you must first install it on your system. Follow the official instructions for your operating system:

- [Get Docker](https://docs.docker.com/get-docker/)

---

## ⚡️ Quick Start: Using Docker in a New or Existing Project

### If You Are **Creating the Docker Setup from Scratch**

- Install Docker on your system.
- Create Dockerfiles for each service (backend, frontend, etc.).
- Write a `docker-compose.yml` file to define your services and how they interact.
- Create example `.env.example` files for required environment variables.
- Document the setup steps in your README or this file.
- Build and run your containers with `docker compose up --build`.

### If You Are **Cloning an Existing Repo with Docker Setup**

- Install Docker on your system (if not already installed).
- Clone the repository.
- Copy `.env.example` files to `.env` and fill in any required values (or create `.env` files as documented).
- Run `docker compose up --build` to build and start all services.
- Use the documented commands to run migrations or other setup steps inside containers if needed.

> **Note:**
>
> - Never commit real secrets or production credentials to your repository. Use example files and documentation for sharing required environment variables.
> - If you are working in a team, always keep `.env.example` files up to date with any new variables.

---

## Full Stack Project: Docker Compose Setup Example

This section covers a typical setup for a full stack project (React frontend, Django backend, PostgreSQL database) using Docker Compose.

### 1. Directory Structure

- client/app: React frontend (Vite)
- server/Spendo: Django backend

### 2. Docker Compose File Example (`docker-compose.yml`)

```yaml
services:
    frontend:
        build:
            context: ./client/app
        working_dir: /app
        ports:
            - '5173:5173'
        environment:
            - NODE_ENV=development
        volumes:
            - ./client/app:/app
        command: ['npm', 'run', 'dev', '--', '--host']

    backend:
        build:
            context: ./server/Spendo
        working_dir: /code
        ports:
            - '8000:8000'
        volumes:
            - ./server/Spendo:/code
        env_file:
            - ./server/Spendo/Spendo/.env
        depends_on:
            - db
        command: sh -c "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"

    db:
        image: postgres:16
        restart: always
        env_file:
            - ./postgres.env
        ports:
            - '5432:5432' # Change left port if 5432 is in use on host
        volumes:
            - postgres_data:/var/lib/postgresql/data

volumes:
    postgres_data:
```

### 2a. Example Dockerfile for Frontend (`client/app/Dockerfile`)

```dockerfile
# Frontend Dockerfile (Vite/React)
FROM node:20
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
CMD ["npm", "run", "dev", "--", "--host"]
```

### 2b. Example Dockerfile for Backend (`server/Spendo/Dockerfile`)

```dockerfile
# Backend Dockerfile (Django)
FROM python:3.12
WORKDIR /code
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### 2c. Dockerfile and docker-compose.yml Breakdown

#### Frontend Dockerfile (`client/app/Dockerfile`)

- `FROM node:20` — Uses the official Node.js 20 image as the base for building and running the frontend.
- `WORKDIR /app` — Sets the working directory inside the container to `/app`.
- `COPY package*.json ./` — Copies `package.json` and `package-lock.json` for efficient dependency installation.
- `RUN npm install` — Installs frontend dependencies.
- `COPY . .` — Copies the rest of the frontend source code into the container.
- `CMD ["npm", "run", "dev", "--", "--host"]` — Starts the Vite development server, accessible from outside the container.

#### Backend Dockerfile (`server/Spendo/Dockerfile`)

- `FROM python:3.12` — Uses the official Python 3.12 image as the base for the backend.
- `WORKDIR /code` — Sets the working directory inside the container to `/code`.
- `COPY requirements.txt ./` — Copies the requirements file for dependency installation.
- `RUN pip install --upgrade pip && pip install -r requirements.txt` — Installs backend dependencies.
- `COPY . .` — Copies the rest of the backend source code into the container.
- `CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]` — Starts the Django development server, listening on all interfaces.

#### docker-compose.yml

- `services:` — Defines each containerized service (frontend, backend, db).
- `build:` — Specifies the build context (directory) for each service and uses the Dockerfile in that directory.
- `working_dir:` — Sets the working directory for commands run in the container.
- `ports:` — Maps container ports to host ports (e.g., `8000:8000` for backend, `5173:5173` for frontend).
- `volumes:` — Mounts local code into the container for live reload during development.
- `env_file:` — Loads environment variables from a file into the container.
- `depends_on:` — Ensures services start in the correct order (e.g., backend waits for db).
- `command:` — Overrides the default command, useful for running migrations or custom startup scripts.

This breakdown should help you understand what each part of the Docker and Compose setup does and why it's needed for a smooth development workflow.

### 3. Environment Files

**`postgres.env`**

```
POSTGRES_DB=spendo_db
POSTGRES_USER=spendo_user
POSTGRES_PASSWORD=spendo_pass
```

**`server/Spendo/Spendo/.env`**

```
DATABASE_URL=postgres://spendo_user:spendo_pass@db:5432/spendo_db
ALLOWED_HOSTS=localhost
```

**`client/app/.env`**

```
VITE_API_URL=http://localhost:8000/api
```

### 4. Running and Managing Containers

- Build and start all services:
    ```bash
    sudo docker compose up --build
    ```
- If you change environment variables or dependencies, rebuild with `--build`.
- To run Django management commands inside the backend container:
    ```bash
    sudo docker compose exec backend python manage.py makemigrations
    sudo docker compose exec backend python manage.py migrate
    ```

### 5. Database Access

- You can connect to the PostgreSQL database from your host (if port mapped) or from inside the db container:
    ```bash
    sudo docker compose exec db psql -U spendo_user spendo_db
    ```

### 5a. Accessing the Database with GUI Tools (e.g., DBeaver, Navicat, TablePlus)

If you want to connect to your Dockerized PostgreSQL database using a GUI tool:

- Use these connection settings in your GUI:

    - **Host:** localhost
    - **Port:** 5432 (or the port you mapped in docker-compose.yml)
    - **User:** spendo_user (from POSTGRES_USER)
    - **Password:** spendo_pass (from POSTGRES_PASSWORD)
    - **Database:** spendo_db (from POSTGRES_DB)

- Make sure the database container is running and the port is mapped in docker-compose.yml:
    ```yaml
    ports:
        - '5432:5432'
    ```
- You can now use tools like DBeaver, Navicat, or TablePlus to browse tables, run queries, and manage your database visually.

### 6. Common Issues

- **Port already in use:** Change the left port in the `ports` section of `docker-compose.yml`.
- **Permission denied on Docker socket:** Add your user to the docker group: `sudo usermod -aG docker $USER` and log out/in.
- **Django can't connect to db:** Ensure `DATABASE_URL` uses `db` as the hostname, not `localhost`.
- **Tables not created:** Make sure migrations run successfully (see above).

---

## 🐞 Common Issues and Fixes in This Project

### 1. Port Conflict on 5432 (PostgreSQL)

**Issue:**

```
failed to bind host port for 0.0.0.0:5432: ... address already in use
```

**Cause:** Port 5432 is already used by another PostgreSQL instance on the host.
**Fix:**

- Stop the native PostgreSQL service with `sudo service postgresql stop` or change the port mapping in `docker-compose.yml` (e.g., `5433:5432`).

### 2. Backend Tries to Connect to DB Before DB is Ready

**Issue:**

```
django.db.utils.OperationalError: connection to server at "db" ... failed: Connection refused
```

**Cause:** Docker starts the backend before the database is ready to accept connections.
**Fix:**

- Added a `wait-for-it.sh` script to the backend service to wait for the database to be ready before running migrations and starting the server.
- Updated `docker-compose.yml` to use this script in the backend service's command.

### 3. wait-for-it.sh: nc: command not found

**Issue:**

```
/wait-for-it.sh: line 10: nc: command not found
```

**Cause:** The backend Docker image did not have `netcat` installed, which is required by the wait-for-it script.
**Fix:**

- Updated the backend Dockerfile to install `netcat-openbsd` (the correct package for Debian-based images):
    ```dockerfile
    RUN apt-get update && apt-get install -y netcat-openbsd
    ```
- Rebuilt the Docker images with `docker-compose build`.

---

## 🛠️ Single-Container (All-in-One) Setup for Portfolio or Demo Projects

If you want to run both your frontend and backend in a single container (for example, for a portfolio project or simple deployment):

- Place a Dockerfile at the root of your project that:
    - Builds the frontend and backend using multi-stage builds.
    - Copies the frontend build output into a directory served by the backend or a static server.
    - Installs Supervisor (or another process manager) to run both the backend (e.g., Django with Gunicorn) and a static file server for the frontend.
    - Copies your backend .env file into the image (if needed) and ensures your backend loads environment variables from it (using python-dotenv or similar).
- Example files:
    - `Dockerfile` (root): Multi-stage build for both frontend and backend, runs Supervisor.
    - `supervisord.conf` (root): Supervisor config to run both processes.
- You do NOT need docker-compose.yml for this setup. Everything runs in one container.
- This is ideal for portfolio/demo projects where simplicity is more important than scalability.

**See the provided Dockerfile and supervisord.conf in this repo for a working example.**

> **Note:** For production or real-world apps, it is better to use separate containers/services for frontend and backend for flexibility and scalability. This single-container approach is mainly for demos and portfolios.

---

### 📝 Example: Single-Container (All-in-One) Docker Setup

Below is a sample setup for running both a React frontend and Django backend in a single Docker container, suitable for portfolio or demo projects.

#### Dockerfile (place at project root)

```dockerfile
# Multi-stage Dockerfile for portfolio deployment (frontend + backend)

# 1. Build frontend
FROM node:20 AS frontend-build
WORKDIR /app
COPY client/app/package*.json ./
RUN npm install
COPY client/app .
RUN npm run build

# 2. Build backend
FROM python:3.12 AS backend-build
WORKDIR /code
COPY server/Spendo/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY server/Spendo .

# 3. Final stage: combine and run both
FROM python:3.12
WORKDIR /code

# Copy backend
COPY --from=backend-build /code /code

# Copy frontend build to Django static files (adjust path if needed)
COPY --from=frontend-build /app/dist /code/client_dist

# Install supervisor and gunicorn
RUN pip install gunicorn supervisor

# Add supervisor config
COPY supervisord.conf /etc/supervisord.conf

EXPOSE 8000 3000
CMD ["/usr/local/bin/supervisord", "-c", "/etc/supervisord.conf"]
```

#### supervisord.conf (place at project root)

```ini
[supervisord]
nodaemon=true

[program:django]
command=gunicorn Spendo.wsgi:application --bind 0.0.0.0:8000
directory=/code

default_user=root

[program:frontend]
command=python -m http.server 3000
directory=/code/client_dist
```

#### Example requirements.txt (Django backend)

```txt
Django>=4.0
djangorestframework
gunicorn
psycopg2-binary
dj-database-url
python-dotenv
django-cors-headers
```

#### Example .env (Django backend)

```env
DATABASE_URL=postgres://spendo_user:spendo_pass@db:5432/spendo_db
```

#### Example postgres.env (for local Postgres, if needed)

```env
POSTGRES_DB=spendo_db
POSTGRES_USER=spendo_user
POSTGRES_PASSWORD=spendo_pass
```

#### Example package.json (React frontend)

```json
{
    "name": "app",
    "private": true,
    "version": "0.0.0",
    "type": "module",
    "scripts": {
        "dev": "vite",
        "build": "tsc -b && vite build",
        "lint": "eslint .",
        "preview": "vite preview",
        "start": "vite preview --port $PORT"
    },
    "dependencies": {
        "react": "^19.1.0",
        "react-dom": "^19.1.0"
    },
    "devDependencies": {
        "@eslint/js": "^9.25.0",
        "@types/react": "^19.1.2",
        "@types/react-dom": "^19.1.2",
        "@vitejs/plugin-react": "^4.4.1",
        "eslint": "^9.25.0",
        "eslint-plugin-react-hooks": "^5.2.0",
        "eslint-plugin-react-refresh": "^0.4.19",
        "globals": "^16.0.0",
        "typescript": "~5.8.3",
        "typescript-eslint": "^8.30.1",
        "vite": "^6.3.5"
    }
}
```

---

This setup will:

- Build both frontend and backend.
- Serve the frontend static files from /code/client_dist (on port 3000).
- Run the Django backend with Gunicorn (on port 8000).
- Use Supervisor to run both processes in a single container.
- Load .env variables for Django if your backend is set up to do so (e.g., with python-dotenv).

You do NOT need docker-compose.yml for this single-container setup. Use this for portfolio/demo deployments where simplicity is key.

---

### ✅ Single-Container Setup: Quick Checklist & Notes

- You do NOT need separate Dockerfiles in the frontend or backend folders for this setup. The single root-level Dockerfile handles building both the frontend and backend using multi-stage builds.
- Only use nested (per-service) Dockerfiles if you want to build and run the frontend and backend as separate containers (e.g., with docker-compose).
- For this all-in-one approach:
    - The root Dockerfile builds the frontend, then the backend, then combines them in the final image.
    - Supervisor runs both the Django backend and serves the built frontend static files.
    - The frontend is served as static files by Django (not via the Vite dev server).

#### Steps to Build & Run

1. Place your `.env` file for Django in the correct directory (where `manage.py` can find it, e.g., `/code/.env` inside the container).
2. Build the Docker image:
    ```bash
    docker build -t spendo-app .
    ```
3. Run the container:
    ```bash
    docker run -p 8000:8000 spendo-app
    ```
4. Access your app at `http://localhost:8000/`.

#### Troubleshooting

- If you see `DisallowedHost` errors, ensure your `.env` contains:
    ```
    ALLOWED_HOSTS=localhost,127.0.0.1
    ```
    and rebuild the image.
- If Django crashes with `ModuleNotFoundError: No module named 'django'`, make sure the Dockerfile installs requirements in the final stage.
- If you update `.env` or dependencies, rebuild the image and restart the container.
- To debug inside the container:
    ```bash
    docker run -it spendo-app /bin/bash
    # Then run:
    python manage.py runserver 0.0.0.0:8000
    ```

---

This approach is ideal for demos and portfolios. For production or scalable deployments, use separate containers and Dockerfiles for each service with docker-compose or Kubernetes.

---

## Note for Ubuntu Users Running Inside WSL

If you are using Ubuntu inside Windows Subsystem for Linux (WSL), you may encounter issues starting the Docker daemon with `systemctl` because WSL does not use `systemd` by default. If you see an error like:

```
System has not been booted with systemd as init system (PID 1). Can't operate.
Failed to connect to bus: Host is down
```

You can start the Docker daemon manually with:

```bash
sudo dockerd
```

Leave this terminal open. In a new terminal, you can now run Docker commands, for example:

```bash
sudo docker run hello-world
```

If you want a more integrated experience, consider installing Docker Desktop for Windows and enabling WSL integration, which allows you to use Docker from within WSL without starting the daemon manually.
