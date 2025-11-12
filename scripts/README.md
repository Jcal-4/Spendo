# Scripts Directory

This directory contains utility scripts to help with development and deployment.

## Available Scripts

### `setup.sh`
Setup script for new developers. This script:
- Checks for required tools (Docker, Node.js, Python)
- Sets up environment files from examples
- Optionally installs dependencies
- Provides next steps for getting started

**Usage:**
```bash
./scripts/setup.sh
```

### `deploy.sh`
Deployment script for building production Docker images.

**Usage:**
```bash
./scripts/deploy.sh
```

### `reset-db.sh`
Database reset script that drops and recreates the database, then runs migrations.

**Usage:**
```bash
./scripts/reset-db.sh
```

**Warning:** This will delete all database data!

### `heroku.sh`
Heroku deployment and management script. Provides easy commands for common Heroku tasks.

**Usage:**
```bash
./scripts/heroku.sh [command] [app-name]
```

**Available Commands:**
- `deploy [app]` - Deploy to Heroku (builds and pushes)
- `logs [app]` - View last 100 lines of logs
- `tail [app]` - View live logs (follow mode, real-time)
- `logs-tail [app]` - Alias for tail (view live logs)
- `migrate [app]` - Run database migrations
- `shell [app]` - Open Heroku bash shell
- `console [app]` - Open Django shell
- `superuser [app]` - Create Django superuser
- `restart [app]` - Restart Heroku dynos
- `status [app]` - Check app status
- `open [app]` - Open app in browser
- `config [app]` - Show environment variables
- `set-env [app]` - Set environment variable (interactive)
- `psql [app]` - Open PostgreSQL console
- `backup [app]` - Create database backup
- `restore [app]` - Restore database from backup

**Examples:**
```bash
# Deploy to Heroku
./scripts/heroku.sh deploy spendo-app

# View live logs (follow mode)
./scripts/heroku.sh tail spendo-app

# View last 100 lines of logs
./scripts/heroku.sh logs spendo-app

# Run migrations
./scripts/heroku.sh migrate spendo-app

# Create superuser
./scripts/heroku.sh superuser spendo-app
```

**Note:** If you have a Heroku git remote configured, you can omit the app name.

## Adding New Scripts

Feel free to add more utility scripts here, such as:
- `test.sh` - Test runners
- `lint.sh` - Linting scripts
- `backup-db.sh` - Database backup scripts
- etc.

Make sure to:
1. Add `#!/bin/bash` at the top
2. Make scripts executable: `chmod +x scripts/your-script.sh`
3. Update this README with documentation

