import backtrader as bt
import math
import numpy as np
import talib as ta

# chaikinAD(SMA)交叉指标
# 离散指标(A/D)——Accumulation/Distribution是由价格和成交量的变化而决定
# 的。成交量在价格的变化中充当重要的权衡系数。系数越高（成交量），价格
# 的变化的分布就越能被这个技术指标所体现（在当前时段内）。
class chaikinAD(bt.Indicator):
    lines = ('chaikin',)
    params = (
        ('m', 12),
        ('n', 14),)

    def log(self, txt, dt=None):
        #Logging function for this strategy
        dt = dt or self.data.datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        #self.addminperiod(self.params.m)
        print(f'--chaikinAD --{self.params.m}:{self.params.n}')
        self.m = self.params.m
        self.n = self.params.n
        self.temps=[]
        self.ads=[]

    def next(self):
        diff = (self.data.close - self.data.low) - (self.data.high - self.data.close)
        mom = self.data.high - self.data.low
        temp = diff / mom * self.data.volume
        # 求和
        self.temps.append(temp)
        ad = math.fsum(self.temps)
        # 移动平均
        self.ads.append(ad)
        ads_n = np.array(self.ads)
        #self.log(ads_n)
        #ads_sma_m = ta.SMA(ads_n, self.m)
        #ds_sma_n = ta.SMA(ads_n, self.n)

        ads_sma_m = ta.EMA(ads_n, self.m)
        ads_sma_n = ta.EMA(ads_n, self.n)

        #self.log(ads_sma_m)
        ads_sma_m1 = ads_sma_m[::-1]
        ads_sma_n1 = ads_sma_n[::-1]
        #self.log(ads_sma_m1[0])
        #self.log(ads_sma_n1[0])
        #self.log('--')
        #self.log(ads_sma_n1[0])
        # chaikin
        chaikin = ads_sma_m1[0] - ads_sma_n1[0]
        #self.log(chaikin)
        self.lines.chaikin[0] = chaikin





