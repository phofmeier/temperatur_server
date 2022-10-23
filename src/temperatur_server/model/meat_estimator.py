from model.meat_model import MeatModel
import casadi as cad
import numpy as np

class MeatEstimator():
    def __init__(self) -> None:
        self._num_elements = 10
        self._dt= 10.0
        self._model = MeatModel(self._num_elements)
        self.last_x_init = None

    def fit_params(self,meas_inner, meas_outer):
        x_init = []
        r = cad.SX.sym("r")
        x_init.append(1.0)
        g = [r]
        lbg = [0.0]
        ubg = [40.0]
        x_0 = cad.SX.sym("x_0", self._num_elements)
        w = [r,x_0]
        x_init.append(np.zeros(self._num_elements))
        
        f = (x_0[self._num_elements-1] - meas_inner[0])**2

        for i in range(self._num_elements-1):
            g.append(x_0[i]-x_0[i+1])
            lbg.append(0.0)
            ubg.append(cad.inf)
        for i in range(self._num_elements):
            g.append(x_0[i])
            lbg.append(0.0)
            ubg.append(60.0)
        

        x_curr = x_0
        for i in range(len(meas_inner)-1):
            x_sym = cad.SX.sym("x_" + str(i+1), self._num_elements)
            w.append(x_sym)
            x_init.append(np.linspace(meas_outer[i],meas_inner[i+1],self._num_elements))
            x_next = self._model.casadi_fun(x_curr,meas_outer[i],r,self._dt)
            g.append(x_sym - x_next)
            lbg.append(np.zeros(self._num_elements))
            ubg.append(np.zeros(self._num_elements))
            g.append(x_curr)
            lbg.append(np.zeros(self._num_elements))
            ubg.append(200.0*np.ones(self._num_elements))
            f += (x_sym[self._num_elements-1] - meas_inner[i+1])**2
            x_curr=x_sym
        
        g.append(x_curr)
        lbg.append(np.zeros(self._num_elements))
        ubg.append(200.0*np.ones(self._num_elements))
        
        qp = {'x':cad.vertcat(*w), 'f':f, 'g':cad.vertcat(*g)}
        solver = cad.nlpsol("Solver", "ipopt",qp)
        x_init = cad.vertcat(*x_init)
        if self.last_x_init is not None:
            x_init[:self.last_x_init.shape[0]] = self.last_x_init
        sol = solver(x0=x_init, lbg=cad.vertcat(*lbg), ubg=cad.vertcat(*ubg))
        r = sol["x"][0]
        self.last_x_init = sol["x"].full().flatten()
        states = np.reshape(np.array(sol["x"][1:]),(-1, self._num_elements))
        return r, states

# from oven_model import OvenModel
# est = MeatEstimator()
# oven = OvenModel()
# import matplotlib.pyplot as plt
# dt = 10.0
# t = np.linspace(0,600*dt,num=1000)
# outer_meas = 10.0* np.ones_like(t)
# inner_meas = [1.0]
# heating = True
# outer_meas[0] = 44.0
# oven_state = np.array([44.0 ,0.0])
# x = np.ones(20)
# for i in range(999):
#     oven_state, heating = oven.next_temp(oven_state,heating,55.0,45.0,0.0001, 0.004, 20.0,0.01,dt)
#     outer_meas[i+1] = oven_state[0]
#     x = est._model.next_state(x,outer_meas[i],7.2,dt)
#     inner_meas.append(x[-1] + np.random.normal()*0.1)

# r, states = est.fit_params(inner_meas,outer_meas)
# print("r: ", r)
# plt.plot(t,states)
# plt.plot(t,inner_meas)
# plt.plot(t,outer_meas)
# plt.show()

