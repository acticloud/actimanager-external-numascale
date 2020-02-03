class RabbitMQConfig:
    def __init__(self, host, port, username, password, queue_name):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.queue_name = queue_name


class Config:
    def __init__(
        self,
        cloud,
        offload_cloud,
        server_group,
        host_count,
        alert_window,
        decision_cooldown,
        offload_threshold,
        rabbitmq_config,
        heat_spreader_config,
        heat_spreader_stack_name,
    ):
        self.cloud = cloud
        self.offload_cloud = offload_cloud
        self.host_count = int(host_count)
        self.server_group = server_group

        self.alert_window = int(alert_window)
        self.decision_cooldown = int(decision_cooldown)
        self.offload_threshold = float(offload_threshold)

        self.rabbitmq = rabbitmq_config

        self.heat_spreader = heat_spreader_config
        self.heat_spreader_stack_name = heat_spreader_stack_name
