#!/usr/bin/env bash

source "$(dirname ${BASH_SOURCE[0]})/utils.sh"

ensure ">>> killing existing services" docker-compose kill db user_server role_server region_server
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
ensure ">>> starting db" docker-compose up -d db
waituntil 10 ">>> connect postgres" docker-compose exec db pg_isready
ensure ">>> starting services" docker-compose up -d
ensure ">>> create tables" docker-compose run --rm user_server python -m migrations
docker-compose run --rm role_server python -m migrations
docker-compose run --rm region_server python -m migrations
