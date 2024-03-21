#/bin/sh
podman build -t localhost/epever .
#podman run --name epever -d --restart=on-failure:5 -v ./config:/app/config:ro localhost/epever
podman run --rm --name epever -v ./config:/app/config:ro localhost/epever

