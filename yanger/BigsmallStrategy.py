import pandas
import collections
import backtrader as bt
from DaysMomentum import *
from ChandeMomentumOscillator import *


class BigsmallStrategy(bt.Strategy):
    params = (('ma_period', 30),
              ('printlog', False),
              ('traderatio', 0.95),
              ('is_sizeadding', False),
              ('is_loggingpos', False),
              ('profit_ratio_of_sizeadding', 0.1),
              )

    def log(self, txt, dt=None):
        #Logging function for this strategy
        if self.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):

        self.printlog = self.params.printlog
        self.period = self.params.ma_period
        self.trade_ratio = self.params.traderatio
        self.is_size_adding = self.params.is_sizeadding
        self.is_logging_pos = self.params.is_loggingpos
        self.profit_ratio_of_size_adding = self.params.profit_ratio_of_sizeadding

        # 初始化交易指令、买卖价格和手续费
        self.order = None
        self.buyprice = None
        self.buycomm = None
        #初始化
        self.flag_size_adding = 0
        self.momentum_days = self.period   # 动量天数
        self.big_data = self.datas[0]
        self.small_data = self.datas[1]
        print('--动量天数--')
        print(self.period)

        # 动量指标
        self.big_mom = DaysMomentum(self.datas[0], period=self.momentum_days)
        self.small_mom = DaysMomentum(self.datas[1], period=self.momentum_days)

        self.big_cmo = ChandeMomentumOscillator(self.datas[0], period=self.momentum_days)
        self.small_cmo = ChandeMomentumOscillator(self.datas[1], period=self.momentum_days)

    def prenext(self):
        pass
    def next(self):
        # 数据定义
        big_mom = 0  # big动量
        small_mom = 0  # small动量

        pos_pnl = 0 #持仓浮动收益
        pos_pnl_ratio = 0.0  #持仓浮动收益率
        big_pos = self.getposition(self.big_data).size
        small_pos = self.getposition(self.small_data).size

        # 策略准备
        big_mom_greater_small = small_mom_less_big = self.big_mom[0] > self.small_mom[0]
        big_mom_less_small = small_mom_greater_big = self.big_mom[0] < self.small_mom[0]
        big_mom_greater_small_yesterday = small_mom_less_big_yesterday = self.big_mom[-1] > self.small_mom[-1]
        big_mom_less_small_yesterday = small_mom_greater_big_yesterday = self.big_mom[-1] < self.small_mom[-1]

        big_mom_greater_0 = self.big_mom[0] > 0
        small_mom_greater_0 = self.small_mom[0] > 0
        all_mom_less_0 = (self.big_mom[0] < 0) & (self.small_mom[0] < 0)
        big_mom_greater_5 = self.big_mom[0] > 5
        small_mom_greater_5 = self.small_mom[0] > 5
        all_mom_less_5 = (self.big_mom[0] < 5) & (self.small_mom[0] < 5)

        # 策略2 - 钱德动量摆动指标
        big_cmo_greater_small = small_cmo_less_big = self.big_cmo[0] > self.small_cmo[0]
        big_cmo_less_small = small_cmo_greater_big = self.big_cmo[0] < self.small_cmo[0]
        big_cmo_greater_small_yesterday = small_cmo_less_big_yesterday = self.big_cmo[-1] > self.small_cmo[-1]
        big_cmo_less_small_yesterday = small_cmo_greater_big_yesterday = self.big_cmo[-1] < self.small_cmo[-1]

        big_cmo_greater_0 = self.big_cmo[0] > 0
        small_cmo_greater_0 = self.small_cmo[0] > 0
        all_cmo_less_0 = (self.big_cmo[0] < 0) & (self.small_cmo[0] < 0)
        big_cmo_greater_5 = self.big_cmo[0] > 5
        small_cmo_greater_5 = self.small_cmo[0] > 5
        big_cmo_less_f5 = self.big_cmo[0] < -5
        small_cmo_less_f5 = self.small_cmo[0] < -5

        all_cmo_less_f5 = big_cmo_less_f5 & small_cmo_less_f5
        big_cmo_greater_50 = self.big_cmo[0] > 50
        small_cmo_greater_50 = self.small_cmo[0] > 50
        big_cmo_less_50 = self.big_cmo[0] < 50
        small_cmo_less_50 = self.small_cmo[0] < 50
        big_cmo_greater_f50 = self.big_cmo[0] > -50
        small_cmo_greater_f50 = self.small_cmo[0] > -50
        big_cmo_less_f50 = self.big_cmo[0] < -50
        small_cmo_less_f50 = self.small_cmo[0] < -50
        big_cmo_crossdown_50 = (self.big_cmo[0] < 50) & (self.big_cmo[-1] > 50)
        small_cmo_crossdown_50 = (self.small_cmo[0] < 50) & (self.small_cmo[-1] > 50)
        big_cmo_crossup_f50 = (self.big_cmo[0] > -50) & (self.big_cmo[-1] < -50)
        small_cmo_crossup_f50 = (self.small_cmo[0] > -50) & (self.small_cmo[-1] < -50)

        # 策略条件
        # 差价策略
        # big long 条件
        trading_big_long = big_mom_greater_0 & big_mom_greater_small & big_mom_greater_small_yesterday
        # small long 条件
        trading_small_long = small_mom_greater_0 & small_mom_greater_big & small_mom_greater_big_yesterday
        # big short 条件
        trading_big_short = all_mom_less_0 & big_mom_less_small & big_mom_less_small_yesterday
        # small short 条件
        trading_small_short = all_mom_less_0 & small_mom_less_big & small_mom_less_big_yesterday

        # 钱德动量摆动指标（Chande Momentum Oscillator）
        # big long 条件
        #trading_big_long = big_cmo_greater_5 & big_cmo_greater_small & big_cmo_greater_small_yesterday & big_cmo_less_50
        # small long 条件
        #trading_small_long = small_cmo_greater_5 & small_cmo_greater_big & small_cmo_greater_big_yesterday & small_cmo_less_50
        # big short 条件
        #trading_big_short = all_cmo_less_0 & big_cmo_less_f5 & big_cmo_less_small & big_cmo_less_small_yesterday & big_cmo_greater_f50
        # small short 条件
        #trading_small_short = all_cmo_less_0 & small_cmo_less_f5 & small_cmo_less_big & small_cmo_less_big_yesterday & small_cmo_greater_f50

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
        # self.log(f'big_mom={big_mom:.2f},small_mom={small_mom:.2f}')
        # 检查是否有订单等待执行
        if self.order:
            return
        # 检查是否持仓
        if no_position:  # 没有持仓 开仓
            self.cash = self.broker.get_cash()
            # long big
            if trading_big_long:
                big_size = round(self.trade_ratio * self.cash / big_close,4)
                self.log('Order:open Long big, %.4f' % big_close)
                # 执行买入
                self.order = self.buy(self.big_data, big_size)
            # long small
            if trading_small_long:
                small_size = round(self.trade_ratio * self.cash / small_close, 4)
                self.log('Order:open Long small, %.4f' % small_close)
                # 执行买入
                self.order = self.buy(self.small_data, small_size)
            # short big
            if trading_big_short:
                big_size = round(self.trade_ratio * self.cash / big_close, 4)
                self.log('Order:open short big, %.4f' % big_close)
                # 执行买入
                self.order = self.sell(self.big_data, big_size)
            # short small
            if trading_small_short:
                small_size = round(self.trade_ratio * self.cash / small_close, 4)
                self.log('Order:open short small, %.4f' % small_close)
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
                    self.log('ORDER:close small, %.4f' % small_close)
                    self.order = self.close(self.small_data)
                    self.flag_size_adding = 0
                elif big_pos.size < 0:
                    self.log('ORDER:close big, %.4f' % big_close)
                    self.order = self.close(self.big_data)
                    self.flag_size_adding = 0
                else:
                    pass

            # small做多,先平仓
            if trading_small_long :
                # 平仓
                if big_has_pos:
                    self.log('ORDER:close big, %.4f' % big_close)
                    self.order = self.close(self.big_data)
                    self.flag_size_adding = 0
                elif small_pos.size < 0:
                    self.log('ORDER:close small, %.4f' % small_close)
                    self.order = self.close(self.small_data)
                    self.flag_size_adding = 0
                else:
                    pass

            #big做空 先平仓
            if trading_big_short:
                # 平仓
                if small_has_pos:
                    self.log('ORDER:close small, %.4f' % small_close)
                    self.order = self.close(self.small_data)
                    self.flag_size_adding = 0
                elif big_pos.size > 0:
                    self.log('ORDER:close big, %.4f' % big_close)
                    self.order = self.close(self.big_data)
                    self.flag_size_adding = 0
                else:
                    pass
            #small做空 先平仓
            if trading_small_short:
                # 平仓
                if big_has_pos:
                    self.log('ORDER:close big, %.4f' % big_close)
                    self.order = self.close(self.big_data)
                    self.flag_size_adding = 0
                elif small_pos.size > 0:
                    self.log('ORDER:close small, %.4f' % small_close)
                    self.order = self.close(self.small_data)
                    self.flag_size_adding = 0
                else:
                    pass


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

