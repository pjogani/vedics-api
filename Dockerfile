FROM python:3.12.4-slim as base

FROM base as builder
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir --target=packages -r requirements.txt

FROM base as runtime
COPY --from=builder /app/packages /usr/lib/python3.12/site-packages
ENV PYTHONPATH=/usr/lib/python3.12/site-packages

# Create and switch to a non-root user for security
RUN useradd -m nonroot
USER nonroot

WORKDIR /app
COPY . .

EXPOSE 8000
CMD gunicorn --bind 0.0.0.0:8000 --access-logfile - core.wsgi:application