FROM python:3.11-slim

WORKDIR /app
COPY shared/requirements.txt .
RUN pip install -r requirements.txt

COPY worker /app/worker

CMD ["python", "worker/worker.py"]
