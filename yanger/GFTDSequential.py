import backtrader as bt
import math
import talib as ta


class GFTDSequential(bt.Indicator):
    alias = ('GFTD', 'GFTDSequential',)
    lines = ('signal_buy', 'signal_sell', 'stop_price_4buy', 'stop_price_4sell')
    params = (('n1', 5), ('n2', 3), ('n3', 6),)

    def log(self, txt, dt=None):
        #Logging function for this strategy
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        #self.addminperiod(self.params.period + 2)
        self.n1 = self.params.n1
        self.n2 = self.params.n2
        self.n3 = self.params.n3
        print(f'GFTD.Indicator n1={self.n1},n2={self.n2},n3={self.n3}')

        self.start_len = self.n1

        hi, lo, op, cl = self.data.high, self.data.low, self.data.open, self.data.close
        self.hi, self.lo, self.op, self.cl = hi(0), lo(0), op(0), cl(0)
        #self.hi, self.lo, self.op, self.cl = hi(-1), lo(-1), op(-1), cl(-1)

        self.ud_last1 = 0
        self.ud = 0
        self.ud_sum = 0

        self.buy_ready_count = 0
        self.sell_ready_count = 0
        self.k1_close = 0
        self.temp = []

        self.do_buy = 0
        self.do_sell = 0

        self.open_long_stop_price = 9999999
        self.open_short_stop_price = 0

    def next(self):
        # 计算ud
        # 启动长度配置
        start_length = self.start_len * -1
        if self.cl[-1] > self.cl[start_length]:
            self.ud = 1
        elif self.cl[-1] < self.cl[start_length]:
            self.ud = -1
        else:
            self.ud = 0
        #累加ud
        if self.ud == self.ud_last1:
            self.ud_sum += self.ud
        else:
            self.ud_sum = 0
        # 信号配置
        # do sell
        if self.ud_sum >= self.n2:
            if self.ud_sum == self.n2+1:
                self.k1_close = self.cl[-1]
                #self.log(self.k1_close)
            #self.log(self.ud_sum)
            #self.log('prepare sell begin')
            # 计数条件
            condition1 = self.cl[-1] >= self.hi[-3]
            condition2 = self.hi[-1] > self.hi[-2]
            condition3 = self.cl[-1] > self.k1_close
            # 条件计数
            if condition1 & condition2 & condition3:
                self.sell_ready_count += 1
                #self.log(self.sell_ready_count)
                # 开空仓止损价格
                self.open_short_stop_price = max(self.hi[-1], self.open_short_stop_price)
                #self.log(self.open_short_stop_price)
                #
                if self.sell_ready_count == self.n3:
                    #self.log('do sell(open Short) - GFTD')
                    self.do_sell = 1
                else:
                    self.do_sell = 0
            else:
                self.sell_ready_count = 0  #
        # do buy
        elif self.ud_sum <= (self.n2*-1):
            #
            if self.ud_sum == self.n2*1-1:
                self.k1_close = self.cl[-1]
            #self.log(self.ud_sum)
            #self.log('prepare buy begin')
            # 计数条件
            condition1 = self.cl[-1] <= self.lo[-3]
            condition2 = self.lo[-1] < self.lo[-2]
            condition3 = self.cl[-1] < self.k1_close
            if condition1 & condition2 & condition3:
                self.buy_ready_count += 1
                #self.log(self.buy_ready_count)
                # 开多仓止损价格
                self.open_long_stop_price = min(self.lo[-1], self.open_long_stop_price)
                #self.log(self.open_long_stop_price)
                if self.buy_ready_count == self.n3:
                    #self.log('do buy(open Long) - GFTD')
                    self.do_buy = 1
                else:
                    self.do_buy = 0
            else:
                self.buy_ready_count = 0  #

        else:
            pass
        # 保存ud下个k线比较用
        self.ud_last1 = self.ud

        #
        self.lines.signal_buy[0] = self.do_buy
        self.lines.signal_sell[0] = self.do_sell
        self.lines.stop_price_4buy[0] = self.open_long_stop_price
        self.lines.stop_price_4sell[0] = self.open_short_stop_price




