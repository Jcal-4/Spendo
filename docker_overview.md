# Docker Overview

Docker is a platform that allows you to package, distribute, and run applications in lightweight, portable containers. Here’s a high-level overview of how Docker works:

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

## General Guide: Setting Up Docker

### 1. Install Docker

- Go to [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/) and download Docker Desktop (Windows/Mac) or follow the instructions for Linux.
- Follow the installation steps for your operating system.
- After installation, verify by running `docker --version` in your terminal.

### 2. Create a Dockerfile

- In your project root, create a file named `Dockerfile` (no extension).
- Add instructions to set up your environment. Example for a Node.js app:
    ```Dockerfile
    FROM node:20
    WORKDIR /app
    COPY package*.json ./
    RUN npm install
    COPY . .
    CMD ["npm", "start"]
    ```
- For Python, use a base image like `python:3.12` and adjust accordingly.

### 3. Build the Docker Image

- In your project directory, run:
    ```bash
    docker build -t your-image-name .
    ```
- This creates an image using your Dockerfile.

### 4. Run a Container

- Start your app in a container:
    ```bash
    docker run -p 3000:3000 your-image-name
    ```
- Adjust the port as needed for your app.

### 5. (Optional) Share Your Image

- Push your image to Docker Hub or another registry:
    ```bash
    docker tag your-image-name your-dockerhub-username/your-image-name
    docker push your-dockerhub-username/your-image-name
    ```

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

---

This guide helps you set up Docker for most projects. Adjust the Dockerfile for your specific language or framework. If you need a sample Dockerfile for your project, let me know!
