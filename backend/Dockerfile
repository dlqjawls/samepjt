# 
FROM python:3.9

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir -r /code/requirements.txt

# 
COPY ./app /code/app

# 
CMD ["uvicorn", "app.main:create_app", "--host", "0.0.0.0", "--port", "8000"]