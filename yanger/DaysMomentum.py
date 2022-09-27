import backtrader as bt
import math

class DaysMomentum(bt.Indicator):
    lines = ('mom',)
    params = (('period', 14),)

    def __init__(self):
        #self.addminperiod(self.params.period)
        self.mom_days = self.params.period
        self.begin = -1
        self.end = self.begin - self.mom_days
        print(f'--mom动量天数--{self.mom_days}')

    def next(self):
        self.lines.mom[0] = (self.data.close[self.begin] - self.data.close[self.end]) / self.data.close[self.end] * 100

