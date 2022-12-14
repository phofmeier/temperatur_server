"""Model implementation of the meat
"""

import casadi as cad
import numpy as np


class MeatModel:
    """Model defining the temperature in the meat"""

    def __init__(self, num_elemnets: int = 10) -> None:
        """Initialize the meat model.

        Args:
            num_elemnets (int, optional): number of elements. Defaults to 10.
        """
        self._num_elements = num_elemnets
        x_sim_meat = cad.SX.sym("x_sim_meat", self._num_elements)
        u_sim_meat = cad.SX.sym("u_sim_meat", 1)
        r_sim_meat = cad.SX.sym("r_sim_meat", 1)
        dt_sim_meat = cad.SX.sym("dt_sim_meat", 1)
        x_next = self.next_state_casadi(x_sim_meat, u_sim_meat, r_sim_meat, dt_sim_meat)
        self.casadi_fun = cad.Function(
            "next_state",
            [x_sim_meat, u_sim_meat, r_sim_meat, dt_sim_meat],
            [x_next],
            ["x0_sim_meat", "u_sim_meat", "r_sim_meat", "dt_sim_meat"],
            [
                "x_next",
            ],
        )

    def ode_casadi(self, x, u, r):
        dT = []
        r_scaled = 1 / (r * self._num_elements)
        dT.append(r_scaled * (u / 2.0 - x[0] + x[1] / 2.0))
        for i in range(1, self._num_elements - 1):
            dT.append(r_scaled * (x[i - 1] / 2.0 - x[i] + x[i + 1] / 2.0))
        dT.append(r_scaled * (x[self._num_elements - 2] - x[self._num_elements - 1]))
        return cad.vertcat(*dT)

    def next_state_casadi(self, x, u, r, dt):
        x_next = self.rk4(self.ode_casadi, x, u, r, dt)
        return x_next

    def ode(self, x, u, r):
        """
        state = T
        dT_k = 1/2 * r * (T_k-1 - T_k) + 1/2 * r * (T_k+1 - T_k)
           = -r*T_k + 1/2 r * (T_k-1 + T_k+1)
           = r * (1/2 T_k-1 - T_k + 1/2 T_k+1)

        dT_0 = 1/2* r* (u - T_0) + 1/2* r * (T_1 - T_0)
             = r (1/2 u -T_0 + 1/2 T_1)

        dT_N = r(T_N-1 - T_N)
        """
        dT = []
        r_scaled = 1 / (r * self._num_elements)
        dT.append(r_scaled * (u / 2.0 - x[0] + x[1] / 2.0))
        for i in range(1, self._num_elements - 1):
            dT.append(r_scaled * (x[i - 1] / 2.0 - x[i] + x[i + 1] / 2.0))
        dT.append(r_scaled * (x[self._num_elements - 2] - x[self._num_elements - 1]))
        return np.array(dT)

    def next_state(self, x, u, r, dt):
        # x_next = self.rk4(self.ode,x,u,r, dt)
        x_next = np.array(self.casadi_fun(x, u, r, dt).full().flatten())
        return x_next

    def rk4(self, ode, x, u, r, dt):
        steps = 5
        dt_step = dt / steps
        x_next = x
        for j in range(steps):
            k1 = ode(x_next, u, r)
            k2 = ode(x_next + dt_step / 2.0 * k1, u, r)
            k3 = ode(x_next + dt_step / 2.0 * k2, u, r)
            k4 = ode(x_next + dt_step * k3, u, r)
            x_next = x_next + dt_step / 6.0 * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        return x_next
