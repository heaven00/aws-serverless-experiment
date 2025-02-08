# Use the official Python image from the Docker Hub
FROM public.ecr.aws/lambda/python:3.11

# Copy function code and requirements
COPY app.py ${LAMBDA_TASK_ROOT}
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install dependencies
RUN pip install -r requirements.txt

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD ["app.valid_transaction"]
