# Django + React Project Creation Guide

This guide walks you through creating a modern web application using Django (Python) for the backend and React (Vite) for the frontend, organized in a monorepo structure.

---

## What is Django?

Django is a high-level web framework for building dynamic websites and web applications using Python. It follows the Model-View-Template (MVT) architectural pattern, promoting a clean separation of logic and presentation.

**Key features:**

- **Rapid Development:** Build applications quickly and efficiently.
- **Reusability:** Modular design encourages code reuse.
- **Admin Interface:** Powerful built-in admin for managing data.
- **Security:** Protection against common threats like SQL injection and XSS.
- **Scalability:** Handles high traffic and large data loads.

Django is popular for its simplicity, robustness, and strong community support.

---

## Project Folder Layout

```
├── frontend/          # React frontend (Vite)
└── backend/           # Django backend
    └── spendo/        # Django project
```

---

## 1. Implement React in Frontend

1. **Create the `frontend` directory:**
   ```bash
   mkdir frontend
   cd frontend
   ```
2. **Create a new Vite React app:**
   ```bash
   npm create vite@latest .
   ```
   - Select **React** as the framework
   - Choose **TypeScript** as the language (recommended)
   - When prompted for project name, use `.` to create in current directory

**Folder structure should now look like:**

```
├── frontend/
│   ├── public/
│   ├── src/
│   │   └── assets/
│   ├── package.json
│   ├── vite.config.ts
│   └── index.html
└── backend/
```

3. **Install required packages:**

   ```bash
   npm install
   ```

4. **Configure Vite for production builds:**

   Update `frontend/vite.config.ts` to handle production builds correctly:

   ```typescript
   import { defineConfig } from 'vite';
   import react from '@vitejs/plugin-react';
   import tailwindcss from '@tailwindcss/vite'; // Optional: if using Tailwind CSS
   import { fileURLToPath } from 'url';
   import { dirname, resolve } from 'path';

   const __filename = fileURLToPath(import.meta.url);
   const __dirname = dirname(__filename);

   export default defineConfig(({ mode }) => ({
     plugins: [react(), tailwindcss()], // Add tailwindcss() if using Tailwind
     base: mode === 'production' ? '/static/' : '/',
     resolve: {
       alias: {
         '@': resolve(__dirname, './src'),
       },
     },
   }));
   ```

   **Key points:**

   - `base: '/static/'` in production ensures assets are served from Django's static files
   - The `@` alias allows importing from `src/` using `@/components/...`

---

## 2. Run the React App

1. **Start the Vite development server:**
   ```bash
   npm run dev
   ```
2. **Open the local link** provided in the terminal to view your React app in the browser.

---

## 3. Implement Django

1. **Create the `backend` directory and move into it:**
   ```bash
   mkdir backend
   cd backend
   ```
2. **Install Django and Django REST Framework:**
   ```bash
   pip install django djangorestframework
   ```
3. **Start a new Django project:**
   ```bash
   django-admin startproject spendo .
   ```
   - The `.` at the end creates the project in the current directory
   - This creates the Django project configuration files directly in `backend/`
   - The project folder will be `backend/spendo/`

**Folder structure should now look like:**

```
├── frontend/
└── backend/
    ├── spendo/          # Django project settings
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── manage.py
    └── (other files)
```

4. **Create a Django app for your API:**

   ```bash
   python3 manage.py startapp api
   ```

   - `api` is the name of the app that will hold your backend logic.

5. **Register the app and REST framework in Django settings:**
   - Open `backend/spendo/settings.py` and update `INSTALLED_APPS`:
   ```python
   INSTALLED_APPS = [
       'django.contrib.admin',
       'django.contrib.auth',
       'django.contrib.contenttypes',
       'django.contrib.sessions',
       'django.contrib.messages',
       'django.contrib.staticfiles',
       'api',
       'rest_framework',
       'corsheaders'
   ]
   ```

---

## 4. Add Backend Requirements and Procfile

1. **Create a `requirements.txt` file in `backend/`:**
   This file lists all Python dependencies for your Django backend. Example contents:

   ```
   Django>=4.0
   djangorestframework
   gunicorn
   psycopg2-binary
   dj-database-url
   python-dotenv
   django-cors-headers
   whitenoise
   ```

   - `gunicorn` is a production-ready WSGI server for deploying Django.
   - `psycopg2-binary` and `dj-database-url` are for PostgreSQL support and environment-based configuration.
   - `python-dotenv` loads environment variables from `.env` files.
   - `django-cors-headers` handles CORS for frontend-backend communication.
   - `whitenoise` serves static files in production.

