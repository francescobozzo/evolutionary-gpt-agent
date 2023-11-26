from typing import Optional  # required due to a typer lib limitation

import tiktoken
from typer import Typer

from models.db.models import Experiment
from models.db_handler import DatabaseHandler

app = Typer()

_GPT_4_8K_CONTEXT_1000_INPUT_TOKENS_COST = 0.029
_GPT_4_8K_CONTEXT_1000_OUTPUT_TOKENS_COST = 0.057


@app.command(short_help="Exeperiment name.")
def estimate(experiment_name: Optional[str] = None) -> None:
    db_handler = DatabaseHandler()

    experiments: list[Experiment] = []
    if experiment_name:
        experiments = [db_handler.get_experiment_by_name(experiment_name)]
    else:
        experiments = db_handler.get_all_experiments()

    encoder = tiktoken.encoding_for_model("gpt-4")

    input_tokens = 0
    output_tokens = 0
    n_perceivers = 0
    n_plans = 0
    perceivers_tokens = {
        "input": 0,
        "output": 0,
    }
    plans_tokens = {
        "input": 0,
        "output": 0,
    }

    for experiment in experiments:
        n_perceivers += len(experiment.perceivers)
        n_plans += len(experiment.plans)

        current_plan_input_tokens = sum(
            [len(encoder.encode(p.prompt)) for p in experiment.plans]
        )
        current_plan_output_tokens = sum(
            [len(encoder.encode(p.code)) for p in experiment.plans]
        )
        current_perceiver_input_tokens = sum(
            [len(encoder.encode(p.prompt)) for p in experiment.perceivers]
        )
        current_perceiver_output_tokens = sum(
            [len(encoder.encode(p.code)) for p in experiment.perceivers]
        )

        input_tokens += current_plan_input_tokens + current_perceiver_input_tokens
        output_tokens += current_plan_output_tokens + current_perceiver_output_tokens
        plans_tokens["input"] += current_plan_input_tokens
        plans_tokens["output"] += current_plan_output_tokens
        perceivers_tokens["input"] += current_perceiver_input_tokens
        perceivers_tokens["output"] += current_perceiver_output_tokens

    print(f"Estimated costs for {len(experiments)} experiments")
    print(f"\t{n_perceivers} perceivers")
    print(
        "\t\tinput tokens:"
        f" {perceivers_tokens['input']/1000*_GPT_4_8K_CONTEXT_1000_INPUT_TOKENS_COST}"
    )
    print(
        "\t\toutput tokens:"
        f" {perceivers_tokens['output']/1000*_GPT_4_8K_CONTEXT_1000_OUTPUT_TOKENS_COST}"
    )
    print(f"\t{n_plans} plans")
    print(
        "\t\tinput tokens:"
        f" {plans_tokens['input']/1000*_GPT_4_8K_CONTEXT_1000_INPUT_TOKENS_COST}"
    )
    print(
        "\t\toutput tokens:"
        f" {plans_tokens['output']/1000*_GPT_4_8K_CONTEXT_1000_OUTPUT_TOKENS_COST}"
    )
    print(
        "\tTOTAL:\n"
        f"\t\t{input_tokens} input tokens:"
        f" {input_tokens/1000*_GPT_4_8K_CONTEXT_1000_INPUT_TOKENS_COST}\n",
        f"\t\t{output_tokens} output tokens:"
        f" {output_tokens/1000*_GPT_4_8K_CONTEXT_1000_OUTPUT_TOKENS_COST}\n",
        f"\t\ttotal:"
        f""" {
        input_tokens/1000*_GPT_4_8K_CONTEXT_1000_INPUT_TOKENS_COST +
        output_tokens/1000*_GPT_4_8K_CONTEXT_1000_OUTPUT_TOKENS_COST
        }\n""",
    )


def main() -> None:
    app()
