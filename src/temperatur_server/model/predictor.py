from model.meat_estimator import MeatEstimator
from model.oven_estimator import OvenEstimator

class Predictor():
    def __init__(self) -> None:
        self._oven_est = OvenEstimator()
        self._meat_est = MeatEstimator()
        self._dt = 10.0
        pass

    def fit(self, outer_measurement, inner_measurement):
        self._oven_params = self._oven_est.fit_params(outer_measurement)
        self._meat_params = self._meat_est.fit_params(inner_measurement, outer_measurement)
        self._t0 = len(outer_measurement) * self._dt
        # print(outer_measurement)
        print("fitted_w_0: ", self._oven_params[1])
        return self._oven_params, self._meat_params

    def predict(self, ref_temp, max_dur = 8*10*60*60):
        t_0 = self._t0
        meat_x_0 = self._meat_params[1][-1,:]
        # print(*self._oven_params)
        oven_temp = [self._oven_est._model.func(t_0 , *self._oven_params)]
        meat_state = [meat_x_0.tolist()]
        for i in range(int(max_dur/self._dt)):
            meat_state.append(self._meat_est._model.next_state(meat_state[-1], oven_temp[-1], self._meat_params[0], self._dt).tolist())
            oven_temp.append(self._oven_est._model.func(t_0 + (i+1)* self._dt, *self._oven_params))
            
            
            if meat_state[-1][-1] >= ref_temp:
                break

        return oven_temp, meat_state, i * self._dt + t_0

# from oven_model import OvenModel
# import numpy as np
# est = MeatEstimator()
# oven = OvenModel()
# import matplotlib.pyplot as plt
# dt = 10.0
# t = np.linspace(0,600*dt,num=1000)
# outer_meas = 10.0* np.ones_like(t)
# inner_meas = [1.0]
# heating = True

# oven_state = np.array([45.0 ,0.0])
# x = np.ones(20)
# for i in range(200):
#     oven_state, heating = oven.next_temp(oven_state,heating,55.0,45.0,0.00001, 0.0004, 20.0,0.01,dt)
# outer_meas[0] = oven_state[0]
# for i in range(999):
#     oven_state, heating = oven.next_temp(oven_state,heating,55.0,45.0,0.00001, 0.0004, 20.0,0.01,dt)
#     outer_meas[i+1] = oven_state[0]
#     x = est._model.next_state(x,outer_meas[i],7.2,dt)
#     inner_meas.append(x[-1] )#+ np.random.normal()*0.1)

# pred = Predictor()
# oven_params, meat_params = pred.fit(outer_meas, inner_meas)
# oven_temp, meat_state = pred.predict(25)
# t_pred = t[-1] + np.array(range(len(oven_temp)))*dt
# #r, states = est.fit_params(inner_meas,outer_meas)
# #print("r: ", r)
# plt.plot(t,meat_params[1])
# plt.plot(t,inner_meas)
# plt.plot(t,outer_meas)
# plt.plot(t_pred, oven_temp)
# plt.plot(t_pred, meat_state)
# plt.show()


