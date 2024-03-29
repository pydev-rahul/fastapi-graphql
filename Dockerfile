# Pull base image
FROM python:3.9

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code/

# Install dependencies
RUN pip install pipenv
COPY Pipfile Pipfile.lock /code/
RUN pipenv install --system --dev
RUN pip3 install bcrypt && pip3 install passlib
# RUN pip3 install pyjwt
RUN pip3 install python-multipart && pip3 install python-jose[cryptography]
RUN pip3 install pymongo 
COPY . /code/

EXPOSE 8000