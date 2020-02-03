from enum import auto, Enum

import structlog

log = structlog.getLogger(__name__)


class Decision(Enum):
    OFFLOAD = auto()
    MIGRATE = auto()
    NOTHING = auto()


class DecisionMaker:
    def __init__(self, config, alert_manager):
        self._host_count = config.host_count
        self._offload_threshold = config.offload_threshold

        self._alert_manager = alert_manager

    def decision(self):
        alerts = self._alert_manager.get()

        alert_count = len(alerts)

        alert_amount = float(alert_count) / float(self._host_count)

        log.info(
            "decision_maker_decision",
            host_count=self._host_count,
            alert_count=alert_count,
            alert_amount=alert_amount,
            offload_threshold=self._offload_threshold,
        )

        if alert_amount > self._offload_threshold:
            return Decision.OFFLOAD
        elif alert_count > 0:
            return Decision.MIGRATE
        else:
            return Decision.NOTHING
