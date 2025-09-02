# Backend Dockerfile for Django
FROM python:3.12
RUN apt-get update && apt-get install -y netcat-openbsd
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /code
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .

EXPOSE 8000

# Run migrations and then start the server
CMD ["sh", "-c", "python manage.py migrate && gunicorn Spendo.wsgi:application --bind 0.0.0.0:8000"]
