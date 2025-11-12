# Deployment Guide

This guide covers deployment to Heroku and other platforms.

## Table of Contents

- [Heroku Deployment](#heroku-deployment)
  - [Prerequisites](#prerequisites)
  - [Initial Setup](#initial-setup)
  - [Buildpack Configuration](#buildpack-configuration)
  - [Important Files for Heroku](#important-files-for-heroku)
  - [Environment Variables](#environment-variables)
  - [Deployment Process](#deployment-process)
  - [Post-Deployment Steps](#post-deployment-steps)
  - [How the Build Process Works](#how-the-build-process-works)
  - [Common Heroku Commands](#common-heroku-commands)
- [Project Structure for Deployment](#project-structure-for-deployment)
  - [Root Directory Files (Required for Heroku)](#root-directory-files-required-for-heroku)
  - [Why Symlinks?](#why-symlinks)
- [Troubleshooting](#troubleshooting)
  - [Buildpack Detection Issues](#buildpack-detection-issues)
  - [Monorepo Buildpack Errors](#monorepo-buildpack-errors)
  - [Frontend Not Building](#frontend-not-building)
  - [Database Migration Issues](#database-migration-issues)
  - [Static Files Not Serving](#static-files-not-serving)
- [Additional Resources](#additional-resources)

---

## Heroku Deployment

### Prerequisites

1. **Heroku CLI** installed ([Installation Guide](https://devcenter.heroku.com/articles/heroku-cli))
2. **Git** repository initialized
3. **Heroku account** and app created

### Initial Setup

1. **Login to Heroku:**

   ```bash
   heroku login
   ```

2. **Create Heroku app (if not already created):**

   ```bash
   heroku create your-app-name
   ```

3. **Add Heroku git remote:**
   ```bash
   heroku git:remote -a your-app-name
   ```

### Buildpack Configuration

This project uses a **monorepo structure** with both frontend (Node.js) and backend (Python). Heroku requires specific buildpack configuration:

**Required Buildpacks (in order):**

1. `heroku/nodejs` - For building the frontend
2. `heroku/python` - For running the Django backend

**Configure buildpacks (first time only):**

```bash
heroku buildpacks:clear -a your-app-name
heroku buildpacks:add heroku/nodejs -a your-app-name
heroku buildpacks:add heroku/python -a your-app-name
```

### Important Files for Heroku

The following files are required in the **root directory** for Heroku detection:

- **`Procfile`** - Defines how to run the app

  ```
  web: cd backend && gunicorn spendo.wsgi
  release: cd backend && python manage.py migrate
  ```

- **`requirements.txt`** - Symlink to `backend/requirements.txt`

  - Created as: `ln -sf backend/requirements.txt requirements.txt`
  - Required for Python buildpack detection

- **`.python-version`** - Symlink to `backend/.python-version`

  - Created as: `ln -sf backend/.python-version .python-version`
  - Specifies Python version (3.11)

- **`package.json`** - Contains `heroku-postbuild` script

  - Builds frontend and copies to `backend/spendo/client_dist/`

- **`app.json`** - Optional, defines buildpack configuration

### Environment Variables

Set required environment variables on Heroku:

```bash
# Django settings
heroku config:set SECRET_KEY=your-secret-key -a your-app-name
heroku config:set DEBUG=False -a your-app-name
heroku config:set ALLOWED_HOSTS=your-app.herokuapp.com,localhost -a your-app-name

# Database (if using Heroku Postgres)
heroku config:set DATABASE_URL=$(heroku config:get DATABASE_URL -a your-app-name) -a your-app-name

# OpenAI API (if using ChatKit)
heroku config:set OPENAI_API_KEY=your-api-key -a your-app-name

# Other required variables
heroku config:set VITE_API_URL=https://your-app.herokuapp.com -a your-app-name
```

### Deployment Process

**Deploy by pushing to Heroku:**

```bash
# Push to Heroku (this triggers the build)
git push heroku main
# or
git push heroku master
```

That's it! Heroku will automatically:

1. Build the frontend using the Node.js buildpack
2. Build the backend using the Python buildpack
3. Run migrations (via the `release` command in Procfile)
4. Start your app

### Post-Deployment Steps

Migrations run automatically via the `release` command in your Procfile. If you need to run them manually:

```bash
heroku run python manage.py migrate -a your-app-name
```

**Other useful commands:**

```bash
# Create superuser
heroku run python manage.py createsuperuser -a your-app-name

# View logs
heroku logs --tail -a your-app-name

# Open app in browser
heroku open -a your-app-name

# View environment variables
heroku config -a your-app-name
```

### How the Build Process Works

1. **Node.js Buildpack:**

   - Detects `package.json` in root
   - Installs Node.js dependencies
   - Runs `heroku-postbuild` script:
     - Builds frontend with Vite
     - Copies built files to `backend/spendo/client_dist/`

2. **Python Buildpack:**

   - Detects `requirements.txt` (symlink) in root
   - Detects `.python-version` (symlink) in root
   - Installs Python dependencies
   - Prepares Django app

3. **Runtime:**
   - `Procfile` runs: `cd backend && gunicorn spendo.wsgi`
   - Django serves both API and frontend static files

### Common Heroku Commands

```bash
# View logs (live)
heroku logs --tail -a your-app-name

# View last 100 lines
heroku logs --num 100 -a your-app-name

# Check app status
heroku ps -a your-app-name

# Restart dynos
heroku restart -a your-app-name

# Open Django shell
heroku run python manage.py shell -a your-app-name

# Database backup (if using Heroku Postgres)
heroku pg:backups:capture -a your-app-name
```

---

## Project Structure for Deployment

### Root Directory Files (Required for Heroku)

```
Spendo/
├── Procfile                    # Heroku process definition
├── requirements.txt            # Symlink to backend/requirements.txt
├── .python-version             # Symlink to backend/.python-version
├── package.json                # Contains heroku-postbuild script
├── app.json                    # Optional: buildpack configuration
└── backend/
    ├── requirements.txt        # Actual Python dependencies
    ├── .python-version         # Actual Python version file
    ├── Procfile                # Not used (root Procfile takes precedence)
    └── spendo/
        └── client_dist/        # Frontend build output (created during build)
```

### Why Symlinks?

Heroku's Python buildpack requires `requirements.txt` and `.python-version` in the **root directory** for detection. Since our project uses a monorepo structure with the backend in `backend/`, we use symlinks to satisfy this requirement while keeping the actual files in their proper location.

**Important:** These symlinks must be committed to git for Heroku to see them.

---

## Troubleshooting

### Buildpack Detection Issues

**Error:** "App not compatible with buildpack: heroku/python"

**Solution:**

- Ensure `requirements.txt` symlink exists in root: `ln -sf backend/requirements.txt requirements.txt`
- Ensure `.python-version` symlink exists: `ln -sf backend/.python-version .python-version`
- Commit symlinks to git: `git add requirements.txt .python-version && git commit -m "Add Heroku symlinks"`

### Monorepo Buildpack Errors

**Error:** "mv: cannot stat '/tmp/build\_\*/server/Spendo': No such file or directory"

**Solution:**

- Remove any monorepo buildpacks:
  ```bash
  heroku buildpacks:clear -a your-app-name
  heroku buildpacks:add heroku/nodejs -a your-app-name
  heroku buildpacks:add heroku/python -a your-app-name
  ```

### Frontend Not Building

**Error:** Frontend assets not found after deployment

**Solution:**

- Check `heroku-postbuild` script in `package.json`
- Verify paths in the script match your structure
- Check build logs: `heroku logs --tail -a your-app-name`

### Database Migration Issues

**Error:** Database migrations fail

**Solution:**

- Run migrations manually: `heroku run python manage.py migrate -a your-app-name`
- Check database connection: `heroku config:get DATABASE_URL -a your-app-name`
- Verify Heroku Postgres addon is attached

### Static Files Not Serving

**Error:** Frontend not loading, 404 errors

**Solution:**

- Verify `backend/spendo/client_dist/` exists after build
- Check `STATICFILES_DIRS` in `backend/spendo/settings.py`
- Ensure WhiteNoise middleware is enabled
- Run `collectstatic`: `heroku run python manage.py collectstatic --noinput -a your-app-name`

---

## Additional Resources

- [Heroku Python Support](https://devcenter.heroku.com/articles/python-support)
- [Heroku Node.js Support](https://devcenter.heroku.com/articles/nodejs-support)
- [Heroku Buildpacks](https://devcenter.heroku.com/articles/buildpacks)
