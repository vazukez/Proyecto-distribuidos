FROM python:3.10-slim

WORKDIR /app

# Copia requerimientos e instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el script
COPY generator.py .

# Comando por defecto: se puede sobreescribir con argumentos
CMD ["python", "generator.py"]
