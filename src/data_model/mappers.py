from datetime import datetime

from data_model.api import Event as ApiEvent
from data_model.db.models import Event as DbEvent
from data_model.db.models import Experiment


def api_event_to_db_event(
    apiEvent: ApiEvent, experiment: Experiment, parentEvent: DbEvent | None
) -> DbEvent:
    return DbEvent(
        received_date=datetime.fromtimestamp(apiEvent.received_date),
        parent=parentEvent,
        experiment=experiment,
        origin=apiEvent.origin,
        description=apiEvent.description,
        data=apiEvent.data,
        game_dump=apiEvent.game_dump,
    )


def db_event_to_api_event(db_event: DbEvent) -> ApiEvent:
    return ApiEvent(
        description=db_event.description,
        origin=db_event.origin,
        data=db_event.data,
        game_dump=db_event.game_dump,
        received_date=0,
    )
