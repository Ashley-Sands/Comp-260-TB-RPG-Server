FROM python:3.7.7-alpine3.11

WORKDIR /usr/src/app

EXPOSE 8222

COPY py_requirements.txt ./
RUN pip install --no-cache-dir -r py_requirements.txt

COPY . .

CMD [ "python", "-u", "./selector_main.py" ]