import numpy as np


class OvenModel:
    def __init__(self) -> None:
        pass

    def two_point_controller(self, temp, heating, upper_temp, lower_temp):
        if heating and temp >= upper_temp:
            heating = False
        if not heating and temp <= lower_temp:
            heating = True
        return heating

    def ode(self, x, heating, ambient_constant, heat_constant, temp_ambient, damping):
        """
        state = T, heating
        heating = if heating & T> upper -> heating=False
        dT = k*(T_a - T) + u
        u =

        """
        dx = np.array(
            [
                x[1],
                ambient_constant * (temp_ambient - x[0])
                + heating * heat_constant
                - damping * x[1],
            ]
        )

        return dx

    def next_temp(
        self,
        x,
        heating,
        upper_temp,
        lower_temp,
        ambient_constant,
        heat_constant,
        temp_ambient,
        damping,
        dt,
    ):
        heating = self.two_point_controller(x[0], heating, upper_temp, lower_temp)

        return (
            x
            + self.ode(
                x, heating, ambient_constant, heat_constant, temp_ambient, damping
            )
            * dt,
            heating,
        )
