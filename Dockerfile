FROM python:3.10.12

# Create a non-root user
RUN useradd -m -u 1000 user

# Set up the working directory
WORKDIR /app

# Copy the requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the application
COPY . .

# Create and set permissions for the cache directory
RUN mkdir /.cache && chown -R user:user /.cache && chmod -R 777 /.cache

# Switch to the non-root user
USER user

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]