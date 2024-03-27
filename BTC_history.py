""" Candlestick Class """
import datetime as dt
import time
import ccxt
from matplotlib import pyplot as plt
import pandas as pd
import mplfinance as mpf

class CandlestickChart():
    """ Candlestick Chart """
    def __init__(self, exchange, symbol, timeframe, limit):
        self.figure = None
        self.__title = f"{exchange.capitalize()} - {symbol} - {timeframe} - Limit: {limit}"
        self.__exchange = None
        self.__symbol = symbol
        self.__timeframe = timeframe
        self.__limit = limit
        self.__show_volume = True
        self.__show_apds = True
        self.__show_mav = True

        self.get_exchange(exchange)

    def get_exchange(self, exchange):
        """ get right exchange """
        if exchange.lower() == 'binance':
            self.exchange = ccxt.binance()
        elif exchange.lower() == 'kraken':
            self.exchange = ccxt.kraken()

    @property
    def title(self):
        """ getter: title """
        return self.__title

    @property
    def exchange(self):
        """ getter: exchange """
        return self.__exchange

    @exchange.setter
    def exchange(self, exchange):
        """ setter: exchange """
        self.__exchange = exchange

    @property
    def symbol(self):
        """ getter: symbol """
        return self.__symbol

    @property
    def timeframe(self):
        """ getter: timeframe """
        return self.__timeframe

    @property
    def limit(self):
        """ getter: limit """
        return self.__limit
    
    @property
    def show_volume(self):
        """ getter: show_volume """
        return self.__show_volume
    
    @show_volume.setter
    def show_volume(self, show_volume):
        """ setter: show_volume """
        self.__show_volume = show_volume
        self.show_chart()

    @property
    def show_apds(self):
        """ getter: show_apds """
        return self.__show_apds
    
    @show_apds.setter
    def show_apds(self, show_apds):
        """ setter: show_apds """
        self.__show_apds = show_apds
        self.show_chart()

    @property
    def show_mav(self):
        """ getter: show_mav """
        return self.__show_mav
    
    @show_mav.setter
    def show_mav(self, show_mav):
        """ setter: show_mav """
        self.__show_mav = show_mav
        self.show_chart()

    def fetch_current_price(self):
        """Fetches current price from the exchange """
        ticker = self.exchange.fetch_ticker(self.symbol)
        return ticker['last']

    def fetch_data(self):
        """" Fetch data from exchange """
        start_date = dt.datetime.now() - dt.timedelta(days=self.limit)
        timestamp = int(time.mktime(start_date.timetuple())) * 1000
        since = timestamp

        ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.timeframe, since=since, limit=self.limit)
        self.df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'], unit='ms')
        self.df.set_index('timestamp', inplace=True)

    def plot_chart(self):
        """ Plot chart """
        self.fetch_data()
        self.current_price = self.fetch_current_price()

        typical_price = (self.df['close'] + self.df['high'] + self.df['low']) / 3
        PERIOD = 20
        std = self.df['close'].rolling(PERIOD).std() 
        middle_band = typical_price.rolling(PERIOD).mean()
        upper_band = middle_band + (2 * std)
        lower_band = middle_band - (2 * std)

        self.apds = [mpf.make_addplot(upper_band, color='blue'),
                mpf.make_addplot(middle_band, color='grey'),
                mpf.make_addplot(lower_band, color='red')]

        self.show_chart()

    def show_chart(self):
        """ Show Chart """
        if self.figure is not None:
            plt.close(self.figure)

        mav_settings = (3, 6, 9) if self.show_mav else ()

        title = f"{self.title} - Current Price: {self.current_price:.2f}"
        fig, axes = mpf.plot(self.df, type='candle', style='charles',
                          title=title,
                          ylabel='Price', volume=self.show_volume, addplot=self.apds if self.show_apds else [], mav=mav_settings, returnfig=True)

        self.figure = fig

    def get_figure(self):
        """ get the figure of the chart """
        if not self.figure:
            self.plot_chart()
        return self.figure

if __name__ == "__main__":
    chart = CandlestickChart(exchange='Binance', symbol='BTC/USD', timeframe='1d', limit=150)
    chart.plot_chart()
