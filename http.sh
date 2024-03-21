#/bin/sh
podman build -t localhost/epever .
podman run --rm -it --network=host --name epeverHttp -v ./config:/app/config:ro localhost/epever -c /app/config/only-http.json

