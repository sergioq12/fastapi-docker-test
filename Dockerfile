# set python image version
FROM python:3.12

# set working directory
WORKDIR /code

# copy the requirements file
COPY ./requirements.txt /code/requirements.txt

# run the requirements install of dependencies
RUN pip install --no-cache-dir -r /code/requirements.txt

# copy the app folder into the working directory
COPY ./app /code/app

# run the last command to make the app to run
CMD ["uvicorn", "app.index:app", "--host", "0.0.0.0", "--port", "8080"]