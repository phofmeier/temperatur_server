import copy
import traceback
from multiprocessing import Process, Queue
from typing import List, Optional, Tuple, Union

import numpy as np

from models.meat_estimator import MeatEstimator
from models.oven_estimator import OvenEstimator


class PredictionInputData:
    def __init__(
        self,
        outer_measurements: List[float],
        inner_measurements: List[float],
        start_time: int,
        core_end_temp: float,
    ) -> None:
        self.outer_measurements = outer_measurements
        self.inner_measurements = inner_measurements
        self.start_time = start_time
        self.core_end_temp = core_end_temp


class PredictionResult:
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
        self.timestamps_fit = timestamps_fit
        self.oven_temp_fit = oven_temp_fit
        self.meat_state_fit = meat_state_fit
        self.timestamps_prediction = timestamps_prediction
        self.oven_temp_prediction = oven_temp_prediction
        self.meat_state_prediction = meat_state_prediction
        self.timestamp_end = timestamp_end

    def to_list(self) -> List[Union[List[int], List[float], List[List[float]], int]]:
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
    def __init__(
        self, dt: float = 10, oven_num_func: int = 10, meat_num_func: int = 10
    ) -> None:
        self._oven_est = OvenEstimator(dt, oven_num_func)
        self._meat_est = MeatEstimator(dt, meat_num_func)
        self._dt = dt
        self.process: Optional[Process] = None
        self.result: Optional[PredictionResult] = None
        self.input_q: Queue[PredictionInputData] = Queue(maxsize=1)
        self.output_q: Queue[PredictionResult] = Queue(maxsize=1)

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
            # Todo: throw error
            print("still alive")
            return
        self.input_q.put(input_data)
        if self.process is not None:
            self.process.close()
        self.process = Process(
            target=self.generate_result,
            daemon=False,
        )
        self.process.start()
        return

    def is_running(self) -> bool:
        self.save_result()
        if self.process is None:
            return False
        return self.process.is_alive()

    def maybe_get_result(
        self,
    ) -> Optional[List[Union[List[int], List[float], List[List[float]], int]]]:
        self.save_result()
        if self.is_running():
            return None

        if self.result is not None:
            result_return = copy.deepcopy(self.result)
            self.result = None
            return result_return.to_list()

        return None

    def save_result(self) -> None:
        if not self.output_q.empty():
            self.result = self.output_q.get()

    def generate_result(self) -> None:
        try:
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
            t_pred = t_fit[-1] + np.array(np.arange(len(oven_temp)), dtype=int) * int(
                self._dt * 1e9
            )
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
