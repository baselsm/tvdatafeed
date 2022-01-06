# **TvDatafeed**

A simple TradingView historical Data Downloader. Tvdatafeed allows downloading upto 5000 bars on any of the supported timeframe.

If you found the content useful and want to support my work, you can buy me a coffee!
[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/StreamAlpha)

## Installation

This module is installed via pip:

```sh
pip install tvdatafeed
```

or installing from github repo

```sh
pip install --upgrade --no-cache-dir git+https://github.com/StreamAlpha/tvdatafeed.git
```

For usage instructions, watch these videos-

v1.2 tutorial with installation and backtrader usage

[![Watch the video](https://img.youtube.com/vi/f76dOZW2gwI/hqdefault.jpg)](https://youtu.be/f76dOZW2gwI)

Full tutorial

[![Watch the video](https://img.youtube.com/vi/qDrXmb2ZRjo/hqdefault.jpg)](https://youtu.be/qDrXmb2ZRjo)

---

## Usage

Import the packages and initialize with your tradingview username and password. If running for first time it will prompt chromedriver download, type 'y' and press enter.

```python
from tvDatafeed import TvDatafeed, Interval

username = 'YourTradingViewUsername'
password = 'YourTradingViewPassword'



tv = TvDatafeed(username, password, chromedriver_path=None)
```

If auto login fails, you can try logging in manually by specifying `auto_login=False`

```python
tv = TvDatafeed(auto_login=False)
```

It will open TradingView website, you need to login manually. Once logged in return back to terminal and press 'enter', browser will automatically close. Whichever login method is used, login is required only once. **For detailed login precedure watch the videos shown above.**

You may use without logging in, but in some cases tradingview may limit the symbols and some symbols might not be available. To use it without logging in

```python
tv = TvDatafeed()
```

when using without login, following warning will be shown `you are using nologin method, data you access may be limited`

---

## Getting Data

To download the data use `tv.get_hist` method.

It accepts following arguments and returns pandas dataframe

```python
(symbol: str, exchange: str = 'NSE', interval: Interval = Interval.in_daily, n_bars: int = 10, fut_contract: int | None = None, extended_session: bool = False) -> DataFrame)
```

for example-

```python
# index
nifty_index_data = tv.get_hist(symbol='NIFTY',exchange='NSE',interval=Interval.in_1_hour,n_bars=1000)

# futures continuous contract
nifty_futures_data = tv.get_hist(symbol='NIFTY',exchange='NSE',interval=Interval.in_1_hour,n_bars=1000,fut_contract=1)

# crudeoil
crudeoil_data = tv.get_hist(symbol='CRUDEOIL',exchange='MCX',interval=Interval.in_1_hour,n_bars=5000,fut_contract=1)

# downloading data for extended market hours
extended_price_data = tv.get_hist(symbol="EICHERMOT",exchange="NSE",interval=Interval.in_1_hour,n_bars=500, extended_session=False)
```

---

## Calculating Indicators

Indicators data is not downloaded from tradingview. For that you can use [TA-Lib](https://github.com/mrjbq7/ta-lib). Check out this video for installation and usage instructions-

[![Watch the video](https://img.youtube.com/vi/0MeHXJm9HRk/hqdefault.jpg)](https://youtu.be/0MeHXJm9HRk)

---

## Supported Time Intervals

Following timeframes intervals are supported-

`Interval.in_1_minute`

`Interval.in_3_minute`

`Interval.in_5_minute`

`Interval.in_15_minute`

`Interval.in_30_minute`

`Interval.in_45_minute`

`Interval.in_1_hour`

`Interval.in_2_hour`

`Interval.in_3_hour`

`Interval.in_4_hour`

`Interval.in_daily`

`Interval.in_weekly`

`Interval.in_monthly`

---

## Troubleshooting

If you face any difficulty, you can reset this tvdatafeed using `clear_cache` method. You will need to login again after reset.

```python
tv.clear_cache()
```

if still issue persists checj out [#26 (comment)](https://github.com/StreamAlpha/tvdatafeed/issues/26#issuecomment-912619033), works on all platforms.

---

## Read this before creating an issue

Before creating an issue in this library, please follow the following steps.

1. Search the problem you are facing is already asked by someone else. There might be some issues already there, either solved/unsolved related to your problem. Go to [issues](https://github.com/StreamAlpha/tvdatafeed/issues) page, use `is:issue` as filter and search your problem. ![image](https://user-images.githubusercontent.com/59556194/128167319-2654cfa1-f718-4a52-82f8-b0c0d26bf4ef.png)
2. If you feel your problem is not asked by anyone or no issues are related to your problem, then create a new issue.
3. Describe your problem in detail while creating the issue. If you don't have time to detail/describe the problem you are facing, assume that I also won't be having time to respond to your problem.
4. Post a sample code of the problem you are facing. If I copy paste the code directly from issue, I should be able to reproduce the problem you are facing.
5. Before posting the sample code, test your sample code yourself once. Only sample code should be tested, no other addition should be there while you are testing.
6. Have some print() function calls to display the values of some variables related to your problem.
7. Post the results of print() functions also in the issue.
8. Use the insert code feature of github to inset code and print outputs, so that the code is displyed neat. !
9. If you have multiple lines of code, use tripple grave accent ( ``` ) to insert multiple lines of code. [Example:](https://docs.github.com/en/github/writing-on-github/creating-and-highlighting-code-blocks) ![image](https://user-images.githubusercontent.com/59556194/128167963-90edc379-6a15-4363-911f-5bfe1e92ef56.png)
