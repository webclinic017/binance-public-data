import pandas
import collections
import backtrader as bt
from DaysMomentum import *
from ChandeMomentumOscillator import *
from chaikinAD import *
from EMV import *
from KDJ import *

class TrandOneStrategy(bt.Strategy):
    params = (('m_period', 12),
              ('n_period', 14),
              ('printlog', True),
              ('is_loggingpos', False),
              )

    def log(self, txt, dt=None):
        #Logging function for this strategy
        if self.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):

        self.printlog = self.params.printlog
        self.m = self.params.m_period
        self.n = self.params.n_period

        self.is_logging_pos = self.params.is_loggingpos
        self.big_data = self.datas[0]
        self.small_data = self.datas[1]
        self.big_name = self.datas[0]._name
        self.small_name = self.datas[1]._name
        self.order = None
        self.trade_ratio = 0.95


        self.big_chaikin = chaikinAD(self.datas[0], m=self.m, n=self.n)
        self.small_chaikin = chaikinAD(self.datas[1], m=self.m, n=self.n)
        self.big_emv = EMV(self.datas[0],period=30).emv
        self.big_maemv = EMV(self.datas[0], period=30).maemv

        self.big_kdj = KDJ(self.datas[0], period=9, period_dfast=3, period_dslow=3)


    def prenext(self):
        pass
    def next(self):
        # 数据定义
        big_pos = self.getposition(self.big_data).size
        small_pos = self.getposition(self.small_data).size

        # 策略4 -chaikin
        big_chaikin_crossup_0 = (self.big_chaikin[0] > 0) & (self.big_chaikin[-1] < 0)
        big_chaikin_crossdown_0 = (self.big_chaikin[0] < 0) & (self.big_chaikin[-1] > 0)
        big_chaikin_greater_0 = (self.big_chaikin[0] > 0)
        big_chaikin_less_0 = (self.big_chaikin[0] < 0)
        big_chaikin_yesterday_greater_0 = (self.big_chaikin[-1] > 0)
        big_chaikin_yesterday_less_0 = (self.big_chaikin[-1] < 0)
        small_chaikin_crossup_0 = (self.small_chaikin[0] > 0) & (self.small_chaikin[-1] < 0)
        small_chaikin_crossdown_0 = (self.small_chaikin[0] < 0) & (self.small_chaikin[-1] > 0)
        small_chaikin_greater_0 = (self.small_chaikin[0] > 0)
        small_chaikin_less_0 = (self.small_chaikin[0] < 0)
        small_chaikin_yesterday_greater_0 = (self.small_chaikin[-1] > 0)
        small_chaikin_yesterday_less_0 = (self.small_chaikin[-1] < 0)
        big_chaikin_greater_small = self.big_chaikin[0] > self.small_chaikin[0]
        big_chaikin_less_small = self.big_chaikin[0] < self.small_chaikin[0]
        all_chaikin_less_0 = small_chaikin_less_0 & big_chaikin_less_0

        # EMV策略准备
        big_emv_crossup_0 = (self.big_emv[0] > 0) & (self.big_emv[-1] < 0)
        big_emv_crossdown_0 = (self.big_emv[0] < 0) & (self.big_emv[-1] > 0)
        big_emv_greater_0 = (self.big_emv[0] > 0)
        big_emv_less_0 = (self.big_emv[0] < 0)
        big_emv_yesterday_greater_0 = (self.big_emv[-1] > 0)
        big_emv_yesterday_less_0 = (self.big_emv[-1] < 0)

        #

        # 策略条件
        # big long 条件
        trading_big_long = big_emv_greater_0 & big_emv_yesterday_greater_0
        # small long 条件
        trading_small_long = False  # small_chaikin_greater_0 & small_chaikin_yesterday_greater_0 & big_chaikin_less_small
        # big short 条件
        trading_big_short = big_emv_less_0 & big_emv_yesterday_less_0
        # small short 条件
        trading_small_short = False  # all_chaikin_less_0 & small_chaikin_yesterday_less_0 & big_chaikin_greater_small

        # 强制平仓条件
        # big long 条件
        close_big = big_emv_crossdown_0 or big_emv_crossup_0
        # small long 条件
        close_small = False #small_chaikin_crossup_0 or small_chaikin_crossdown_0

        #交易准备
        self.big_size = 0
        self.small_size = 0
        no_position = (big_pos == 0) & (small_pos == 0)
        big_has_pos = big_pos != 0
        small_has_pos = small_pos != 0
        big_no_pos = big_pos == 0
        small_no_pos = small_pos == 0
        big_close = self.big_data.close[0]
        small_close = self.small_data.close[0]
        #self.log(f'big_chaikin={self.big_chaikin[0]:.2f},small_chaikin={self.small_chaikin[0]:.2f}')
        self.log(f'big_KDJ_K={self.big_kdj.K[0]:.2f} big_KDJ_D={self.big_kdj.D[0]:.2f   }')

        # 检查是否有订单等待执行
        if self.order:
            return

        # 检查是否持仓
        if no_position:  # 没有持仓 开仓
            self.cash = self.broker.get_cash()
            # long big
            if trading_big_long:
                big_size = round(self.trade_ratio * self.cash / big_close,4)
                self.log(f'Order:open Long {self.big_name}, {big_close:.4f}')
                # 执行买入
                self.order = self.buy(self.big_data, big_size)
            # long small
            if trading_small_long:
                small_size = round(self.trade_ratio * self.cash / small_close, 4)
                self.log(f'Order:open Long {self.small_name}, {small_close:.4f}')
                # 执行买入
                self.order = self.buy(self.small_data, small_size)
            # short big
            if trading_big_short:
                big_size = round(self.trade_ratio * self.cash / big_close, 4)
                self.log(f'Order:open Short {self.big_name}, {big_close:.4f}')
                # 执行买入
                self.order = self.sell(self.big_data, big_size)
            # short small
            if trading_small_short:
                small_size = round(self.trade_ratio * self.cash / small_close, 4)
                self.log(f'Order:open Short {self.small_name}, {small_close:.4f}')
                # 执行买入
                self.order = self.sell(self.small_data, small_size)

        #持仓日
        else:
            big_pos = self.getposition(self.big_data)
            small_pos = self.getposition(self.small_data)
            #big做多 ，先平仓
            if trading_big_long:
                #平仓
                if small_has_pos:
                    self.log(f'ORDER:close {self.small_name}, {small_close:.4f}')
                    self.order = self.close(self.small_data)
                    self.flag_size_adding = 0
                elif big_pos.size < 0:
                    self.log(f'ORDER:close {self.big_name}, {big_close:.4f}')
                    self.order = self.close(self.big_data)
                    self.flag_size_adding = 0
                else:
                    pass

            # small做多,先平仓
            if trading_small_long :
                # 平仓
                if big_has_pos:
                    self.log(f'ORDER:close {self.big_name}, {big_close:.4f}')
                    self.order = self.close(self.big_data)
                    self.flag_size_adding = 0
                elif small_pos.size < 0:
                    self.log(f'ORDER:close {self.small_name}, {small_close:.4f}')
                    self.order = self.close(self.small_data)
                    self.flag_size_adding = 0
                else:
                    pass

            #big做空 先平仓
            if trading_big_short:
                # 平仓
                if small_has_pos:
                    self.log(f'ORDER:close {self.small_name}, {small_close:.4f}')
                    self.order = self.close(self.small_data)
                    self.flag_size_adding = 0
                elif big_pos.size > 0:
                    self.log(f'ORDER:close {self.big_name}, {big_close:.4f}')
                    self.order = self.close(self.big_data)
                    self.flag_size_adding = 0
                else:
                    pass
            #small做空 先平仓
            if trading_small_short:
                # 平仓
                if big_has_pos:
                    self.log(f'ORDER:close {self.big_name}, {big_close:.4f}')
                    self.order = self.close(self.big_data)
                    self.flag_size_adding = 0
                elif small_pos.size > 0:
                    self.log(f'ORDER:close {self.small_name}, {small_close:.4f}')
                    self.order = self.close(self.small_data)
                    self.flag_size_adding = 0
                else:
                    pass

            # 强制平仓
            if close_big & big_has_pos:
                self.log(f'ORDER: force close {self.big_name}, {big_close:.4f}')
                self.order = self.close(self.big_data)
                self.flag_size_adding = 0
            if close_small & small_has_pos:
                self.log(f'ORDER: force close {self.small_name}, {small_close:.4f}')
                self.order = self.close(self.small_data)
                self.flag_size_adding = 0


    #记录交易执行情况
    def notify_order(self, order):
        # 如果order为submitted/accepted,返回空
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 如果order为buy/sell executed,报告价格结果
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'Trade:买入:价格:{order.executed.price:.2f},数量:{order.executed.size:.2f},'
                         f'价值:{order.executed.value:.2f},\n手续费:{order.executed.comm:.2f}')
                #self.log(f'Trade:Margin:{order.executed.margin},pnl:{order.executed.pnl:.2f}')
                #self.log(f'Trade:仓位:{order.executed.psize:.2f},持仓价格:{order.executed.pprice:.2f}')

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(f'Trade:卖出:价格:{order.executed.price:.2f},数量:{order.executed.size:.2f},'
                         f'价值:{order.executed.value:.2f},\n手续费:{order.executed.comm:.2f}')
                #self.log(f'Trade:Margin:{order.executed.margin},pnl:{order.executed.pnl:2f}')
                #self.log(f'Trade:仓位:{order.executed.psize:.2f},持仓价格:{order.executed.pprice:.2f}')
            self.bar_executed = len(self)
        # 如果指令取消/交易失败, 报告结果
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Trade:交易失败')
        self.order = None
        #self.log(f'现金余额:{self.broker.get_cash():.2f}')

    #记录交易收益情况
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'策略收益:毛收益:{trade.pnl:.2f}, 净收益:{trade.pnlcomm:.2f}')
        #self.log(f'现金余额:{self.broker.get_cash():.2f}')

    def notify_cashvalue(self, cash, value):
        #self.log(f'现金:{cash:.2f},资产:{value:.2f}')
        pass

    def notify_fund(self, cash, value, fundvalue, shares):
        #返回当前资金、总资产、基金价值、基金份额
        #self.log(f'现金:{cash:.2f},资产:{value:.2f},资产价值:{fundvalue:.2f},份额:{shares:.2f}')
        pass

    #回测前准备
    def start(self):
        pass

    #回测后总结
    def stop(self):
        self.log('期末资产 %.2f' % (self.broker.getvalue()))
        self.log('期末资金 %.2f' % (self.broker.getcash()))

