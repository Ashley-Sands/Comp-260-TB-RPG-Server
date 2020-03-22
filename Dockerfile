# test_server:0.1.4
######################
FROM python:3.7.7-alpine3.11

WORKDIR /usr/src/app

ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app"

COPY py_requirements.txt ./
RUN pip install --no-cache-dir -r py_requirements.txt

COPY ./Test/test_server.py ./TEST/TEST
COPY ./Common/ ./Common/

CMD [ "python", "-u", "./Test/test_server.py" ]