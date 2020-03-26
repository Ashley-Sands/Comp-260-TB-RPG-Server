# SERVER SELECTOR
# server_selector.0.1.8
######################

FROM python:3.7.7-alpine3.11

WORKDIR /usr/src/app

ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app"

EXPOSE 8222

COPY py_requirements.txt ./
RUN pip install --no-cache-dir -r py_requirements.txt

COPY ./server_selector.py ./
COPY ./Common/ ./Common/
COPY ./Sockets/ ./Sockets/

CMD [ "python", "-u", "./server_selector.py" ]