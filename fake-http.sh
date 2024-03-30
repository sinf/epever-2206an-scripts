#/bin/sh
set -e
podman build -t localhost/epever .
#podman run --rm -it --network=host --name epeverHttp -v ./config:/app/config:ro localhost/epever -c /app/config/only-http.json
podman run --rm --replace -it -p 127.0.0.1:8000:8000 --name epeverHttp -v ./config:/app/config:ro localhost/epever -c /app/config/fake.json

