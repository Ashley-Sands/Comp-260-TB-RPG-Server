# GAME_SERVER
# server_game.0.1.0
######################

FROM python:3.7.7-alpine3.11

WORKDIR /usr/src/app

ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app"

COPY py_requirements.txt ./
RUN pip install --no-cache-dir -r py_requirements.txt

COPY ./server_game.py ./
COPY ./Common/ ./Common/
COPY ./Sockets/ ./Sockets/
COPY ./logs/log.txt ./logs/log.txt
COPY ./Components/ ./Components/

CMD [ "python", "-u", "./server_game.py" ]