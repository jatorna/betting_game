FROM python:3.7.3
WORKDIR /usr/src/app
COPY requirements.txt .
ENV PYTHONPATH .
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip && pip3 install -r requirements.txt
