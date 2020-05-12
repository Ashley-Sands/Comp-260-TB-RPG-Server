# Server Info and Status
# server_info:0.1
######################

FROM python:3.7.7-alpine3.11

WORKDIR /usr/src/app

ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app"

COPY ./server_socket_info_status.py ./

CMD [ "python", "-u", "./server_socket_info_status.py" ]
