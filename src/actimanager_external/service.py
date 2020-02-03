import asyncio
import signal

import structlog

from .actimanager_external import ActimanagerExternal

log = structlog.getLogger(__name__)

SIGNALS_STOP = [signal.SIGINT, signal.SIGTERM]


class Service:
    def __init__(self, config):
        self._loop = asyncio.get_event_loop()

        self._running = False

        self._actimanager_external = ActimanagerExternal(config)

    async def stop(self):
        log.info("service_stop")
        self._running = False

    async def force_stop(self):
        log.info("service_force_stop")

        tasks = [
            t for t in asyncio.all_tasks() if t is not asyncio.current_task()
        ]

        for task in tasks:
            task.cancel()

    def _force_stop_signal_handler(self):
        asyncio.ensure_future(self.force_stop())

    def _signal_handler(self, s):
        _log = log.bind(signal=s.name)

        _log.debug("service_caught_signal")

        if s in SIGNALS_STOP:
            for s in SIGNALS_STOP:
                self._loop.remove_signal_handler(s)

            asyncio.ensure_future(self.stop())

            self._loop.add_signal_handler(
                signal.SIGINT, self._force_stop_signal_handler
            )

            print("Interrupt to force stop")
        else:
            _log.error("service_unhandled_signal")

    async def run(self):
        log.info("service_run")

        self._running = True

        for s in SIGNALS_STOP:
            asyncio.get_event_loop().add_signal_handler(
                s, self._signal_handler, s
            )

        await self._actimanager_external.start()

        while True:
            if not self._running:
                break

            await self._actimanager_external.recv_msg()

            asyncio.create_task(self._actimanager_external.decide())

            await asyncio.sleep(1)

        await self._actimanager_external.stop()
