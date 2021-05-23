FROM arm64v8/ubuntu

ENV TZ = "UTC"

RUN apt-get update -y && \
    apt-get install -y cron python3-pip python3-dev

COPY ./web/requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY web .
RUN cp ./static/ca/traefik.home.lab-ca.crt /usr/local/share/ca-certificates && update-ca-certificates

#RUN mv ./db/test123.db /tmp/prod1.db
#RUN ls -la /tmp

ENTRYPOINT [ "/bin/python3" ]

CMD [ "app.py" ]
