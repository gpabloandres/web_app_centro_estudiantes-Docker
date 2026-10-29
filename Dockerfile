FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN useradd --create-home --uid 10001 appuser \
	&& mkdir -p /data \
	&& chown -R appuser:appuser /app /data

USER appuser

EXPOSE 5000

CMD ["sh", "-c", "flask --app 'app:create_app' init-db && exec gunicorn --bind 0.0.0.0:5000 --workers 2 'app:create_app()'"]
