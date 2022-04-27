
import numpy as np


class LinearRegression:

    def __init__(self, max_data_size):
        self.max_data_size = max_data_size
        self.clear()

    def add_point(self, x, y):
        if self.curr_size == self.max_data_size:
            self.x.pop(0)
            self.y.pop(0)
            self.curr_size -= 1

        self.x.append(x)
        self.y.append(y)
        self.curr_size += 1

    def clear(self):
        self.x = []
        self.y = []
        self.curr_size = 0

    def _estimate_coef(self):
        n = self.curr_size
        x = np.array(self.x)
        y = np.array(self.y)

        m_x = np.mean(x)
        m_y = np.mean(y)
        SS_xy = np.sum(y*x) - n*m_y*m_x
        SS_xx = np.sum(x*x) - n*m_x*m_x
        b_1 = SS_xy / SS_xx
        b_0 = m_y - b_1*m_x
        return (b_0, b_1)

    def estimate(self, x):
        b, m = self._estimate_coef()
        return m * x + b


if __name__ == '__main__':
    l = LinearRegression(30)
    l.add_point(44100.0, 0.0010006427764892578)
    print(l.estimate(260003420))
