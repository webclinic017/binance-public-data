import backtrader as bt
import math
import numpy as np
import talib as ta

# 钱德动量摆动指标
class ChandeMomentumOscillator(bt.Indicator):
    lines = ('cmo',)
    params = (
        ('period', 30),)

    def log(self, txt, dt=None):
        #Logging function for this strategy
        dt = dt or self.data.datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.cmo_days = self.params.period
        #self.addminperiod(self.params.period)
        self.up = []
        self.down = []
        print(f'--钱德动量摆动指标cmo动量天数--{self.cmo_days}')

    def next(self):
        up_sn = 0
        down_sn = 0
        cmo=0
        # 2. 自行计算， 同 CMO = ta.cmo(close, length=n, talib=False)
        diff = self.data.close[-1] - self.data.close[-2]
        if diff > 0:
            self.up.append(diff)
            self.down.append(0.0)
        elif diff < 0:
            self.up.append(0.0)
            self.down.append(abs(diff))
        else:
            self.up.append(0.0)
            self.down.append(0.0)

        # 计算up
        up_n = np.array(self.up)
        up_n1 = up_n[::-1]
        up_sn = up_n1[:self.cmo_days].sum()
        # 计算down
        down_n = np.array(self.down)
        down_n1 = down_n[::-1]
        down_sn = down_n1[:self.cmo_days].sum()
        # 计算 cmo
        if len(down_n)>=self.cmo_days:
            cmo = (up_sn - down_sn)/(up_sn+down_sn)*100

        self.lines.cmo[0] = cmo


