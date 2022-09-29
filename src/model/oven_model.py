import numpy as np
import casadi as cad

class OvenModel():
    def __init__(self) -> None:
        pass

    def two_point_controller(self,temp, heating,upper_temp,lower_temp):
        if heating and temp >= upper_temp:
            heating = False
        if not heating and temp <= lower_temp:
            heating = True
        return heating

    def two_point_controller_casadi(self,temp, heating,upper_temp,lower_temp):
        new_heating = cad.if_else(heating>0, cad.if_else(temp >= upper_temp, 0.0, heating), cad.if_else(temp <= lower_temp, 1.0, heating))
        return new_heating

    def ode_casadi(self,x, heating, ambient_constant,heat_constant, temp_ambient, damping):
        """
        state = T, heating
        heating = if heating & T> upper -> heating=False
        dT = k*(T_a - T) + u
        u = 

        """
        dx = cad.vertcat(x[1],ambient_constant * (temp_ambient - x[0]) + heating * heat_constant - damping*x[1])
         
        return dx

    def next_temp_casadi(self,x, heating,upper_temp,lower_temp, ambient_constant,heat_constant, temp_ambient,damping,dt):
        heating = self.two_point_controller_casadi(x[0],heating, upper_temp,lower_temp)
        
        return x + self.ode_casadi(x, heating, ambient_constant,heat_constant, temp_ambient,damping)*dt , heating
    
    def ode(self,x, heating, ambient_constant,heat_constant, temp_ambient, damping):
        """
        state = T, heating
        heating = if heating & T> upper -> heating=False
        dT = k*(T_a - T) + u
        u = 

        """
        dx = np.array([x[1],ambient_constant * (temp_ambient - x[0]) + heating * heat_constant - damping*x[1]])
         
        return dx

    def next_temp(self,x, heating,upper_temp,lower_temp, ambient_constant,heat_constant, temp_ambient,damping,dt):
        heating = self.two_point_controller(x[0],heating, upper_temp,lower_temp)
        
        return x + self.ode(x, heating, ambient_constant,heat_constant, temp_ambient,damping)*dt , heating


# import matplotlib.pyplot as plt

heating = 0.0
upper_temp = 50.0
lower_temp = 45.0
ambient_constant = 0.00008
heat_constant = 0.01
temp_ambient = 20.0
damping=0.011
dt = 1.0


# curr_temp = np.array([20.0,0.0])
# tempertures =  [curr_temp]
oven = OvenModel()
# for i in range(4*600):
#     curr_temp, heating = oven.next_temp(curr_temp,heating, upper_temp,lower_temp,ambient_constant,heat_constant,temp_ambient,dt)
#     tempertures.append(curr_temp)

# plt.figure()
# plt.plot(tempertures)
# plt.show()
curr_temp = cad.SX.sym("x",2)
upper_temp = cad.SX.sym("ut",1)
lower_temp = cad.SX.sym("lt",1)
heating = cad.SX.sym("h",1)
next_heating, next_state = oven.next_temp_casadi(curr_temp,heating, upper_temp,lower_temp,ambient_constant,heat_constant,temp_ambient,damping,dt)
print(next_heating)
print(next_state) 