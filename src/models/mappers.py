from datetime import datetime

from models.api import Event as ApiEvent
from models.db.models import Event as DbEvent
from models.db.models import Experiment


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
    )
