FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p data output/reports data/vectors
EXPOSE 5000
CMD ["python", "app.py"]
