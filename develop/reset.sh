#!/usr/bin/env bash

source "$(dirname ${BASH_SOURCE[0]})/utils.sh"

# ensure ">>> killing existing services" docker-compose kill db user_server role_server region_server consul
ensure ">>> stop existing services" docker-compose stop
ensure ">>> removing existing services" docker-compose rm -f -v

if [ -n "${BUILD}" ]
then
    ensure "building services" docker-compose build
fi

if [ -n "${PULL}" ]
then
    ensure "pulling images" docker-compose pull
fi

PGDATABASE=postgres
export PGDATABASE
ensure ">>> starting db/consul/zipkin" docker-compose up --remove-orphans -d db consul zipkin
waituntil 10 ">>> connect postgres" docker-compose exec db pg_isready
# user_server must start after role/region_server
ensure ">>> starting services" docker-compose up -d
ensure ">>> create tables" docker-compose run --rm user_server python -m migrations
docker-compose run --rm role_server python -m migrations
docker-compose run --rm region_server python -m migrations

# create testing data
# curl -X POST "http://localhost:8020/roles" -H  "accept: application/json" -H  "content-type: application/json" -d "{  \"name\": \"admin\"}"
# curl -X POST "http://localhost:8030/users" -H  "accept: application/json" -H  "content-type: application/json" -d "{\"name\": \"Kevinqqnj\",\"age\":11,\"role_id\":1}"
