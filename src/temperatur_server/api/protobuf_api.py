""" Implementation for an api via Protobuf messages.
"""

import flask_socketio
from temperature_proto.proto.settings_pb2 import Settings

from database.database import MeasurementDB
from temperatur_server.server_state import ServerState


class ProtobufApi(flask_socketio.Namespace):
    def __init__(
        self, server_state: ServerState, database: MeasurementDB, namespace: str = "/pb"
    ) -> None:
        """Initialize the Api

        Args:
            server_state (ServerState): Current State of the server
            database (MeasurementDB): Database
            namespace (str, optional): SocketIO namespace. Defaults to "/js".
        """
        super().__init__(namespace=namespace)
        self.server_state = server_state
        self.database = database

    def on_getSettings(self, data):
        """Get the current start time.

        Args:
            data (_type_): unused

        Returns:
            int: current start time in nanoseconds since epoch.
        """
        settings_msg = Settings()
        settings_msg.oven_target_temperature = self.server_state.oven_ref_temp
        settings_msg.core_target_temperature = self.server_state.core_ref_temp

        return settings_msg.SerializeToString()

    def on_setSettings(self, data):
        settings_msg = Settings()
        settings_msg.ParseFromString(data)

        self.server_state.oven_ref_temp = settings_msg.oven_target_temperature
        self.server_state.core_ref_temp = settings_msg.core_target_temperature

        self.emit("newSettings", data)
