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
from Backtesting import *


date_range_start = '2022-01-01'
date_range_end = '2022-08-30'

A_name = 'ETH'
B_name = 'MATIC'

# ------------------------------------
data_path = '/Users/yanger/Downloads/Backtesting/'
A_File = data_path + A_name+'USDT-1d.csv'
B_File = data_path + B_name+'USDT-1d.csv'
report_title = A_name+'-'+B_name

# 是否展示画图
is_plot_show = 0
is_size_adding = False
is_logging_pos = False
# 投资金额
investment_fund = 1000
trade_ratio = 0.98  # 首次交易比例
commission_ratio = 0.00068
profit_ratio_of_size_adding = 0.1  # 加仓的盈利率

## 数据准备
s_date = datetime.datetime.strptime(date_range_start, '%Y-%m-%d').date()
e_date = datetime.datetime.strptime(date_range_end, '%Y-%m-%d').date()

# 读取数据
df_A = pd.read_csv(A_File,  parse_dates=True, header=None)
df_B = pd.read_csv(B_File,  parse_dates=True, header=None)

# 设置列名
#|Open time|Open|High|Low|Close|Volume|Close time|Quote asset volume|Number of trades|Taker buy base asset volume|Taker buy quote asset volume|Ignore| | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
df_A.columns = ['candle_end_time','open','High','Low','close','Volume','Close_time','QAV','NT','TBBAV','TBQAV','IG']
df_B.columns = ['candle_end_time','open','High','Low','close','Volume','Close_time','QAV','NT','TBBAV','TBQAV','IG']

# 转化日期格式
df_A['candle_end_time'] = pd.to_datetime(df_A['candle_end_time'], unit='ms').dt.date
df_B['candle_end_time'] = pd.to_datetime(df_B['candle_end_time'], unit='ms').dt.date
df_A['Close_time'] = pd.to_datetime(df_A['Close_time'], unit='ms').dt.date
df_B['Close_time'] = pd.to_datetime(df_B['Close_time'], unit='ms').dt.date

# 时间范围选择
df_A = df_A[(df_A['candle_end_time'] >= s_date) & (df_A['candle_end_time'] <= e_date)]
df_B = df_B[(df_B['candle_end_time'] >= s_date) & (df_B['candle_end_time'] <= e_date)]
df_A.index = pd.to_datetime(df_A['candle_end_time'],format="%Y-%m-%d",utc=True)
df_B.index = pd.to_datetime(df_B['candle_end_time'],format="%Y-%m-%d",utc=True)
del df_A['candle_end_time']
del df_B['candle_end_time']

# 数据ready
data_A = bt.feeds.PandasData(dataname=df_A)
data_B = bt.feeds.PandasData(dataname=df_B)

# 回测执行
cerebro_one = bt.Cerebro()
cerebro_two = bt.Cerebro()

#设定分析器
cerebro_one.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
cerebro_one.addanalyzer(bt.analyzers.AnnualReturn, _name='AnnualReturn')
cerebro_one.addanalyzer(bt.analyzers.DrawDown, _name='DrawDown')
cerebro_one.addanalyzer(bt.analyzers.TradeAnalyzer, _name='TradeAnalyzer')
cerebro_one.addanalyzer(bt.analyzers.TradeAnalyzer, _name='Transactions')
cerebro_one.addanalyzer(Tradelist, _name='trade_list1')

cerebro_two.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
cerebro_two.addanalyzer(bt.analyzers.AnnualReturn, _name='AnnualReturn')
cerebro_two.addanalyzer(bt.analyzers.DrawDown, _name='DrawDown')
cerebro_two.addanalyzer(bt.analyzers.TradeAnalyzer, _name='TradeAnalyzer')
cerebro_two.addanalyzer(bt.analyzers.TradeAnalyzer, _name='Transactions')
cerebro_two.addanalyzer(Tradelist, _name='trade_list2')

# 策略指定
cerebro_one.addstrategy(BigsmallStrategy, ma_period=30)
cerebro_two.addstrategy(TrandOneStrategy)

# 加载数据
cerebro_one.adddata(data_A, name=A_name)
cerebro_one.adddata(data_B, name=B_name)

cerebro_two.adddata(data_A, name=A_name)
cerebro_two.adddata(data_B, name=B_name)

# 设置最小成交量
cerebro_one.addsizer(bt.sizers.FixedSize, stake=0.001)
cerebro_two.addsizer(bt.sizers.FixedSize, stake=0.001)

# 设置启动资金
cerebro_one.broker.setcash(investment_fund)
cerebro_one.broker.setcommission(commission=commission_ratio)

cerebro_two.broker.setcash(investment_fund)
cerebro_two.broker.setcommission(commission=commission_ratio)

