# FastAPI için base image
FROM python:3.9-slim

# Çalışma dizini oluşturma
WORKDIR /app

# Gereksinimleri yükleme
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulamayı kopyalama
COPY . .

# Uvicorn ile çalıştırma
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
