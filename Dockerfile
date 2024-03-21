FROM alpine
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
COPY epever-modbus-client.py .
COPY docker-entrypoint.sh .

ENTRYPOINT ["/bin/sh", "/app/docker-entrypoint.sh"]

