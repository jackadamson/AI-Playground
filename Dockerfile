# pull official base image
FROM python:3.8.0-alpine
RUN apk add --no-cache openssl-dev libffi-dev python3-dev gcc musl-dev
# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
COPY ./requirements-broker.txt /usr/src/app/requirements-broker.txt
RUN pip install -r requirements-broker.txt

# copy project
COPY aiplayground /usr/src/app/aiplayground
EXPOSE 8000
CMD ["gunicorn", "--worker-class", "eventlet", "-b", ":8000", "-w", "1", "aiplayground._app:app"]
