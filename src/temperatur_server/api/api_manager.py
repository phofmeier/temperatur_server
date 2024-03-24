""" Implementation to manage different apis.
"""

from flask_socketio import SocketIO

from database.database import MeasurementDB
from temperatur_server.api.js_api import JavaScriptApi
from temperatur_server.api.protobuf_api import ProtobufApi
from temperatur_server.server_state import ServerState


class ApiManager:
    """Manages the usage of different SocketIO apis."""

    def __init__(
        self, state: ServerState, database: MeasurementDB, socket_io: SocketIO
    ) -> None:
        """Initialize the Manager for the different apis

        Args:
            state (_type_): _description_
            database (_type_): _description_
            socket_io (_type_): _description_
        """
        self.state = state
        self.socket_io = socket_io
        self.api_list = [
            JavaScriptApi(state, database, "/js"),
            ProtobufApi(state, database, "/pb"),
        ]
        self.register_apis()

    def register_apis(self) -> None:
        """Register all apis to the socket io server."""
        for api in self.api_list:
            self.socket_io.on_namespace(api)

    def emit_all(
        self,
        event,
        data=None,
        room=None,
        include_self=True,
        namespace=None,
        callback=None,
    ):
        """Emit a message to all apis.

            All arguments are forwarded to each api.

        Args:
            event (any): event name
            data (any, optional): data. Defaults to None.
            room (any, optional): room. Defaults to None.
            include_self (bool, optional): include_self. Defaults to True.
            namespace (any, optional): namespace. Defaults to None.
            callback (any, optional): callback. Defaults to None.
        """

        for api in self.api_list:
            api.emit(event, data, room, include_self, namespace, callback)
