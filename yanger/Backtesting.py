from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime  # 用于datetime对象操作
import os.path  # 用于管理路径
import sys  # 用于在argvTo[0]中找到脚本名称
import backtrader as bt # 引入backtrader框架
import pandas as pd
import matplotlib.dates
import quantstats as qs
from tabulate import tabulate
import collections
import collections.abc
from BigsmallStrategy import *
from TradelistAnalyzer import *
from TradeOneStrategy import *


class Backtesting():
    a_name = 'BTC'
    b_name = 'ETH'
    date_range_start = '2020-01-01'
    date_range_end = '2022-08-30'

    def __init__(self):
        pass

    def data_load(self, big_name='BTC', small_name='ETH', folder_path=''):
        self.a_name = big_name
        self.b_name = small_name
        self.fpath = folder_path #/Users/yanger/Downloads/Backtesting/
        A_File =  self.fpath + self.a_name + 'USDT-1d.csv'
        B_File = self.fpath +  self.b_name + 'USDT-1d.csv'


        s_date = datetime.datetime.strptime(self.date_range_start, '%Y-%m-%d').date()
        e_date = datetime.datetime.strptime(self.date_range_end, '%Y-%m-%d').date()

        # 读取数据
        df_A = pd.read_csv(A_File, parse_dates=True, header=None)
        df_B = pd.read_csv(B_File, parse_dates=True, header=None)

        # 设置列名
        # |Open time|Open|High|Low|Close|Volume|Close time|Quote asset volume|Number of trades|Taker buy base asset volume|Taker buy quote asset volume|Ignore| | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
        df_A.columns = ['candle_end_time', 'open', 'High', 'Low', 'close', 'Volume', 'Close_time', 'QAV', 'NT', 'TBBAV',
                        'TBQAV', 'IG']
        df_B.columns = ['candle_end_time', 'open', 'High', 'Low', 'close', 'Volume', 'Close_time', 'QAV', 'NT', 'TBBAV',
                        'TBQAV', 'IG']

        # 转化日期格式
        df_A['candle_end_time'] = pd.to_datetime(df_A['candle_end_time'], unit='ms').dt.date
        df_B['candle_end_time'] = pd.to_datetime(df_B['candle_end_time'], unit='ms').dt.date
        df_A['Close_time'] = pd.to_datetime(df_A['Close_time'], unit='ms').dt.date
        df_B['Close_time'] = pd.to_datetime(df_B['Close_time'], unit='ms').dt.date

        # 时间范围选择
        df_A = df_A[(df_A['candle_end_time'] >= s_date) & (df_A['candle_end_time'] <= e_date)]
        df_B = df_B[(df_B['candle_end_time'] >= s_date) & (df_B['candle_end_time'] <= e_date)]
        df_A.index = pd.to_datetime(df_A['candle_end_time'], format="%Y-%m-%d", utc=True)
        df_B.index = pd.to_datetime(df_B['candle_end_time'], format="%Y-%m-%d", utc=True)
        del df_A['candle_end_time']
        del df_B['candle_end_time']
        #print(df_A.head())
        return df_A, df_B

    def back_testing(self, big_name='BTC', small_name='ETH', mom_days=30):

        mkt_data= self.data_load(self,big_name,small_name,folder_path='/Users/yanger/Downloads/Backtesting/')
        df_A = mkt_data[0]
        df_B = mkt_data[1]

        investment_fund = 1000
        commission_ratio = 0.0004
        report_title = big_name +'-'+small_name

        cerebro = bt.Cerebro()
        #设定分析器
        cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='AnnualReturn')

        #策略指定
        cerebro.addstrategy(BigsmallStrategy, ma_period=mom_days)


        #加载数据
        data_A = bt.feeds.PandasData(dataname=df_A)
        data_B = bt.feeds.PandasData(dataname=df_B)
        # 在Cerebro中添加价格数据
        cerebro.adddata(data_A, name='Big')
        cerebro.adddata(data_B, name='Small')

        cerebro.addsizer(bt.sizers.FixedSize, stake=0.001)
        # 设置启动资金
        cerebro.broker.setcash(investment_fund)
        cerebro.broker.setcommission(commission=commission_ratio)
        #收盘成交
        cerebro.broker.set_coc(True) #收盘成交
        cerebro.broker.set_shortcash(False) ##现金管理支持做空

        # 回测，遍历所有数据
        back = cerebro.run()
        print(report_title + '-'+str(mom_days))

        #策略评估
        qs.extend_pandas()
        strat = back[0]

        #portfolio_stats = strat.analyzers.getbyname('pyfolio')
        #returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
        #returns.index = returns.index.tz_convert(None)

        temp = strat.analyzers.AnnualReturn.get_analysis()
        AnnualReturn_2022 = 0
        for i in temp.items():
            if i[0] == 2022:
                AnnualReturn_2022 = i[1]

        return temp

    def back_testing_one(self, big_name='BTC', small_name='ETH', m_period=14, n_period=12):

        self.fpath = '/Users/yanger/Downloads/Backtesting/'
        mkt_data = self.data_load(self, big_name, small_name, folder_path=self.fpath)
        df_A = mkt_data[0]
        df_B = mkt_data[1]

        investment_fund = 1000
        commission_ratio = 0.0004
        report_title = big_name

        cerebro = bt.Cerebro()
        #设定分析器
        cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='AnnualReturn')
        #cerebro.addanalyzer(Tradelist, _name='trade_list')
        #策略指定
        cerebro.addstrategy(ChaikinStrategy,m_period=m_period, n_period=n_period)


        #加载数据
        data_A = bt.feeds.PandasData(dataname=df_A)
        data_B = bt.feeds.PandasData(dataname=df_B)

        # 在Cerebro中添加价格数据
        cerebro.adddata(data_A, name=big_name)
        cerebro.adddata(data_B, name=small_name)

        cerebro.addsizer(bt.sizers.FixedSize, stake=0.001)
        # 设置启动资金
        cerebro.broker.setcash(investment_fund)
        cerebro.broker.setcommission(commission=commission_ratio)
        #收盘成交
        cerebro.broker.set_coc(True) #收盘成交
        cerebro.broker.set_shortcash(False) ##现金管理支持做空

        # 回测，遍历所有数据
        back = cerebro.run(tradehistory=True)
        print(report_title + '-'+str(m_period)+':'+str(n_period))

        #策略评估
        qs.extend_pandas()
        strat = back[0]

        #portfolio_stats = strat.analyzers.getbyname('pyfolio')
        #returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
        #returns.index = returns.index.tz_convert(None)

        #trade_list = strat.analyzers.trade_list.get_analysis()
        #print(tabulate(trade_list, headers="keys"))

        temp = strat.analyzers.AnnualReturn.get_analysis()
        AnnualReturn_2022 = 0
        for i in temp.items():
            if i[0] == 2022:
                AnnualReturn_2022 = i[1]

        return temp