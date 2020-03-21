FROM python:3.7.7

WORKDIR /usr/src/app

COPY py_requirements.txt ./
RUN pip install --no-cache-dir -r py_requirements.txt

COPY . .

CMD [ "python", "-u", "./selector_main.py" ]