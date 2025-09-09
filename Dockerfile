FROM python:3.11-slim AS builder
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app

ENV PATH=/root/.local/bin:$PATH
COPY --from=builder /root/.local /root/.local
COPY . .

EXPOSE 8000
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "config.wsgi"]