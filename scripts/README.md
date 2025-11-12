# Scripts Directory

This directory contains utility scripts for Heroku deployment and management.

## Available Scripts

### `heroku.sh`
Heroku deployment and management script. Provides easy commands for common Heroku tasks.

**Usage:**
```bash
./scripts/heroku.sh [command] [app-name]
```

**Available Commands:**
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

### `fix-heroku-buildpacks.sh`
Quick script to fix Heroku buildpack configuration by removing problematic monorepo buildpacks and setting up standard buildpacks.

**Usage:**
```bash
./scripts/fix-heroku-buildpacks.sh [app-name]
```

**What it does:**
- Clears all buildpacks
- Removes any monorepo buildpacks
- Adds `heroku/nodejs` and `heroku/python` buildpacks
- Removes `BUILD_SUBDIR` config if it exists
- Verifies the final buildpack configuration

**When to use:**
- First time setting up Heroku deployment
- After changing project structure
- If you get "server/Spendo not found" errors

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

