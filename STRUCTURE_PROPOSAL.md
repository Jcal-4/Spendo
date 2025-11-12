# Proposed Project Structure

## Current Issues

1. **Backend**: Confusing nested `server/Spendo/Spendo/` structure
2. **Frontend**: `client/app/` is reasonable but could be clearer
3. **Configuration files**: Scattered in root directory
4. **Docker files**: Multiple Dockerfiles in different locations

## Proposed Structure

```
Spendo/
├── README.md
├── .gitignore
├── .prettierrc
│
├── backend/                          # Renamed from server/Spendo
│   ├── manage.py
│   ├── requirements.txt
│   ├── Procfile
│   ├── Dockerfile                    # Backend-specific Dockerfile
│   │
│   ├── spendo/                       # Django project (renamed from nested Spendo/Spendo)
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   ├── asgi.py
│   │   ├── wait-for-it.sh
│   │   ├── .env.example
│   │   └── .env                      # Local env (gitignored)
│   │
│   ├── api/                          # Django app
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializer.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── tests.py
│   │   ├── chatkit_server.py
│   │   ├── memory_store.py
│   │   │
│   │   ├── migrations
│   │   │   ├── __init__.py
│   │   │   └── *.py
│   │   │
│   │   ├── management/
│   │   │   └── commands/
│   │   │       ├── __init__.py
│   │   │       ├── generate_fake_data.py
│   │   │       ├── truncate_all_tables.py
│   │   │       └── delete_migrations.py
│   │   │
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── openai_service.py     # Renamed (lowercase)
│   │       └── user_service.py
│   │
│   └── staticfiles/                  # Django collectstatic output (gitignored)
│
├── frontend/                         # Renamed from client/app
│   ├── package.json
│   ├── package-lock.json
│   ├── Dockerfile
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tsconfig.app.json
│   ├── tsconfig.node.json
│   ├── tailwind.config.js
│   ├── postcss.config.cjs
│   ├── eslint.config.js
│   │
│   ├── public/
│   │   └── vite.svg
│   │
│   ├── src/
│   │   ├── main.tsx
│   │   ├── index.css
│   │   ├── vite-env.d.ts
│   │   │
│   │   ├── api/
│   │   │   └── auth.ts
│   │   │
│   │   ├── assets/
│   │   │   └── login-background.png
│   │   │
│   │   ├── components/
│   │   │   ├── chatbot/
│   │   │   ├── footer/
│   │   │   ├── header-menu/
│   │   │   ├── navbar/
│   │   │   ├── theme-toggle/
│   │   │   ├── ui/
│   │   │   ├── user-info-icons/
│   │   │   └── ProtectedRoute.tsx
│   │   │
│   │   ├── contexts/
│   │   │   ├── AuthContext.ts
│   │   │   ├── AuthContext.tsx
│   │   │   └── useAuth.ts
│   │   │
│   │   ├── pages/                    # Renamed from Homepage/authentication-page
│   │   │   ├── HomePage/
│   │   │   │   ├── HomePage.tsx
│   │   │   │   ├── HomePage.css
│   │   │   │   ├── components/       # Page-specific components
│   │   │   │   │   ├── features-cards/
│   │   │   │   │   ├── hero-section/
│   │   │   │   │   └── home-grid/
│   │   │   │   └── ...
│   │   │   └── AuthenticationPage/
│   │   │       ├── AuthenticationPage.tsx
│   │   │       └── AuthenticationPage.module.css
│   │   │
│   │   └── ... (other source files)
│   │
│   └── dist/                         # Build output (gitignored)
│
├── config/                           # NEW: Centralized configuration
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml      # Production compose file (optional)
│   ├── supervisord.conf
│   ├── postgres.env.example
│   └── .env.example                 # Root level env examplecd
│
├── docker/                           # NEW: Docker deployment files
│   ├── Dockerfile.prod              # Production Dockerfile (moved from root)
│   └── .dockerignore
│
├── docs/                             # NEW: Documentation
│   ├── CHATKIT_INTEGRATION_GUIDE.md
│   └── docker_overview.md
│
├── scripts/                          # NEW: Utility scripts (optional)
│   └── setup.sh                     # Setup script for new developers
│
└── node_modules/                     # Root node_modules (gitignored)
```

## Key Changes Explained

### 1. Backend Structure

- **`server/Spendo` → `backend/`**: Clearer naming convention
- **`server/Spendo/Spendo/` → `backend/spendo/`**: Flattened Django project structure
- **Benefits**: No confusion about nested directories, easier navigation

### 2. Frontend Structure

- **`client/app` → `frontend/`**: Removes unnecessary nesting
- **`Homepage/` → `pages/HomePage/`**: Standard naming for page components
- **`authentication-page/` → `pages/AuthenticationPage/`**: Consistent casing and location
- **Benefits**: Follows React conventions, easier to find pages

### 3. Configuration Organization

- **`config/` folder**: All Docker, database, and service configs in one place
- **Benefits**: Easy to find all configuration files, better for deployment

### 4. Documentation

- **`docs/` folder**: All markdown documentation files
- **Benefits**: Keeps root directory clean, easy to find documentation

### 5. Docker Files

- **`docker/` folder**: Production deployment files
- **Benefits**: Separates development and production Docker configs

## Files That Need Path Updates

After reorganization, these files will need path updates:

1. `docker-compose.yml` - Update all paths to use new structure
2. `package.json` (root) - Update heroku-postbuild script paths
3. `Dockerfile` (root) - Update COPY paths if keeping at root, or move to docker/
4. `supervisord.conf` - Update paths if references exist
5. Any import statements that use absolute paths

## Migration Steps

1. Create new directory structure
2. Move files to new locations
3. Update all configuration files with new paths
4. Update import statements (if any use absolute paths)
5. Test that everything still works
6. Update documentation

## Benefits Summary

✅ **Clearer naming**: `backend/` and `frontend/` are industry standard  
✅ **No confusion**: Removed nested Spendo/Spendo structure  
✅ **Better organization**: Config, docs, and deployment files grouped  
✅ **Easier navigation**: Everything has a logical place  
✅ **Scalability**: Easy to add more configs, docs, or services  
✅ **Team-friendly**: New developers can understand structure quickly
