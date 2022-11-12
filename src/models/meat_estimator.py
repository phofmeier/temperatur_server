"""Implementation of meat identification.
"""
from typing import List, Tuple, Union

import casadi as cad
import numpy as np

from models.meat_model import MeatModel


class MeatEstimator:
    """Estimates the temperature and model parameter for the meat."""

    def __init__(self) -> None:
        """Initialize the estimator."""
        self._num_elements = 10
        self._dt = 10.0
        self._model = MeatModel(self._num_elements)
        self.last_x_init = None

    def fit_params(
        self, meas_inner: List[float], meas_outer: List[float]
    ) -> Tuple[float, np.ndarray]:
        """Fit meat parameter to measurements.

        Args:
            meas_inner (List[float]): Measurements of the core temperature.
            meas_outer (List[float]): Measurements of the oven temperature.

        Returns:
            Tuple[float,np.ndarray]: meat resistance param r, temperature states.
        """
        x_init: List[Union[float, np.ndarray]] = []
        r = cad.SX.sym("r")
        x_init.append(1.0)
        g: List[Union[float, np.ndarray]] = [r]
        lbg: List[Union[float, np.ndarray]] = [0.0]
        ubg: List[Union[float, np.ndarray]] = [40.0]
        x_0 = cad.SX.sym("x_0", self._num_elements)
        w = [r, x_0]
        x_init.append(np.zeros(self._num_elements))

        f = (x_0[self._num_elements - 1] - meas_inner[0]) ** 2

        for i in range(self._num_elements - 1):
            g.append(x_0[i] - x_0[i + 1])
            lbg.append(0.0)
            ubg.append(cad.inf)
        for i in range(self._num_elements):
            g.append(x_0[i])
            lbg.append(0.0)
            ubg.append(60.0)

        x_curr = x_0
        for i in range(len(meas_inner) - 1):
            x_sym = cad.SX.sym("x_" + str(i + 1), self._num_elements)
            w.append(x_sym)
            x_init.append(
                np.linspace(meas_outer[i], meas_inner[i + 1], self._num_elements)
            )
            x_next = self._model.casadi_fun(x_curr, meas_outer[i], r, self._dt)
            g.append(x_sym - x_next)
            lbg.append(np.zeros(self._num_elements))
            ubg.append(np.zeros(self._num_elements))
            g.append(x_curr)
            lbg.append(np.zeros(self._num_elements))
            ubg.append(200.0 * np.ones(self._num_elements))
            f += (x_sym[self._num_elements - 1] - meas_inner[i + 1]) ** 2
            x_curr = x_sym

        g.append(x_curr)
        lbg.append(np.zeros(self._num_elements))
        ubg.append(200.0 * np.ones(self._num_elements))

        qp = {"x": cad.vertcat(*w), "f": f, "g": cad.vertcat(*g)}
        solver = cad.nlpsol("Solver", "ipopt", qp)
        x_init = cad.vertcat(*x_init)
        if self.last_x_init is not None:
            x_init[: self.last_x_init.shape[0]] = self.last_x_init
        sol = solver(x0=x_init, lbg=cad.vertcat(*lbg), ubg=cad.vertcat(*ubg))
        r = sol["x"][0]
        self.last_x_init = sol["x"].full().flatten()
        states = np.reshape(np.array(sol["x"][1:]), (-1, self._num_elements))
        return r, states
