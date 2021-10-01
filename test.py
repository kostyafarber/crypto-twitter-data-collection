# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from IPython import get_ipython

# %%
import backtrader as bt
import yfinance as yf

import matplotlib.pyplot as plt
# %%
forex = yf.download(
                    "AUDUSD=X", 
                    start="2021-08-01", 
                    end="2021-09-17",
                    interval='5m')


# %%
forex.head()


# %%
# Create a Stratey
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        if self.dataclose[0] < self.dataclose[-1]:
            # current close less than previous close

            if self.dataclose[-1] < self.dataclose[-2]:
                # previous close less than the previous close

                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.buy()


# %%
cerebro = bt.Cerebro()

print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())


# %%
data = bt.feeds.PandasData(dataname = forex)


# %%
cerebro.addstrategy(TestStrategy)


cerebro.adddata(data)

cerebro.run()


# %%
cerebro.plot(style='bar')


# %%



