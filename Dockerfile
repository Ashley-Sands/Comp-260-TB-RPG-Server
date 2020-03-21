FROM python:3.7.7-alpine3.11

WORKDIR /usr/src/app

ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app"

COPY py_requirements.txt ./
RUN pip install --no-cache-dir -r py_requirements.txt

COPY . .

CMD [ "python", "-u", "./Test/test_server.py" ]