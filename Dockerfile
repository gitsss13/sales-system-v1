FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV PORT=3000
ENV APP_VERSION=v1

EXPOSE 3000

CMD ["python", "app.py"]