import casadi as cad
import numpy as np


class MeatModel:
    def __init__(self, num_elemnets=10) -> None:
        self._num_elements = num_elemnets

    def ode_casadi(self, x, u, r):
        dT = []
        r_scaled = 1 / (r * self._num_elements)
        dT.append(r_scaled * (u / 2.0 - x[0] + x[1] / 2.0))
        for i in range(1, self._num_elements - 1):
            dT.append(r_scaled * (x[i - 1] / 2.0 - x[i] + x[i + 1] / 2.0))
        dT.append(r_scaled * (x[self._num_elements - 2] - x[self._num_elements - 1]))
        return cad.vertcat(*dT)

    def next_state_casadi(self, x, u, r, dt):
        x_next = x + self.ode_casadi(x, u, r) * dt
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
        x_next = x + self.ode(x, u, r) * dt
        return x_next


# import matplotlib.pyplot as plt
# model = MeatModel(20)
# u = 10.0 + np.sin(1e-1*np.array(range(601)))
# r = 0.0010
# dt = 0.01
# x = np.zeros(20)
# states = []
# states.append(x)
# for i in range(600):
#     x = model.next_state(x,u[i],r,dt)
#     states.append(x)
# t = range(601)
# plt.plot(t,states)
# plt.plot(t,u)
# # plt.show()

# x = cad.SX.sym("x", (20,1))

# x_next = model.next_state_casadi(x,u[0],r,dt)
# print(x_next)
