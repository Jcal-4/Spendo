# Spendo Project: Local Development with Docker Compose

This guide explains how to set up your local development environment using Docker and Docker Compose.

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
    docker compose up --build
    ```
4. **To run Django management commands inside the backend container:**
    ```bash
    docker compose exec backend python manage.py makemigrations
    docker compose exec backend python manage.py migrate
    ```

---

## Example docker-compose.yml

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
        command:
            [
                'sh',
                '-c',
                'chmod +x /wait-for-it.sh && /wait-for-it.sh db 5432 python manage.py migrate && python manage.py generate_fake_data && python manage.py runserver 0.0.0.0:8000',
            ]

    db:
        image: postgres:16
        restart: always
        env_file:
            - ./postgres.env
        ports:
            - '5432:5432'
        volumes:
            - postgres_data:/var/lib/postgresql/data

volumes:
    postgres_data:
```

---

## Example Dockerfiles

### Frontend (`client/app/Dockerfile`)

```dockerfile
FROM node:20
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
CMD ["npm", "run", "dev", "--", "--host"]
```

### Backend (`server/Spendo/Dockerfile`)

```dockerfile
FROM python:3.12
WORKDIR /code
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

---

## Environment Files

- `postgres.env` (for the database)
- `server/Spendo/Spendo/.env` (for Django backend)
- `client/app/.env` (for frontend)

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

For more details, see `docker_overview.md` in the project root.
