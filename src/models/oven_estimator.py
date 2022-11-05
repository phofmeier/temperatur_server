import casadi as cad
import numpy as np

from models.fourier_series_model import FourierSeriesModel


class OvenEstimator:
    def __init__(self) -> None:
        self._dt = 10.0
        self._num_functions = 20
        self._model = FourierSeriesModel(self._num_functions)
        self.last_x_init = None

    def get_frequency(self, measurements):
        """ """
        meas = np.array(measurements)
        bias = np.mean(measurements)
        meas[meas < bias] = -1
        meas[meas >= bias] = 1
        diff = np.abs(np.diff(meas))
        index_changes = np.where(diff > 1)[0]
        print("changes_before", index_changes)
        # add logic for filtering

        if index_changes.shape[0] > 1:
            last_index = index_changes[0]
            filtered_changes = [last_index]
            for i in range(1, index_changes.shape[0]):
                curr_diff = index_changes[i] - last_index
                if curr_diff > 15:
                    filtered_changes.append(index_changes[i])
                    last_index = index_changes[i]

            index_changes = np.array(filtered_changes)
        print("changes_after", index_changes)
        steps = 0
        if index_changes.shape[0] == 1:
            steps = np.max([index_changes * 2.0, meas.shape[0]])
        elif index_changes.shape[0] == 2:
            steps = np.max([index_changes[1] - index_changes[0], meas.shape[0]])
        else:
            diff_indices = np.diff(index_changes)
            phase_1 = diff_indices[::2]
            phase_2 = diff_indices[1::2]
            steps = np.mean(phase_1) + np.mean(phase_2)

        if steps == 0:
            w = 0.0
        else:
            w = 2 * np.pi / (steps * self._dt)
        return bias, w

    def fit_params(self, outer_measurements):
        bias_calc, w_calc = self.get_frequency(outer_measurements)
        x_init = []
        w = []

        bias = cad.SX.sym("bias", 1)

        w.append(bias)
        x_init.append(bias_calc)
        phase = 0

        w_0 = w_calc

        amplitudes = cad.SX.sym("amplitudes", (self._num_functions, 2))
        w += cad.horzsplit(amplitudes)
        x_init.append([0.010, 0.01] * self._num_functions)

        f = 0
        for i in range(len(outer_measurements)):
            f += (
                1.001**i
                * (
                    outer_measurements[i]
                    - self._model.casadi_fun(i * self._dt, amplitudes, w_0, bias, phase)
                )
                ** 2.0
            )

        qp = {
            "x": cad.vertcat(*w),
            "f": f,
        }
        solver = cad.nlpsol(
            "Solver",
            "ipopt",
            qp,
        )
        if self.last_x_init is not None:
            x_init = self.last_x_init
            x_init[0] = bias_calc
        else:
            x_init = cad.vertcat(*x_init)
        sol = solver(
            x0=x_init,
        )
        fitted_bias = float(sol["x"][0].full()[0])
        fitted_phase = phase
        fitted_w_0 = w_0
        fitted_params = np.zeros((self._num_functions, 2))
        fitted_params[:, 0] = np.array(
            sol["x"][1 : 1 + self._num_functions].full()
        ).reshape((self._num_functions,))
        fitted_params[:, 1] = np.array(
            sol["x"][1 + self._num_functions :].full()
        ).reshape((self._num_functions,))

        self.last_x_init = sol["x"].full().flatten()

        return fitted_params, fitted_w_0, fitted_bias, fitted_phase
