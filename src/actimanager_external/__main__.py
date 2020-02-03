import asyncio
import logging
import os

import heatspreader

from .config import Config, RabbitMQConfig
from .log import setup_logging
from .service import Service


async def run(config):
    service = Service(config)
    await service.run()


def main():
    setup_logging(log_level=logging.INFO)

    config = Config(
        # Cloud settings
        cloud=os.environ["ACTIMANAGER_EXTERNAL_CLOUD"],
        offload_cloud=os.environ["ACTIMANAGER_EXTERNAL_OFFLOAD_CLOUD"],
        host_count=os.environ["ACTIMANAGER_EXTERNAL_HOST_COUNT"],
        server_group=os.environ["ACTIMANAGER_EXTERNAL_SERVER_GROUP"],
        # ACTiManager External settings
        offload_threshold=os.environ["ACTIMANAGER_EXTERNAL_OFFLOAD_THRESHOLD"],
        alert_window=os.environ["ACTIMANAGER_EXTERNAL_ALERT_WINDOW"],
        decision_cooldown=os.environ["ACTIMANAGER_EXTERNAL_DECISION_COOLDOWN"],
        # RabbitMQ settings
        rabbitmq_config=RabbitMQConfig(
            host=os.environ["ACTIMANAGER_EXTERNAL_RABBITMQ_HOST"],
            port=os.environ["ACTIMANAGER_EXTERNAL_RABBITMQ_PORT"],
            username=os.environ["ACTIMANAGER_EXTERNAL_RABBITMQ_USERNAME"],
            password=os.environ["ACTIMANAGER_EXTERNAL_RABBITMQ_PASSWORD"],
            queue_name=os.environ["ACTIMANAGER_EXTERNAL_RABBITMQ_QUEUE"],
        ),
        # Heat Spreader settings
        heat_spreader_config=heatspreader.RemoteBackendConfig(
            host=os.environ["ACTIMANAGER_EXTERNAL_HEAT_SPREADER_HOST"],
            port=os.environ["ACTIMANAGER_EXTERNAL_HEAT_SPREADER_PORT"],
        ),
        heat_spreader_stack_name=os.environ[
            "ACTIMANAGER_EXTERNAL_HEAT_SPREADER_STACK_NAME"
        ],
    )

    asyncio.run(run(config))


if __name__ == "__main__":
    main()
