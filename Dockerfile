FROM python:3.9

EXPOSE 5000

WORKDIR /home/app
COPY . .
RUN pip install .

CMD [ "temperatur_server" ]
