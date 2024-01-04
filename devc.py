import time
from os import getcwd
from typing import Optional  # required due to a typer lib limitation
from typing import Callable

from dotenv import dotenv_values
from python_on_whales import DockerClient
from typer import Typer

app = Typer()
config = dotenv_values(".env")
docker = DockerClient(
    compose_files=["./docker-compose.yml"],
    client_call=[config["CONTAINER_ENGINE"] or "docker"],
)


def spin_db() -> tuple[bool, Callable[[], None]]:
    container = docker.compose.ps(["db"])

    if len(container) > 0 and container[0].state.status == "running":
        return True, lambda: None
    else:
        docker.compose.build()
        docker.compose.up(services="db", detach=True)
        time.sleep(2)

        return False, lambda: docker.compose.down()


@app.command(short_help="Generate a new database migration.")
def new_migration(name: str) -> None:
    docker.compose.build()
    docker.compose.up(services="db", detach=True)

    time.sleep(2)
    docker.run(
        image="evolutionary-gpt-agent-agent",
        remove=True,
        volumes=[
            (
                getcwd() + "/src/data_model",
                "/evolutionary_gpt_agent/src/data_model",
            )
        ],
        envs=config,
        networks=["evolutionary-gpt-agent_default"],
        workdir="/evolutionary_gpt_agent/src/data_model/db",
        command=["alembic", "revision", "--autogenerate", "-m", name],
    )

    docker.compose.down(remove_orphans=True)


@app.command(short_help="Apply last newest migration.")
def upgrade() -> None:
    docker.compose.build()
    docker.compose.up(services="db", detach=True)

    time.sleep(2)
    docker.compose.run(
        service="agent",
        remove=True,
        workdir="/evolutionary_gpt_agent/src/data_model/db",
        command=["alembic", "upgrade", "head"],
    )

    docker.compose.down(remove_orphans=True)


@app.command(short_help="Undo last migration.")
def downgrade() -> None:
    docker.compose.build()
    docker.compose.up(services="db", detach=True)

    time.sleep(2)
    docker.compose.run(
        service="agent",
        remove=True,
        workdir="/evolutionary_gpt_agent/src/data_model/db",
        command=["alembic", "downgrade", "-1"],
    )

    docker.compose.down(remove_orphans=True)


@app.command(short_help="Enter inside the db container and run psql.")
def psql() -> None:
    _, close_fn = spin_db()

    docker.compose.execute(
        "db",
        ["psql", "-U", config["POSTGRES_USER"], "-d", config["POSTGRES_DB"]],
        user="postgres",
        tty=True,
    )

    close_fn()


@app.command(short_help="Delete all rows inside every postgreSQL table.")
def psql_erase() -> None:
    _, close_fn = spin_db()

    docker.compose.execute(
        "db",
        [
            "psql",
            "-U",
            config["POSTGRES_USER"],
            "-d",
            config["POSTGRES_DB"],
            "-c",
            (
                "TRUNCATE perceivers, events, experiments, checkpoints,"
                " belief_sets, prompt_templates CASCADE;"
            ),
        ],
        user="postgres",
        tty=True,
    )

    close_fn()


@app.command(short_help="Inspect database visually.")
def agent_pov() -> None:
    docker.compose.build()
    docker.compose.up(
        services=[
            "db",
            "agent_pov_server",
            # "agent_pov",
        ]
    )


@app.command(short_help="Agent dev entrypoint.")
def agent_dev() -> None:
    _, close_fn = spin_db()

    docker.compose.run("agent", tty=True, build=True, command=["agent-dev"])

    close_fn()


@app.command(short_help="Gpt estimation costs.")
def gpt_estimate_costs(experiment_name: Optional[str] = None) -> None:
    _, close_fn = spin_db()

    if experiment_name:
        docker.compose.run(
            "agent",
            tty=True,
            build=True,
            command=["gpt-estimate-costs", "--experiment-name", experiment_name],
        )
    else:
        docker.compose.run(
            "agent", tty=True, build=True, command=["gpt-estimate-costs"]
        )

    close_fn()


if __name__ == "__main__":
    app()
