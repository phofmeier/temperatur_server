""" Implementation to mange the state of the server
"""

import time


class ServerState:
    """Current state of the server.

    This class holds all configurations which may change during runtime.
    """

    def __init__(self) -> None:
        """Initialize with default values."""
        self.nano_seconds_before_start = 10 * 60 * 1e9
        self.predictor_dt = 10.0
        self.predictor_oven_functions = 10
        self.predictor_meat_elements = 10
        self.oven_ref_temp = 90.0
        self.core_ref_temp = 64.0
        self.start_time = time.time_ns()
        self.last_pushed = self.start_time
