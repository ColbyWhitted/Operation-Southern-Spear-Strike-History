# OSS Strike History

A Django application with PostgreSQL, containerized using Docker.

## Setup

1. Clone the repository.
2. Copy `backend/.env.example` to `backend/.env` and fill in the values:
   - Generate a SECRET_KEY: `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`
   - Set a secure DB_PASSWORD and POSTGRES_PASSWORD (use the same value).
   - Set ALLOWED_HOSTS for production (e.g., your domain).
3. Run `docker compose up --build -d` (or `docker compose -f docker-compose.yml` if using older Docker).
4. Run migrations: `docker compose exec web python manage.py migrate`
5. Create a superuser: `docker compose exec web python manage.py createsuperuser`
6. Access the app at http://localhost:8000 and admin at http://localhost:8000/admin/

## Security Notes

- Never commit `.env` to the repository.
- Use strong, unique passwords for the database.
- Set DEBUG=0 and proper ALLOWED_HOSTS for production.
- For production deployment, use a WSGI server like Gunicorn instead of `runserver`.

## Development

- The app runs in development mode with DEBUG=1.
- Database data persists in a Docker volume.
