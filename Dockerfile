# HTTP Analytics
# version 1
######################

FROM python:3.7.7-alpine3.11

EXPOSE 80
WORKDIR /usr/src/app

ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app"

COPY py_requirements.txt ./
RUN pip install --no-cache-dir -r py_requirements.txt

COPY ./HTTP_Analytics ./HTTP_Analytics
COPY ./Common/ ./Common/
COPY ./logs/log.txt ./logs/log.txt


CMD [ "python", "-u", "./HTTP_Analytics/main_server.py" ]
