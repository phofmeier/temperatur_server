import casadi as cad
import numpy as np

class FourierSeriesModel():
    def __init__(self, num_functions) -> None:
        self.num_functions = num_functions
        t_sim = cad.SX.sym("t_sim",1)
        amp_sim = cad.SX.sym("amp_sim", (self.num_functions,2))
        w_0_sim = cad.SX.sym("w_0_sim",1)
        bias_sim = cad.SX.sym("bias_sim",1)
        phase_sim = cad.SX.sym("phase_sim",1)
        temp_sim = self.func_casadi(t_sim,amp_sim,w_0_sim,bias_sim,phase_sim)
        self.casadi_fun = cad.Function('temp_func', [t_sim, amp_sim, w_0_sim, bias_sim, phase_sim], [temp_sim],['t_sim','amp_sim', 'w_0_sim', 'bias_sim', 'phase_sim'],['temp_sim',])
        pass

    def func_casadi(self, t, amplitudes, w_0, bias, phase):
        value = bias
        for i in range(amplitudes.shape[0]):
            value += amplitudes[i,0] * cad.cos(w_0 * (i+1)* t + phase) + amplitudes[i,1] * cad.sin(w_0 * (i+1) * t+ phase)

        return value

    def func(self, t, amplitudes, w_0, bias, phase):
        # value = bias
        # for i in range(amplitudes.shape[0]):
        #     value += amplitudes[i][0] * np.cos(w_0 * (i+1) *t+ phase) + amplitudes[i][1] * np.sin(w_0 * (i+1) * t+ phase)

        # return value
        temp = self.casadi_fun(t,amplitudes,w_0,bias,phase).full().flatten()[0]
        return temp

