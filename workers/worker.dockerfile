# FROM python:3.9-alpine3.14
FROM python:3.7.6-buster

# COPY DEPENDENCY FILE
COPY workers/requirements.txt /requirements.txt

# UPGRADE PIP & INSTALL PYTHON DEPENDENCIES
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# GO INTO WORKDIR & RUN WORKER
WORKDIR /workers
CMD ["python3", "launcher.py"]