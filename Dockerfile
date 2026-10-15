FROM python:3.13-slim
RUN apt-get update && apt-get install -y --no-install-recommends libsdl2-2.0-0 libasound2 fonts-dejavu-core && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY pin_simulator.py .
COPY assets/ assets/
CMD ["python", "pin_simulator.py"]
