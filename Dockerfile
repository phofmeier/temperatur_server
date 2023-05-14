FROM python:3.9

EXPOSE 5000

WORKDIR /home/app
COPY . .
RUN pip install .

CMD [ "python", "src/temperatur_server/main.py" ]
