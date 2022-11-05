from models.meat_estimator import MeatEstimator
from models.oven_estimator import OvenEstimator


class Predictor:
    def __init__(self) -> None:
        self._oven_est = OvenEstimator()
        self._meat_est = MeatEstimator()
        self._dt = 10.0
        pass

    def fit(self, outer_measurement, inner_measurement):
        self._oven_params = self._oven_est.fit_params(outer_measurement)
        self._meat_params = self._meat_est.fit_params(
            inner_measurement, outer_measurement
        )
        self._t0 = len(outer_measurement) * self._dt
        return self._oven_params, self._meat_params

    def predict(self, ref_temp, max_dur=8 * 10 * 60 * 60):
        t_0 = self._t0
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