2. **Create a `Procfile` in the project root (for Heroku):**
   This tells Heroku how to run your Django app in production. Example contents:

   ```
   web: cd backend && gunicorn spendo.wsgi
   release: cd backend && python manage.py migrate
   ```

   - Note: Uses `spendo.wsgi` (lowercase) since the Django project is named `spendo`
   - The `release` command runs migrations before each deployment
   - Commands run from the `backend/` directory

3. **Create a `.python-version` file in `backend/`:**
   This specifies the Python version for deployment platforms like Heroku:
   ```
   3.11
   ```
   (or `3.12` if using Python 3.12)

---

## 5. Ensure Required Imports in Django Settings

In your `backend/spendo/settings.py`, make sure you have the following imports at the top of the file:

```python
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()
import dj_database_url
```

- `os` is required for path and environment variable handling.
- `dotenv` loads environment variables from `.env` files.
- `dj_database_url` parses database URLs from environment variables.

---

## 6. Configure Django Settings for CORS and Static Files

**Update `backend/spendo/settings.py`:**

Add CORS middleware and WhiteNoise:

```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Add this first
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For serving static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

Add CORS settings:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",
]

CORS_ALLOW_CREDENTIALS = True
```

Add CSRF trusted origins (for production):

```python
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    # Add your production domain here
]
```

Configure database (using environment variables):

```python
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=not DEBUG  # True in production, False in development
    )
}
```

Configure static files for serving frontend:

```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'spendo', 'client_dist'),
]
```

**Important:** Create the `client_dist` directory:

```bash
mkdir -p backend/spendo/client_dist
```

This directory will hold the built frontend files in production.

Configure templates to serve frontend:

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'spendo', 'client_dist')],
        'APP_DIRS': True,
        # ... rest of config
    },
]
```

---

## 7. Set Up Docker Configuration

### 7.1 Create Configuration Directory Structure

1. **Create config directory:**

   ```bash
   mkdir config
   ```

2. **Create docker directory:**
   ```bash
   mkdir docker
   ```

### 7.2 Create Docker Compose File

Create `config/docker-compose.yml`:

```yaml
services:
  frontend:
    build:
      context: ../frontend
    working_dir: /app
    ports:
      - '5173:5173' # Vite dev server
    environment:
      - NODE_ENV=development
    volumes:
      - ../frontend:/app
    command: ['npm', 'run', 'dev', '--', '--host']

  backend:
    build:
      context: ../backend
    working_dir: /code
    ports:
      - '8000:8000'
    volumes:
      - ../backend:/code
    env_file:
      - ../backend/spendo/.env
    depends_on:
      db:
        condition: service_healthy
    command: ['sh', '-c', 'python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000']

  db:
    image: postgres:16
    restart: always
    env_file:
      - ./postgres.env
    ports:
      - '5432:5432'
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -U spendo_user -d spendo_db']
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

**Key points:**

- Paths use `../` because docker-compose.yml is in `config/` directory.
- The `db` service has a `healthcheck` that ensures PostgreSQL is ready before the backend starts.
- The `backend` service uses `depends_on` with `condition: service_healthy` to wait for the database to be ready.
- This modern approach eliminates the need for a separate wait-for-it script.

### 7.3 Create Frontend Dockerfile

Create `frontend/Dockerfile`:

```dockerfile
# Frontend Dockerfile for React (Vite)
FROM node:20 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
```

### 7.4 Create Backend Dockerfile

Create `backend/Dockerfile`:

```dockerfile
# Backend Dockerfile for Django
FROM python:3.12
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /code
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .

EXPOSE 8000
```

**Note:** We no longer need `netcat-openbsd` since we're using Docker Compose health checks instead of a wait-for-it script. If your Dockerfile still has it, you can remove that line.

### 7.5 Create Production Dockerfile (Optional)

Create `docker/Dockerfile.prod`:

```dockerfile
# Multi-stage Dockerfile for portfolio deployment (frontend + backend)

# 1. Build frontend
FROM node:20 AS frontend-build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend .
RUN npm run build

# 2. Build backend
FROM python:3.12 AS backend-build
WORKDIR /code
COPY backend/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY backend .

# 3. Final stage: combine and run both
FROM python:3.12
WORKDIR /code

# Copy backend
COPY --from=backend-build /code /code

# Copy frontend build to Django static files
COPY --from=frontend-build /app/dist /code/spendo/client_dist

# Install Python dependencies in the final image
COPY backend/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install supervisor and gunicorn
RUN pip install gunicorn supervisor

# Add supervisor config
COPY config/supervisord.conf /etc/supervisord.conf

EXPOSE 8000 3000
CMD ["/usr/local/bin/supervisord", "-c", "/etc/supervisord.conf"]
```

