#!/bin/bash

helpMessage="usage $0:\n\tnew_migration [message]\n\tupgrade\n\tdowngrade\n\tenter_db\n"
[ -z $1 ] && echo -e $helpMessage && exit 1
set -e

function build_and_run_db() {
    docker-compose build
    docker-compose up -d db

    sleep 2
}

function stop_db() {
    docker-compose down
}

if [[ $1 == "new_migration" ]]; then
    shift

    [ -z $1 ] && echo $helpMessage && exit 1
    build_and_run_db
    docker-compose run \
                   --rm \
                   -v $(pwd)/src/models:/evolutionary_gpt_agent/src/models \
                   -w /evolutionary_gpt_agent/src/models \
                   agent \
                   alembic revision --autogenerate -m "$1"
    stop_db
elif [[ $1 == "upgrade" ]]; then
    build_and_run_db
    docker-compose run \
                   --rm \
                   -v $(pwd)/src/models:/evolutionary_gpt_agent/src/models \
                   -w /evolutionary_gpt_agent/src/models \
                   agent \
                   alembic upgrade head
    stop_db
elif [[ $1 == "downgrade" ]]; then
    build_and_run_db
    docker-compose run \
                   --rm \
                   -v $(pwd)/src/models:/evolutionary_gpt_agent/src/models \
                   -w /evolutionary_gpt_agent/src/models \
                   agent \
                   alembic downgrade -1
    stop_db
elif [[ $1 == "enter_db" ]]; then
    source .env
    build_and_run_db
    docker-compose exec -u postgres -it db psql -U $POSTGRES_USER -d $POSTGRES_DB
    stop_db
fi

exit 0
