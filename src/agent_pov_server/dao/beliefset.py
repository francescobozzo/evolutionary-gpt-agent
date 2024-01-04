from os import getenv
from typing import Any

from loguru import logger
from sqlalchemy.orm import Session

from data_model.db.models import BeliefSet
from evolutionary_gpt_agent.components.bdi.tester import CodeTester
from evolutionary_gpt_agent.components.gpt_client import Client


def get_beliefset(db: Session, beliefset_id: int) -> BeliefSet | Any:
    db_beliefset = (
        db.query(BeliefSet).filter(BeliefSet.belief_set_id == beliefset_id).first()
    )
    return db_beliefset


def get_beliefsets_by_experiment(db: Session, experiment_id: int) -> list[BeliefSet]:
    db_beliefsets: list[BeliefSet] = (
        db.query(BeliefSet).filter(BeliefSet.experiment_id == experiment_id).all()
    )
    return db_beliefsets


def generate_beliefset_representation(
    db: Session,
    beliefset: BeliefSet,
) -> None:
    openai_api_key = getenv("OPENAI_API_KEY")
    openai_api_base = getenv("OPENAI_API_BASE")
    openai_api_type = getenv("OPENAI_API_TYPE")
    openai_api_version = getenv("OPENAI_API_VERSION")
    openai_deployment = getenv("OPENAI_DEPLOYMENT")
    openai_model = getenv("OPENAI_MODEL")

    if (
        not openai_api_key
        or not openai_api_base
        or not openai_api_type
        or not openai_api_version
        or not openai_deployment
        or not openai_model
    ):
        raise Exception("missing value in the .env config file, see .env.sample")

    gpt_client = Client(
        openai_api_key,
        openai_api_base,
        openai_api_type,
        openai_api_version,
        openai_deployment,
        openai_model,
        "",
    )
    logger.info("gpt client defined")
    is_generator_valid = False
    while not is_generator_valid:
        logger.info(
            f"asking for a new representation for belief set {beliefset.belief_set_id}"
        )

        function_name = "bf_representation_generator"
        generator_code = gpt_client.ask_belief_set_represenation_generator(
            function_name, beliefset.data
        )
        generator = CodeTester(
            generator_code,
            function_name,
        )

        if generator.is_valid(belief_set=beliefset.data):
            is_generator_valid = True

    logger.info(f"representation geneated for belief set {beliefset.belief_set_id}")

    _save_beliefset_representation(db, beliefset, generator(belief_set=beliefset.data))


def _save_beliefset_representation(
    db: Session, beliefset: BeliefSet, represenation: bytes
) -> None:
    beliefset.representation = represenation
    db.add(beliefset)
    db.commit()
    db.flush()
    logger.info(
        f"representation inserted in the db for belief set {beliefset.belief_set_id}"
    )
