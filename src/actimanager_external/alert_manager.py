import time

import structlog

log = structlog.getLogger(__name__)


def _alert_manager_refresh(f):
    def wrapper(self, *args):
        now = time.time()
        for alert in self._alerts.copy():
            if (now - alert.time) > self._alert_window:
                log.info(
                    "alert_manager_outside_window",
                    now=now,
                    alert_time=alert.time,
                    hostname=alert.hostname,
                )
                self._alerts.remove(alert)
        return f(self, *args)

    return wrapper


class AlertManager:
    class _Alert:
        def __init__(self, hostname):
            self.hostname = hostname
            self.time = time.time()

        def __eq__(self, other):
            return self.hostname == other.hostname

        def __hash__(self):
            return hash(self.hostname)

    def __init__(self, config):
        self._alert_window = config.alert_window

        self._alerts = set()

    def add(self, hostname):
        alert = AlertManager._Alert(hostname)

        log.info(
            "alert_manager_alert",
            alert_time=alert.time,
            hostname=alert.hostname,
        )

        try:
            self._alerts.remove(alert)
        except KeyError:
            pass
        self._alerts.add(alert)

    @_alert_manager_refresh
    def get(self):
        return self._alerts
