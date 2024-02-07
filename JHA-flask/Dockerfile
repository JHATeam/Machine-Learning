FROM python:3.12-alpine

# RUN apt-get update -y
# RUN apt-get install -y python-pip

# copy over our requirements.txt file
COPY requirements.txt /tmp/

# upgrade pip and install required python packages
RUN pip install -U pip
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# fix encoding issues
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# making stdout unbuffered (any non empty string works)
ENV PYTHONUNBUFFERED="thisistheway"

# copy over our app code
COPY ./app /app
COPY ./database /database

# set the expose port
EXPOSE 8080
