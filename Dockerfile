FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY basic_server.py .
COPY web_server.py .
COPY static/ static/

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "web_server:app", "--host", "0.0.0.0", "--port", "8000"]