### 7.6 Create Supervisor Configuration

Create `config/supervisord.conf`:

```ini
[supervisord]
nodaemon=true

default_user=root

[program:migrate]
command=python manage.py migrate
directory=/code
autostart=true
startsecs=0
priority=1

[program:web]
command=gunicorn spendo.wsgi:application --bind 0.0.0.0:8000
directory=/code
autostart=true
priority=2

[program:frontend]
command=python -m http.server 3000
directory=/code/spendo/client_dist
autostart=true
priority=3
```

### 7.7 Create PostgreSQL Environment File

Create `config/postgres.env`:

```
POSTGRES_DB=spendo_db
POSTGRES_USER=spendo_user
POSTGRES_PASSWORD=spendo_pass
```

Create `config/postgres.env.example` (for git):

```
POSTGRES_DB=spendo_db
POSTGRES_USER=spendo_user
POSTGRES_PASSWORD=spendo_pass
```

---

## 8. Set Up Root Level Configuration Files

### 8.1 Create Root Package.json

Create `package.json` in project root:

```json
{
  "name": "root-scripts",
  "private": true,
  "scripts": {
    "heroku-postbuild": "rm -rf backend/spendo/client_dist/* && cd frontend && npm install && npm run build && mkdir -p ../backend/spendo/client_dist && cp dist/index.html ../backend/spendo/client_dist/ && cp -r dist/assets ../backend/spendo/client_dist/"
  },
  "dependencies": {
    "prettier": "^3.5.3"
  }
}
```

### 8.2 Create Root Procfile (for Heroku)

Create `Procfile` in project root:

```
web: cd backend && gunicorn spendo.wsgi
release: cd backend && python manage.py migrate
```

### 8.3 Create Heroku Symlinks (Only if deploying to Heroku)

**Note:** This step is ONLY required if you plan to deploy to Heroku. Skip this if you're not using Heroku.

Heroku's Python buildpack looks for `requirements.txt` and `.python-version` in the root directory, but your project has them in `backend/`. Symlinks (symbolic links) create shortcuts in the root that point to the actual files:

```bash
# From project root
ln -sf backend/requirements.txt requirements.txt
ln -sf backend/.python-version .python-version
```

**What are symlinks?** They're like shortcuts - the files in the root don't contain the actual content, they just point to the files in `backend/`. When Heroku reads `requirements.txt` in the root, it actually reads `backend/requirements.txt`.

**Important:** These symlinks must be committed to git for Heroku to detect them.

**If you're NOT deploying to Heroku:** You can skip this step entirely.

### 8.4 Create .gitignore

Create `.gitignore` in project root:

```
**/node_modules/
**/.env
config/postgres.env
**/venv/
**/lib/
**/bin/
**/lib64
**/pyvenv.cfg

# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules
dist
dist-ssr
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?
```

### 8.5 Create Environment File Examples

Create `backend/spendo/.env.example`:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://spendo_user:spendo_pass@localhost:5432/spendo_db
OPENAI_API_KEY=your-openai-api-key
```

Create `frontend/.env.example`:

```
VITE_API_URL=http://localhost:8000
```

---

## 9. Configure Django URLs for Frontend Serving

Update `backend/spendo/urls.py`:

```python
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', TemplateView.as_view(template_name="index.html")),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls'))
]

