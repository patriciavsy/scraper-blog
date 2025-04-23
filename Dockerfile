FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Instalación de dependencias necesarias para el navegador y el driver

# Instalar Chromium
RUN apt-get update && apt-get install -y chromium

# Instalar WebDriver Manager (asegúrate de que se esté descargando correctamente el chromedriver)
RUN pip install webdriver-manager


EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]