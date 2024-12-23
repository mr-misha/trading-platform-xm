# Dockerfile for App Server
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /trading_app

# Copy the requirements file
COPY Pipfile Pipfile.lock ./

# Install pipenv
RUN pip install --no-cache-dir pipenv

# Install the dependencies
RUN pipenv install --system --deploy

# Copy the application files
COPY trading_app ./trading_app

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/trading_app

# Expose the port the app runs on
EXPOSE 8000

# Command to run fastapi server application
CMD ["fastapi", "dev", "./trading_app/trading_api_server.py"]
