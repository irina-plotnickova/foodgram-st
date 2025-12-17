FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

CMD sh -c "python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000"