# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create user to avoid running as root (important for Huggingface Spaces)
RUN useradd -m -u 1000 user

# Set work directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY --chown=user:user . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Ensure the app directory is owned by the user
RUN chown -R user:user /app

# Switch to the non-root user
USER user

# Hugging Face Spaces expose port 7860
EXPOSE 7860

# Command to run the application using Gunicorn
# Command to run the application using Gunicorn and run migrations
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:7860 config.wsgi:application"]
