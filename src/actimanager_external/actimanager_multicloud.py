import structlog

import heatspreader
import heatspreader.exceptions

SCALE_CHANGE = 0.01

log = structlog.getLogger(__name__)


class ActimanagerMulticloud:
    def __init__(self, config):
        self._cloud = config.cloud
        self._offload_cloud = config.offload_cloud
        self._stack_name = config.heat_spreader_stack_name

        self._heat_spreader = heatspreader.Client(config.heat_spreader)

    async def close(self):
        log.debug("heat_spreader_close")
        await self._heat_spreader.close()

    async def offload(self):
        try:
            multicloud_stack = await self._heat_spreader.get(self._stack_name)
        except heatspreader.exceptions.MulticloudStackNotFound as exc:
            log.error("actimanager_multicloud_missing_stack", error=str(exc))
            return

        cloud_weight = multicloud_stack.weights[self._cloud]
        cloud_weight = cloud_weight - SCALE_CHANGE
        if cloud_weight < 0.0:
            log.warning("actimanager_multicloud_cloud_weight_zero")
            cloud_weight = 0.0
            offload_cloud_weight = 1.0
        else:
            offload_cloud_weight = multicloud_stack.weights[
                self._offload_cloud
            ]
            offload_cloud_weight = offload_cloud_weight + SCALE_CHANGE

        try:
            log.info("heat_spreader_update_start")

            await self._heat_spreader.weight_set(
                self._stack_name, self._cloud, cloud_weight
            )
            await self._heat_spreader.weight_set(
                self._stack_name, self._offload_cloud, offload_cloud_weight
            )
            log.info("heat_spreader_update_end")
        except heatspreader.exceptions.ValidationError as exc:
            log.error("heat_spreader_validation_error", error=str(exc))
        except heatspreader.exceptions.BackendException as exc:
            log.error("heatspreader_backend_error", error=str(exc))
