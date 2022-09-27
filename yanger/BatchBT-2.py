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

#big_names = ['BTC']
small_names = ['FTM']

big_names = ['BTC', 'BNB', 'ETH', 'DOT',  'MATIC', 'SOL', 'UNI', 'ETC', 'NEAR', 'FTM', 'ADA', 'BCH', 'SAND', 'AXS', 'FLOW', 'RUNE', 'IOTA', 'NEAR', 'SUSHI']
#small_names = ['BTC', 'BNB', 'ETH', 'DOT', 'MATIC', 'SOL', 'UNI', 'ETC', 'NEAR', 'FTM', 'ADA', 'BCH',  'SAND', 'AXS', 'FLOW', 'RUNE', 'IOTA', 'NEAR', 'SUSHI']

#big_names = ['BTC', 'BNB', 'ETH', 'DOGE', 'DOT',  'MATIC', 'SOL', 'UNI', 'AVAX', 'ETC', 'NEAR', 'FTT', 'FTM', 'ADA', 'LINK', 'BCH', 'SAND', 'AAVE', 'AXS', 'FLOW', 'RUNE', 'IOTA', 'NEAR', 'SUSHI', 'EOS', 'MKR','CRV','CAKE','MANA']
#small_names = ['BTC', 'BNB', 'ETH', 'DOGE', 'DOT', 'MATIC', 'SOL', 'UNI', 'AVAX', 'ETC', 'NEAR', 'FTT', 'FTM', 'ADA', 'LINK', 'BCH',  'SAND', 'AAVE', 'AXS', 'FLOW', 'RUNE', 'IOTA', 'NEAR', 'SUSHI', 'EOS', 'MKR','CRV','CAKE','MANA']

annual = {}
df = pd.DataFrame()
did = []
AnnualReturn_2020 = 0
AnnualReturn_2021 = 0
AnnualReturn_2022 = 0
mom_days = range(30, 31) # 动量指标范围
m_range = range(20, 30)
n_range = range(30, 40)
x=0

# 循环开始
for b in big_names:
    for s in small_names:
        for m in m_range:
            for n in n_range:
                pair_kay= b+s+str(m)+','+str(n)
                if b == s: continue  # 跳过同样的
                if pair_kay not in did:  # 已经做过的不做
                    big_name = b
                    small_name = s
                    #temp = Backtesting.back_testing(Backtesting, big_name, small_name, mom_days=m)
                    temp = Backtesting.back_testing_one(Backtesting, big_name, small_name, m_period=m, n_period=n)
                    pair_name = big_name
                    AnnualReturn_2022 = 0
                    for i in temp.items():
                        if i[0] == 2022:
                            AnnualReturn_2022 = i[1]
                        if i[0] == 2021:
                            AnnualReturn_2021 = i[1]
                        if i[0] == 2020:
                            AnnualReturn_2020 = i[1]

                    df.loc[x, 'pairname'] = pair_name+'-'+str(m)+':'+str(n)
                    df.loc[x, 'mom_days'] = m
                    df.loc[x, '2022'] = AnnualReturn_2022
                    df.loc[x, '2021'] = AnnualReturn_2021
                    df.loc[x, '2020'] = AnnualReturn_2020

                x = x+1
                #将已经测试的记录
                did.append(b + s + str(m)+','+str(n))
                did.append(s + b + str(m)+','+str(n))
                print(AnnualReturn_2022)
                print(x)

df = df.sort_values(by='2022', ascending=False)
print(df.head(10))
df.to_csv('AnnualReturn2.csv', encoding='gbk', index=False)