# 成交设置
cerebro_one.broker.set_coc(True) # 收盘成交
cerebro_one.broker.set_shortcash(False) # 现金管理支持做空

cerebro_two.broker.set_coc(True)  # 收盘成交
cerebro_two.broker.set_shortcash(False)  # 现金管理支持做空

# 回测，遍历所有数据
back1 = cerebro_one.run(tradehistory=True)
back2 = cerebro_two.run(tradehistory=True)

# 画图
if is_plot_show == 1: cerebro_one.plot(style='candel')

#策略评估
qs.extend_pandas()
strat1 = back1[0]
strat2 = back2[0]

portfolio_stats = strat1.analyzers.getbyname('pyfolio')
returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
returns.index = returns.index.tz_convert(None)
qs.reports.html(returns, output='stats.html', title=report_title)
qs.plots.snapshot(returns, title = report_title)

print(strat1.analyzers.AnnualReturn.get_analysis())
print(strat1.analyzers.DrawDown.get_analysis())
print(strat1.analyzers.TradeAnalyzer.get_analysis())
print(strat1.analyzers.Transactions.get_analysis())
print('--')
print(strat2.analyzers.AnnualReturn.get_analysis())
print(strat2.analyzers.DrawDown.get_analysis())
print(strat2.analyzers.TradeAnalyzer.get_analysis())
print(strat2.analyzers.Transactions.get_analysis())
#print(strat.analyzers.PositionsValue.get_analysis())

# 交易明细
trade_list1 = strat1.analyzers.trade_list1.get_analysis()
trade_list2 = strat2.analyzers.trade_list2.get_analysis()
#print(tabulate(trade_list1, headers="keys"))
#print(tabulate(trade_list2, headers="keys"))

# 总结
df_result = pd.DataFrame()

df_result.loc[0, 'name'] = '策略1'
df_result.loc[1, 'name'] = '策略2'
df_result.loc[0, 'datas'] = report_title
df_result.loc[1, 'datas'] = report_title

df_result.loc[0, 'date_start'] = date_range_start
df_result.loc[0, 'date_end'] = date_range_end
df_result.loc[1, 'date_start'] = date_range_start
df_result.loc[1, 'date_end'] = date_range_end

temp1 = strat1.analyzers.AnnualReturn.get_analysis()
temp2 = strat2.analyzers.AnnualReturn.get_analysis()
ROI_2021 = ROI_2020=ROI_2022=0
for i in temp1.items():
    if i[0] == 2020: ROI_2020 = i[1]
    if i[0] == 2021: ROI_2021 = i[1]
    if i[0] == 2022: ROI_2022 = i[1]
df_result.loc[0, 'ROI_2020'] = ROI_2020
df_result.loc[0, 'ROI_2021'] = ROI_2021
df_result.loc[0, 'ROI_2022'] = ROI_2022
for i in temp2.items():
    if i[0] == 2020: ROI_2020 = i[1]
    if i[0] == 2021: ROI_2021 = i[1]
    if i[0] == 2022: ROI_2022 = i[1]

df_result.loc[1, 'ROI_2020'] = ROI_2020
df_result.loc[1, 'ROI_2021'] = ROI_2021
df_result.loc[1, 'ROI_2022'] = ROI_2022

#
temp1 = strat1.analyzers.TradeAnalyzer.get_analysis()
temp2 = strat2.analyzers.TradeAnalyzer.get_analysis()
won=lost=0
for key, value in temp1.items():
    #print(key,value)
    if key == 'won':won = value['total']
    if key == 'lost':lost = value['total']
df_result.loc[0, '持仓次数'] = won+lost
df_result.loc[0, '盈利次数'] = won
df_result.loc[0, '亏损次数'] = lost
df_result.loc[0, '胜率'] = won/(won+lost)

for key, value in temp2.items():
    #print(key,value)
    if key == 'won':won = value['total']
    if key == 'lost':lost = value['total']
df_result.loc[1, '持仓次数'] = won+lost
df_result.loc[1, '盈利次数'] = won
df_result.loc[1, '亏损次数'] = lost
df_result.loc[1, '胜率'] = won/(won+lost)

temp1 = strat1.analyzers.DrawDown.get_analysis()
temp2 = strat2.analyzers.DrawDown.get_analysis()
max =len =mondydown=0
for key, value in temp1.items():
   #print(key,value)
   if key == 'max':
        max = value['drawdown']
        len = value['len']
        mondydown = value['moneydown']
df_result.loc[0, '最大回撤'] = max

for key, value in temp2.items():
   #print(key,value)
   if key == 'max':
        max = value['drawdown']
        len = value['len']
        mondydown = value['moneydown']
df_result.loc[1, '最大回撤'] = max

print(df_result.T)









