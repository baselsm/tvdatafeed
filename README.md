# **TvDatafeed**

A simple TradingView historical Data Downloader

## Installation

This module is installed via pip:

```
pip install --upgrade --no-cache-dir git+https://github.com/StreamAlpha/tvdatafeed.git@develop
```

For usage instructions watch this video-

[![Watch the video](https://img.youtube.com/vi/qDrXmb2ZRjo/hqdefault.jpg)](https://youtu.be/qDrXmb2ZRjo)

---

## Usage

Import the packages and initialize with your tradingview username and password. If running for first time it will prompt chromedriver download, type 'y' and press enter.

```

from tvDatafeed import TvDatafeed,Interval

username = 'YourTradingViewUsername'
password = 'YourTradingViewPassword'



tv=TvDatafeed(username, password, chromedriver_path=None)


```

You may use without logging in, but in that case tradingview may limit the symbols and some symbols might not be available. To use it without logging in

```
tv = TvDatafeed()
```

To download the data use `tv.get_hist` method.

It accepts following arguments and returns pandas dataframe

```

(symbol: str, exchange: str = 'NSE', interval: Interval = Interval.in_daily, n_bars: int = 10, fut_contract: int | None = None) -> DataFrame)
```

for example-

```
nifty_data=tv.get_hist(symbol='NIFTY',exchange='NSE',interval=Interval.in_1_hour,n_bars=1000)


```

---

Following timeframes intervals are supported-

`Interval.in_1_minute `

`Interval.in_3_minute `

`Interval.in_5_minute `

`Interval.in_15_minute `

`Interval.in_30_minute `

`Interval.in_45_minute `

`Interval.in_1_hour `

`Interval.in_2_hour `

`Interval.in_3_hour `

`Interval.in_4_hour `

`Interval.in_daily `

`Interval.in_weekly `

`Interval.in_monthly`
