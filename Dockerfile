FROM python:3.12-slim AS build
WORKDIR /app
COPY . .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements/production.txt
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DJANGO_SETTINGS_MODULE=config.settings.production
RUN useradd --create-home --uid 10001 sentra
WORKDIR /app
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels
COPY --chown=sentra:sentra . .
USER sentra
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/qr/health')"
CMD ["gunicorn","config.wsgi:application","--bind","0.0.0.0:8000","--workers","3","--timeout","30","--graceful-timeout","20","--access-logfile","-"]
