FROM python:3.9
ENV PYTHONBUFFERED=1
WORKDIR /usr/src/organize-application/scheduler_project
COPY requirements.txt ./
RUN pip uninstall django
RUN pip install -r requirements.txt
