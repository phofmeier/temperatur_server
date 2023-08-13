""" Implementation for an api for JavaScript webpage.
"""

import flask_socketio

from database.database import MeasurementDB
from temperatur_server.server_state import ServerState


class JavaScriptApi(flask_socketio.Namespace):
    """Api for the usage with java script.

    Inheritance of socketIO namespace
    """

    def __init__(
        self, server_state: ServerState, database: MeasurementDB, namespace: str = "/js"
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

    def on_getTimeSeries(self, date) -> str:
        """Get the data time series

        Args:
            date (_type_): _description_

        Returns:
            str: All relevant data
        """
        return_value = self.database.getBetweenTime(
            self.server_state.start_time - self.server_state.nano_seconds_before_start
        )
        return return_value

    def on_getOvenRefTemp(self, date) -> float:
        """get the current oven reference temperature.

        Args:
            date (_type_): _description_

        Returns:
            float: the current oven ref temp
        """

        return self.server_state.oven_ref_temp

    def on_getCoreRefTemp(self, date) -> float:
        """get the current core reference temperature.

        Args:
            date (_type_): unused

        Returns:
            float: core reference temperature.
        """
        return self.server_state.core_ref_temp

    def on_newOvenRef(self, data: float) -> None:
        """set a new Oven Reference Temperature.

        Args:
            data (float): the new oven reference temperature.
        """
        self.server_state.oven_ref_temp = data

    def on_newCoreRef(self, data: float) -> None:
        """Set a new core reference temperature.

        Args:
            data (float): the new core reference temperature
        """
        self.server_state.core_ref_temp = data

    def on_newStartTime(self, data: int) -> None:
        """set a new start time.

        Args:
            data (int): new start time in nanoseconds since epoch.
        """
        self.server_state.start_time = int(data)

    def on_getStartTime(self, data) -> int:
        """Get the current start time.

        Args:
            data (_type_): unused

        Returns:
            int: current start time in nanoseconds since epoch.
        """
        return self.server_state.start_time
