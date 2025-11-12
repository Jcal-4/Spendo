#!/bin/bash
# Quick script to fix Heroku buildpacks by removing monorepo buildpack

APP_NAME="${1:-spendo}"

echo "Fixing Heroku buildpacks for: $APP_NAME"
echo ""

echo "1. Clearing all buildpacks..."
heroku buildpacks:clear -a "$APP_NAME"

echo ""
echo "2. Removing any monorepo buildpacks..."
heroku buildpacks:remove https://github.com/lstoll/heroku-buildpack-monorepo.git -a "$APP_NAME" 2>/dev/null || echo "  (not found, skipping)"
heroku buildpacks:remove https://github.com/croaky/heroku-buildpack-monorepo.git -a "$APP_NAME" 2>/dev/null || echo "  (not found, skipping)"

echo ""
echo "3. Adding standard buildpacks..."
heroku buildpacks:add heroku/nodejs -a "$APP_NAME"
heroku buildpacks:add heroku/python -a "$APP_NAME"

echo ""
echo "4. Removing BUILD_SUBDIR config (if exists)..."
heroku config:unset BUILD_SUBDIR -a "$APP_NAME" 2>/dev/null || echo "  (not set, skipping)"

echo ""
echo "5. Verifying buildpacks..."
heroku buildpacks -a "$APP_NAME"

echo ""
echo "✅ Buildpacks fixed! You can now deploy with:"
echo "   git push heroku main"
echo "   or"
echo "   ./scripts/heroku.sh deploy $APP_NAME"
