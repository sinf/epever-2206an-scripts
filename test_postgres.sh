#!/bin/sh
podman run \
--rm \
-p 127.0.0.1:7000:5432/tcp \
-e POSTGRES_PASSWORD=633f396d212b1229b6ce \
-e PGDATA=/var/lib/postgresql/data/pgdata \
--pull=missing \
--name=postgres_testing \
postgres:16.2-alpine3.19

# sqlalchemy: "postgresql+psycopg2://postgres:633f396d212b1229b6ce@127.0.0.1:7000/testing"

