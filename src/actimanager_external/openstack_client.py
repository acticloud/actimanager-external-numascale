import asyncio
import concurrent.futures
import openstack
import structlog


log = structlog.getLogger(__name__)

executor = concurrent.futures.ThreadPoolExecutor()


def run_in_executor(f):
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(executor, lambda: f(*args, **kwargs))

    return wrapper


class OpenstackClient:
    def __init__(self, config):
        self.cloud_name = config.cloud

        self._log = log.bind(cloud_name=self.cloud_name)

    def connect(self):
        self._connection = openstack.connect(cloud=self.cloud_name)

        self._log.info("openstack_connection_open")

        self._compute = self._connection.compute

    def _do_migration(self, server):
        _log = self._log.bind(server_name=server.name)

        _log.info("openstack_migration_start")

        self._compute.migrate_server(server)

        _log.debug("openstack_migration_wait")

        try:
            self._compute.wait_for_server(
                server, status="VERIFY_RESIZE", wait=300
            )
        except openstack.exceptions.ResourceTimeout:
            _log.error("openstack_migration_timeout")

        _log.debug("openstack_migration_confirm")

        self._compute.confirm_server_resize(server)

        _log.info("openstack_migration_success")

    @run_in_executor
    def migrate(self, server_group_name, host):
        _log = self._log.bind(server_group_name=server_group_name, host=host)

        server_group = self._compute.find_server_group(server_group_name)
        if not server_group:
            _log.error("openstack_migrate_server_group_not_found")
            return

        servers = self._compute.servers()
        for server in servers:
            if (
                server.id in server_group.member_ids
                and server.compute_host == host
            ):
                self._do_migration(server)
                return

        _log.warning("openstack_migrate_no_candidate_found")

    def close(self):
        self._connection.close()

        self._log.info("openstack_connection_closed")
