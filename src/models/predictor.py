import copy
import traceback
from multiprocessing import Process, Queue
from typing import List, Optional, Tuple, Union

import numpy as np

from models.meat_estimator import MeatEstimator
from models.oven_estimator import OvenEstimator


class PredictionInputData:
    """Data Container for Prediction input data."""

    def __init__(
        self,
        outer_measurements: List[float],
        inner_measurements: List[float],
        start_time: int,
        core_end_temp: float,
    ) -> None:
        """Initialize the container.

        Args:
            outer_measurements (List[float]): Oven measurements
            inner_measurements (List[float]): Core temperature measurements.
            start_time (int): timestamp of the first measurement.
            core_end_temp (float): Core temperature which should be reached at the end.
        """
        self.outer_measurements = outer_measurements
        self.inner_measurements = inner_measurements
        self.start_time = start_time
        self.core_end_temp = core_end_temp


class PredictionResult:
    """Data Container for Prediction Results."""

    def __init__(
        self,
        timestamps_fit: List[int],
        oven_temp_fit: List[float],
        meat_state_fit: List[List[float]],
        timestamps_prediction: List[int],
        oven_temp_prediction: List[float],
        meat_state_prediction: List[List[float]],
        timestamp_end: int,
    ) -> None:
        """Initialize the input data.

        Args:
            timestamps_fit (List[int]): Timestamps of the fit in ns since epoch.
            oven_temp_fit (List[float]): Temperature of the oven at the fit.
            meat_state_fit (List[List[float]]):
                Temperature of all meat states at the fit.
            timestamps_prediction (List[int]):
                Timestamps of the prediction in ns since epoch.
            oven_temp_prediction (List[float]):
                Temperature of the oven at the prediction.
            meat_state_prediction (List[List[float]]):
                Temperature of the meat states at the prediction.
            timestamp_end (int): Timestamp when the core end temperature is reached.
        """
        self.timestamps_fit = timestamps_fit
        self.oven_temp_fit = oven_temp_fit
        self.meat_state_fit = meat_state_fit
        self.timestamps_prediction = timestamps_prediction
        self.oven_temp_prediction = oven_temp_prediction
        self.meat_state_prediction = meat_state_prediction
        self.timestamp_end = timestamp_end

    def to_list(self) -> List[Union[List[int], List[float], List[List[float]], int]]:
        """Return as List.

        Returns:
            List[Union[List[int], List[float], List[List[float]], int]]:
                List containing all data.
        """
        return [
            self.timestamps_fit,
            self.oven_temp_fit,
            self.meat_state_fit,
            self.timestamps_prediction,
            self.oven_temp_prediction,
            self.meat_state_prediction,
            self.timestamp_end,
        ]


class Predictor:
    """Predicts the time until the meat is ready.

    The measurement data is fit to a model which is used to predict
    the remaining time until a specific core temperature is reached.
    """

    def __init__(self, dt: float, oven_num_func: int, meat_num_func: int) -> None:
        """Initialize the predictor.

        Args:
            dt (float): timedelta between two measurements in seconds.
            oven_num_func (int): Used number of functions for the oven model.
            meat_num_func (int): used number of functions for the meat model.
        """
        self._oven_est = OvenEstimator(dt, oven_num_func)
        self._meat_est = MeatEstimator(dt, meat_num_func)
        self._dt = dt
        self.process: Optional[Process] = None
        self.result: Optional[PredictionResult] = None
        self.input_q: Queue[PredictionInputData] = Queue(maxsize=1)
        self.output_q: Queue[PredictionResult] = Queue(maxsize=1)
        self._is_running = False

    def fit(
        self, outer_measurement: List[float], inner_measurement: List[float]
    ) -> Tuple[Tuple[np.ndarray, float, float, float], Tuple[float, np.ndarray], float]:
        self._oven_params = self._oven_est.fit_params(outer_measurement)
        self._meat_params = self._meat_est.fit_params(
            inner_measurement, outer_measurement
        )
        self._t0 = len(outer_measurement) * self._dt
        return self._oven_params, self._meat_params, self._t0

    def predict(
        self, ref_temp: float, t_0: float, max_dur: int = 8 * 10 * 60 * 60
    ) -> Tuple[List[float], List[List[float]], float]:
        meat_x_0 = self._meat_params[1][-1, :]
        oven_temp = [self._oven_est._model.func(t_0, *self._oven_params)]
        meat_state = [meat_x_0.tolist()]
        for i in range(int(max_dur / self._dt)):
            meat_state.append(
                self._meat_est._model.next_state(
                    meat_state[-1], oven_temp[-1], self._meat_params[0], self._dt
                ).tolist()
            )
            oven_temp.append(
                self._oven_est._model.func(t_0 + (i + 1) * self._dt, *self._oven_params)
            )

            if meat_state[-1][-1] >= ref_temp:
                break

        return oven_temp, meat_state, i * self._dt + t_0

    def run_parallel(self, input_data: PredictionInputData) -> None:
        self.save_result()
        if self.is_running():
            return
        self.input_q.put(input_data)
        self._is_running = True
        if self.process is None or not self.process.is_alive():
            self.process = Process(
                target=self.generate_result,
                daemon=True,
            )
            self.process.start()
        return

    def is_running(self) -> bool:
        self.save_result()
        if self.process is None:
            self._is_running = False
            return False
        if not self.process.is_alive():
            self.process.close()
            self.process = None
            self._is_running = False
            return False
        return self._is_running

    def maybe_get_result(
        self,
    ) -> Optional[PredictionResult]:
        self.save_result()
        if self.is_running():
            return None

        if self.result is not None:
            result_return = copy.deepcopy(self.result)
            self.result = None
            return result_return

        return None

    def save_result(self) -> None:
        if not self.output_q.empty():
            self.result = self.output_q.get()
            self._is_running = False

    def generate_result(self) -> None:

        try:
            while True:
                data = self.input_q.get()
                start_time = data.start_time
                oven_params, meat_params, t_0 = self.fit(
                    data.outer_measurements, data.inner_measurements
                )
                oven_temp, meat_state, duration_to_end = self.predict(
                    data.core_end_temp, t_0
                )
                t_fit = start_time + np.array(
                    np.arange(len(meat_params[1])), dtype=int
                ) * int(self._dt * 1e9)
                t_pred = t_fit[-1] + np.array(
                    np.arange(len(oven_temp)), dtype=int
                ) * int(self._dt * 1e9)
                t_oven = (
                    np.array(np.arange(meat_params[1].shape[0]), dtype=float) * self._dt
                )
                t_end = start_time + int(duration_to_end * 1e9)
                oven_fit = []
                for i in range(t_oven.shape[0]):
                    oven_fit.append(self._oven_est._model.func(t_oven[i], *oven_params))

                result = [
                    t_fit.tolist(),
                    oven_fit,
                    meat_params[1].tolist(),
                    t_pred.tolist(),
                    oven_temp,
                    meat_state,
                    t_end,
                ]
                self.output_q.put(PredictionResult(*result))

        except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")
            traceback.print_exc()
