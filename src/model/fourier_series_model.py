import casadi as cad
import numpy as np

class FourierSeriesModel():
    def __init__(self) -> None:
        pass

    def func_casadi(self, t, amplitudes, w_0, bias):
        value = bias
        for i in range(len(amplitudes)):
            value += amplitudes[i][0] * cad.cos(w_0 * i *t) + amplitudes[i][1] * cad.sin(w_0 * i * t)

        return value

    def func(self, t, amplitudes, w_0, bias):
        value = bias
        for i in range(amplitudes.shape[0]):
            value += amplitudes[i][0] * np.cos(w_0 * i *t) + amplitudes[i][1] * np.sin(w_0 * i * t)

        return value
