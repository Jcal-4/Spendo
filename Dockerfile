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

# Install Python dependencies in the final image
COPY server/Spendo/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install supervisor and gunicorn
RUN pip install gunicorn supervisor

# Add supervisor config
COPY supervisord.conf /etc/supervisord.conf

EXPOSE 8000 3000
CMD ["/usr/local/bin/supervisord", "-c", "/etc/supervisord.conf"]


