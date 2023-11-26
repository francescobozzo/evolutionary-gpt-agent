from typing import Optional  # required due to a typer lib limitation

import tiktoken
from typer import Typer

from models.db.models import Experiment
from models.db_handler import DatabaseHandler

app = Typer()

_GPT_4_8K_CONTEXT_1000_TOKENS_COST = 0.029


@app.command(short_help="Exeperiment name.")
def estimate(experiment_name: Optional[str] = None) -> None:
    db_handler = DatabaseHandler()

    experiments: list[Experiment] = []
    if experiment_name:
        experiments = [db_handler.get_experiment_by_name(experiment_name)]
    else:
        experiments = db_handler.get_all_experiments()

    encoder = tiktoken.encoding_for_model("gpt-4")

    tokens = 0
    n_perceivers = 0
    n_plans = 0
    perceivers_tokens = 0
    plans_tokens = 0

    for experiment in experiments:
        n_perceivers += len(experiment.perceivers)
        n_plans += len(experiment.plans)

        current_plan_tokens = sum(
            [len(encoder.encode(p.prompt)) for p in experiment.plans]
        )
        current_perceiver_tokens = sum(
            [len(encoder.encode(p.prompt)) for p in experiment.perceivers]
        )

        tokens += current_plan_tokens + current_perceiver_tokens
        perceivers_tokens += current_perceiver_tokens
        plans_tokens += current_plan_tokens

    print(f"Estimated costs for {len(experiments)} experiments")
    print(
        f"\t{n_perceivers} perceivers with {perceivers_tokens}"
        f" tokens: {perceivers_tokens/1000*_GPT_4_8K_CONTEXT_1000_TOKENS_COST}"
    )
    print(
        f"\t{n_plans} plans with {plans_tokens} tokens:"
        f" {plans_tokens/1000*_GPT_4_8K_CONTEXT_1000_TOKENS_COST}"
    )
    print(
        f"\tTOTAL, {tokens} tokens:"
        f" {plans_tokens/1000*_GPT_4_8K_CONTEXT_1000_TOKENS_COST}"
    )


def main() -> None:
    app()
