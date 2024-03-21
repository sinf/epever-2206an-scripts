#/bin/sh
podman run --name epever -d --restart=on-failure:5 -v ./config:/app/config:ro localhost/epever

