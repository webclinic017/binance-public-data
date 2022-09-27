import backtrader as bt
import math
import numpy as np

class EMV(bt.Indicator):
    lines = ('emv', 'maemv')
    params = (('period', 1),)

    def __init__(self):
        #self.addminperiod(self.params.period)
        self.emv_days = self.params.period
        self.em_array = []
        self.emv_array = []
        print(f'--emv动量天数--{self.emv_days}')

    def next(self):
        mid = ((self.data.low[-1] + self.data.high[-1]) - (self.data.low[-2] + self.data.high[-2])) / 2
        bro = self.data.volume[-1] / (self.data.high[-1] - self.data.low[-1])
        em = mid / bro
        # 计算emv
        self.em_array.append(em)
        em_array_n = np.array(self.em_array)
        em_array_n1 = em_array_n[::-1]
        emv = em_array_n1[:self.emv_days].sum()
        # 计算 maemv
        self.emv_array.append(emv)
        emv_array_n = np.array(self.emv_array)
        emv_array_n1 = emv_array_n[::-1]
        maemv = emv_array_n1[:self.emv_days].sum()
        # 输出
        self.lines.emv[0] = emv * 1000000
        self.lines.maemv[0] = maemv * 1000000