# Serve static files (React build output) in production
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Catch-all route for React (must be last)
urlpatterns += [
    re_path(r'^(?!static/|api/|admin/).*$', TemplateView.as_view(template_name="index.html")),
]
```

---

## 10. Database Health Checks (Modern Approach)

**Note:** The wait-for-it script is **not necessary** when using Docker Compose health checks. The `docker-compose.yml` file above uses a modern approach with:

1. **Health check on the database service:**

   ```yaml
   healthcheck:
     test: ['CMD-SHELL', 'pg_isready -U spendo_user -d spendo_db']
     interval: 5s
     timeout: 5s
     retries: 5
   ```

2. **Conditional dependency in the backend:**
   ```yaml
   depends_on:
     db:
       condition: service_healthy
   ```

This ensures the backend only starts after the database is ready to accept connections. This is cleaner and more reliable than using a separate wait-for-it script.

**Benefits of this approach:**

- No need for additional scripts or dependencies
- Built into Docker Compose (v2.1+)
- More reliable and easier to maintain
- Automatically retries until the database is ready

**Alternative (if you prefer wait-for-it script):**
If you're using an older version of Docker Compose that doesn't support health checks, you can use a wait-for-it script. However, Docker Compose v2.1+ (released in 2021) supports health checks, so this is the recommended approach.

---

## 11. Complete Project Structure

Your final project structure should look like:

```
Spendo/
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── pages/
│   │   │   ├── HomePage/
│   │   │   └── AuthenticationPage/
│   │   ├── components/
│   │   ├── contexts/
│   │   ├── api/
│   │   └── assets/
│   ├── public/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   └── .env.example
│
├── backend/                    # Django backend
│   ├── spendo/                # Django project
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   ├── asgi.py
│   │   ├── .env
│   │   └── .env.example
│   ├── api/                   # Django app
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── migrations/
│   ├── manage.py
│   ├── requirements.txt
│   ├── Procfile
│   ├── Dockerfile
│   └── .python-version
│
├── config/                     # Configuration files
│   ├── docker-compose.yml
│   ├── supervisord.conf
│   ├── postgres.env
│   └── postgres.env.example
│
├── docker/                     # Docker deployment files
│   └── Dockerfile.prod
│
├── docs/                       # Documentation
│   ├── DEPLOYMENT.md
│   └── docker_overview.md
│
├── scripts/                    # Utility scripts
│   ├── setup.sh
│   ├── deploy.sh
│   ├── heroku.sh
│   └── reset-db.sh
│
├── Procfile                    # Root Procfile (for Heroku)
├── package.json                # Root package.json (for heroku-postbuild)
├── requirements.txt            # Symlink to backend/requirements.txt (Heroku only)
├── .python-version             # Symlink to backend/.python-version (Heroku only)
├── .gitignore
└── README.md
```

---

## 12. Testing the Setup

### 12.1 Test Local Development

1. **Start Docker services:**

   ```bash
   docker compose -f config/docker-compose.yml up --build
   ```

2. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - Django Admin: http://localhost:8000/admin

### 12.2 Test Backend Locally (without Docker)

1. **Set up Python virtual environment:**

   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run migrations:**

   ```bash
   python manage.py migrate
   ```

3. **Create superuser:**

   ```bash
   python manage.py createsuperuser
   ```

4. **Run development server:**
   ```bash
   python manage.py runserver
   ```

### 12.3 Test Frontend Locally (without Docker)

1. **Install dependencies:**

   ```bash
   cd frontend
   npm install
   ```

2. **Run development server:**
   ```bash
   npm run dev
   ```

---

## 13. Deployment Preparation

### 13.1 Heroku Deployment Setup

**Note:** The following steps are ONLY needed for Heroku deployment. If you're deploying elsewhere (AWS, DigitalOcean, etc.), you won't need these symlinks.

1. **Create symlinks (required for Heroku):**

   Heroku's Python buildpack looks for `requirements.txt` and `.python-version` in the root directory. Since your project has them in `backend/`, create symlinks:

   ```bash
   # From project root
   ln -sf backend/requirements.txt requirements.txt
   ln -sf backend/.python-version .python-version
   ```

   **What are symlinks?** They're shortcuts that point to another file. When Heroku reads `requirements.txt` in the root, it actually reads `backend/requirements.txt`.

2. **Commit symlinks to git:**

   ```bash
   git add requirements.txt .python-version
   git commit -m "Add Heroku symlinks"
   ```

3. **Configure Heroku buildpacks:**
   ```bash
   heroku buildpacks:clear -a your-app-name
   heroku buildpacks:add heroku/nodejs -a your-app-name
   heroku buildpacks:add heroku/python -a your-app-name
   ```

See `docs/DEPLOYMENT.md` for complete Heroku deployment instructions.

---

## 14. Next Steps

1. **Set up environment variables** in `.env` files
2. **Configure database** connection in Django settings
3. **Create API endpoints** in `backend/api/`
4. **Build frontend components** in `frontend/src/`
5. **Set up authentication** (if needed)
6. **Configure CORS** for your frontend domain
7. **Test the full stack** locally with Docker
8. **Deploy to production** (see `docs/DEPLOYMENT.md`)

---

You now have a complete Django + React project scaffolded with Docker support, ready for development and deployment!
