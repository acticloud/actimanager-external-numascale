import time

import structlog

from .actimanager_multicloud import ActimanagerMulticloud
from .alert_manager import AlertManager
from .decision_maker import Decision, DecisionMaker
from .message_queue import MessageQueue
from .openstack_client import OpenstackClient

log = structlog.getLogger(__name__)


class ActimanagerExternal:
    def __init__(self, config):
        self._decision_cooldown = config.decision_cooldown
        self._last_decision_time = 0
        self._server_group = config.server_group
        self._message_queue = MessageQueue(config)
        self._actimanager_multicloud = ActimanagerMulticloud(config)
        self._openstack = OpenstackClient(config)
        self._alert_manager = AlertManager(config)
        self._decision_maker = DecisionMaker(config, self._alert_manager)

    async def start(self):
        await self._message_queue.connect()
        self._openstack.connect()

    async def stop(self):
        await self._message_queue.close()
        await self._actimanager_multicloud.close()
        self._openstack.close()

    async def migrate(self):
        alerts = self._alert_manager.get()
        if not len(alerts):
            log.debug("actimanager_external_migrate_skip")
            return

        alert = alerts.pop()

        await self._openstack.migrate(self._server_group, alert.hostname)

    async def recv_msg(self):
        msg = await self._message_queue.recv()
        if msg:
            self._alert_manager.add(msg["hostname"])

    async def decide(self):
        if time.time() - self._last_decision_time < self._decision_cooldown:
            log.debug("actimanager_external_decide_cooldown")
            return

        self._last_decision_time = time.time()

        log.info("actimanager_external_decide_start")

        decision = self._decision_maker.decision()
        _log = log.bind(decision=decision.name)
        _log.info("actimanager_external_decision")

        if decision is Decision.OFFLOAD:
            await self._actimanager_multicloud.offload()
        elif decision is Decision.MIGRATE:
            await self.migrate()
        elif decision is Decision.NOTHING:
            pass

        _log.info("actimanager_external_decide_end")
