# 1. Start with Python 3.12
FROM python:3.12-slim

# 2. Set the working directory
WORKDIR /app

# 3. Copy requirements first
COPY requirements.txt .

# 4. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the application code
COPY . .

# 6. Start Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]