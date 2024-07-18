FROM python:3.9-slim

# Set working directory
WORKDIR /code

# Copy requirements file and install dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --upgrade -r /code/requirements.txt

# Copy application code
COPY ./app /code/app

# Set the command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
