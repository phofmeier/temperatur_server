from model.fourier_series_model import FourierSeriesModel
import casadi as cad
import numpy as np

class OvenEstimator():
    def __init__(self) -> None:
        self._dt= 10.0
        self._num_functions = 20
        self._model = FourierSeriesModel(self._num_functions)
        self.last_x_init = None

    
    def get_frequency(self, measurements):
        """

        """
        meas = np.array(measurements)
        bias = np.mean(measurements)
        meas[meas<bias] = -1
        meas[meas>=bias] = 1
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
            steps = np.max([index_changes*2.0,meas.shape[0]])
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
            w = 2 * np.pi /(steps*self._dt)
        return bias, w    

        
    
    def fit_params(self, outer_measurements):
        bias_calc, w_calc = self.get_frequency(outer_measurements)
        x_init = []
        w = []
        g = []
        lbg = []
        ubg = []
        bias = cad.SX.sym("bias",1)
        # g.append(bias)
        # lbg.append(10.0)
        # ubg.append(200.0)
        w.append(bias)
        x_init.append(bias_calc)
        phase = 0
        # phase = cad.SX.sym("phase",1)
        # g.append(phase)
        # lbg.append(-cad.pi)
        # ubg.append(cad.pi)
        # w.append(phase)
        #x_init.append(0.0)
        # w_0 = cad.SX.sym("w_0",1)
        # w.append(w_0)
        # g.append(w_0)
        # lbg.append(0.00)
        # ubg.append(10.0)
        # x_init.append(1.0)
        w_0 = w_calc
        # amplitudes = []
        # for i in range(self._num_functions):
        #     amp = cad.SX.sym("amp_" + str(i), 2)
        #     amplitudes.append(amp)
        #     w.append(amp)
        #     x_init.append([0.010,0.01])
        amplitudes = cad.SX.sym("amplitudes",(self._num_functions,2))
        w += cad.horzsplit(amplitudes)
        x_init.append([0.010,0.01]*self._num_functions)

        f = 0#1e-3*cad.norm_1(amplitudes)
        for i in range(len(outer_measurements)):
            f += 1.001**i *(outer_measurements[i] - self._model.casadi_fun(i * self._dt,amplitudes,w_0, bias, phase))**2.0

        qp = {'x':cad.vertcat(*w), 'f':f,}#  'g': cad.vertcat(*g)}
        solver = cad.nlpsol("Solver", "ipopt",qp, )
        if self.last_x_init is not None:
            x_init = self.last_x_init
            #x_init = cad.vertcat(*x_init)
            x_init[0]= bias_calc
        else:
            x_init = cad.vertcat(*x_init)
        sol = solver(x0=x_init,)# lbg=cad.vertcat(*lbg), ubg=cad.vertcat(*ubg))
        fitted_bias = float(sol["x"][0].full()[0])
        fitted_phase = phase # float(sol["x"][1].full()[0])
        fitted_w_0 = w_0#float(sol["x"][1].full()[0])
        fitted_params = np.zeros((self._num_functions,2))
        fitted_params[:,0] = np.array(sol["x"][1:1+self._num_functions].full()).reshape((self._num_functions,))
        fitted_params[:,1] = np.array(sol["x"][1+self._num_functions:].full()).reshape((self._num_functions,))
        #fitted_params = np.reshape(np.array(sol["x"][2:].full()),(-1, 2))
        self.last_x_init = sol["x"].full().flatten()
        #print("fitted_w_0: ", fitted_w_0)
        # print(amplitudes)
        # print(w[2:])
        # print(sol["x"][2:].full())
        # print(fitted_params)
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
