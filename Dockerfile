FROM python:3

EXPOSE 5000

WORKDIR /home/app
COPY . .
RUN pip install -e .

CMD [ "temperatur_server" ]
