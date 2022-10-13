from model.fourier_series_model import FourierSeriesModel
import casadi as cad
import numpy as np

class OvenEstimator():
    def __init__(self) -> None:
        self._dt= 10.0
        self._model = FourierSeriesModel()
        self._num_functions = 10
        self.last_x_init = None
        
    
    def fit_params(self, outer_measurements):
        x_init = []
        w = []
        g = []
        lbg = []
        ubg = []
        bias = cad.SX.sym("bias",1)
        w.append(bias)
        x_init.append(50.0)
        phase = cad.SX.sym("phase",1)
        w.append(phase)
        x_init.append(0.0)
        w_0 = cad.SX.sym("w_0",1)
        w.append(w_0)
        g.append(w_0)
        lbg.append(0.0)
        ubg.append(cad.inf)
        x_init.append(0.00010)
        amplitudes = []
        for i in range(self._num_functions):
            amp = cad.SX.sym("amp_" + str(i), 2)
            amplitudes.append(amp)
            w.append(amp)
            x_init.append([0.010,0.01])

        f = 0
        for i in range(len(outer_measurements)):
            f += (outer_measurements[i] - self._model.func_casadi(i * self._dt,amplitudes,w_0, bias, phase))**2.0

        qp = {'x':cad.vertcat(*w), 'f':f,  'g': cad.vertcat(*g)}
        solver = cad.nlpsol("Solver", "ipopt",qp, )
        if self.last_x_init is not None:
            x_init = self.last_x_init
        else:
            x_init = cad.vertcat(*x_init)
        sol = solver(x0=x_init, lbg=cad.vertcat(*lbg), ubg=cad.vertcat(*ubg))
        fitted_bias = float(sol["x"][0].full()[0])
        fitted_phase = float(sol["x"][1].full()[0])
        fitted_w_0 = float(sol["x"][2].full()[0])
        fitted_params = np.reshape(np.array(sol["x"][3:].full()),(-1, 2))
        self.last_x_init = sol["x"]
        return fitted_params, fitted_w_0, fitted_bias, fitted_phase

       
        
# from oven_model import OvenModel
# est = OvenEstimator()
# oven = OvenModel()
# import matplotlib.pyplot as plt
# dt = 10.0
# t = np.linspace(0,1000*dt,num=1000)
# outer_meas = 10.0* np.ones_like(t)
# inner_meas = [1.0]
# heating = True
# outer_meas[0] = 30.0
# oven_state = np.array([30.0 ,0.0])
# x = np.ones(20)
# for i in range(999):
#     oven_state, heating = oven.next_temp(oven_state,heating,55.0,45.0,0.00001, 0.0004, 20.0,0.01,dt)
#     outer_meas[i+1] = oven_state[0] + np.random.normal()*0.5

# bias,w_0, params = est.fit_params(outer_meas[200:])
# fitted_temp = est._model.func(np.array(t[200:], dtype=np.float) - t[200], params, w_0, bias)
# print("bias: ", bias)
# print("w_0: ",w_0)
# print("params: ", params)


# plt.figure(figsize=(20,20))

# plt.plot(t[200:], fitted_temp, label="fitted")
# plt.plot(t,outer_meas, label="meas")
# plt.legend()
# plt.show()
