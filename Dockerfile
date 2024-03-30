FROM alpine:3.19.1 # Jan 27, 2024
RUN apk add python3
RUN apk add py-pip
RUN rm -rf /var/cache/apk

WORKDIR /app
COPY LICENSE .

COPY requirements.txt .
RUN python -m venv ./venv \
&& . ./venv/bin/activate \
&& pip install -r requirements.txt --no-cache

COPY epever-modbus-client.md .
COPY config/epever-modbus-client-config.json.template .
COPY docker-entrypoint.sh .
COPY ./modbus_thing ./modbus_thing

ENTRYPOINT ["/app/docker-entrypoint.sh"]

