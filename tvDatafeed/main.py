import datetime
import enum
import json
import logging
import os
import pickle
import random
import re
import shutil
import string
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from websocket import create_connection

logger = logging.getLogger(__name__)


class Interval(enum.Enum):
    in_1_minute = '1'
    in_3_minute = '3'
    in_5_minute = '5'
    in_15_minute = '15'
    in_30_minute = '30'
    in_45_minute = '45'
    in_1_hour = '1H'
    in_2_hour = '2H'
    in_3_hour = '3H'
    in_4_hour = '4H'
    in_daily = '1D'
    in_weekly = '1W'
    in_monthly = '1M'


class TvDatafeed:
    path = os.path.join(os.path.expanduser("~"), '.tv_datafeed/')
    headers = json.dumps({
        'Origin': 'https://data.tradingview.com'
    })

    def __assert_dir(self):
        if not os.path.exists(self.path):
            os.mkdir(self.path)
            if input('\n\ndo you want to install chromedriver automatically??\t').lower() == 'y':
                self.__install_chromedriver()

    def __install_chromedriver(self):

        os.system('pip install chromedriver-autoinstaller')

        import chromedriver_autoinstaller

        path = chromedriver_autoinstaller.install(cwd=True)

        if path is not None:
            self.chromedriver_path = os.path.join(
                self.path, 'chromedriver' + '.exe' if '.exe' in path else '')
            shutil.copy(path, self.chromedriver_path)

            try:
                time.sleep(1)
                os.remove(path)
            except:
                print(
                    f"unable to remove file '{path}', you may want to remove it manually")

        else:
            print(' unable to download chromedriver automatically.')

    @staticmethod
    def __get_token(username, password, chromedriver_path):
        caps = DesiredCapabilities.CHROME

        caps['goog:loggingPrefs'] = {'performance': 'ALL'}

        headless = True
        logger.info('refreshing tradingview token using selenium')
        logger.debug('launching chrome')
        options = Options()
        if headless:
            options.add_argument('--headless')

        options.add_argument("--start-maximized")

        options.add_argument('--disable-gpu')
        try:
            driver = webdriver.Chrome(
                chromedriver_path, desired_capabilities=caps, options=options)

            logger.debug('opening https://in.tradingview.com ')
            driver.set_window_size(1920, 1080)
            driver.get('https://in.tradingview.com')

            time.sleep(5)
            logger.debug('click sign in')
            driver.find_element_by_link_text('Sign in').click()

            time.sleep(5)
            logger.debug('click email')
            embutton = driver.find_element_by_class_name(
                'tv-signin-dialog__toggle-email')
            embutton.click()
            time.sleep(5)
            logger.debug('enter credentials and log in')
            username_input = driver.find_element_by_name('username')
            username_input.send_keys(username)
            password_input = driver.find_element_by_name('password')
            password_input.send_keys(password)
            submit_button = driver.find_element_by_class_name(
                'tv-button__loader')
            submit_button.click()
            time.sleep(5)
            logger.debug('opening chart')
            driver.get('https://www.tradingview.com/chart/')

            def process_browser_logs_for_network_events(logs):
                for entry in logs:
                    log = json.loads(entry["message"])["message"]
                    # if (
                    #     "Network.response" in log["method"]
                    #     or "Network.request" in log["method"]
                    #     or "Network.webSocket" in log["method"]
                    # )

                    if "Network.webSocketFrameSent" in log["method"]:
                        if 'set_auth_token' in log['params']['response']['payloadData'] and 'unauthorized_user_token' not in log['params']['response']['payloadData']:
                            yield log

            logs = driver.get_log("performance")
            events = process_browser_logs_for_network_events(logs)

            for event in events:
                x = event
                token = json.loads(x['params']['response']
                                   ['payloadData'].split('~')[-1])['p'][0]

            filename = os.path.join(os.path.split(__file__)[0], 'tv_token.pkl')
            with open(filename, 'wb') as f:
                pickle.dump({'date': datetime.date.today(), 'token': token}, f)
            logger.debug('token saved successfully')
            driver.quit()

        except Exception as e:
            logger.warn(f'error {e}')
            driver.quit()
            token = "unauthorized_user_token"
        return token

    def clear_cache(self):

        import shutil
        shutil.rmtree(self.path)
        print('cache cleared')

    def __init__(self, username=None, password=None, chromedriver_path=None) -> None:
        self.chromedriver_path = chromedriver_path
        self.__assert_dir()

        # read if token exists
        tokenfile = os.path.join(self.path, 'token')
        token = 'unauthorized_user_token'

        if username is not None and password is not None:
            if os.path.exists(tokenfile):
                with open(tokenfile, 'rb')as f:
                    contents = pickle.load(f)

                if contents['username'] == username and contents['password'] == password and contents['date'] == datetime.date.today():
                    token = contents['token']
                self.chromedriver_path = contents['chromedriver_path']

            if token is None:
                if self.chromedriver_path is None or not os.path.exists(self.chromedriver_path):
                    if input('\nchromedriver not found. do you want to autoinstall chromedriver?? y/n').lower() == 'y':
                        self.__install_chromedriver()

                token = self.__get_token(
                    username, password, self.chromedriver_path)
                contents = dict(username=username, password=password,
                                token=token, date=datetime.date.today(), chromedriver_path=self.chromedriver_path)

                with open(tokenfile, 'wb')as f:
                    pickle.dump(contents, f)
        else:
            logger.warn(
                'you are using nologin method, data you access may be limited')

        self.token = token
        self.ws = None
        self.session = self.__generate_session()
        self.chart_session = self.__generate_chart_session()

        self.ab_status = False

    def __create_connection(self):
        logging.debug('creating websocket connection')
        self.ws = create_connection(
            'wss://data.tradingview.com/socket.io/websocket', headers=self.headers)

    @staticmethod
    def __filter_raw_message(text):
        try:
            found = re.search('"m":"(.+?)",', text).group(1)
            found2 = re.search('"p":(.+?"}"])}', text).group(1)

            return found, found2
        except AttributeError:
            logger.error('error in filter_raw_message')

    @staticmethod
    def __generate_session():
        stringLength = 12
        letters = string.ascii_lowercase
        random_string = ''.join(random.choice(letters)
                                for i in range(stringLength))
        return "qs_" + random_string

    @staticmethod
    def __generate_chart_session():
        stringLength = 12
        letters = string.ascii_lowercase
        random_string = ''.join(random.choice(letters)
                                for i in range(stringLength))
        return "cs_" + random_string

    @staticmethod
    def __prepend_header(st):
        return "~m~" + str(len(st)) + "~m~" + st

    @staticmethod
    def __construct_message(func, param_list):
        return json.dumps({
            "m": func,
            "p": param_list
        }, separators=(',', ':'))

    def __create_message(self, func, paramList):
        return self.__prepend_header(self.__construct_message(func, paramList))

    def __send_raw_message(self, message):
        self.ws.send(self.__prepend_header(message))

    def __send_message(self, func, args):
        self.ws.send(self.__create_message(func, args))

    @staticmethod
    def __create_df(raw_data, symbol):
        out = re.search('"s":\[(.+?)\}\]', raw_data).group(1)
        x = out.split(',{\"')
        data = list()

        for xi in x:
            xi = re.split('\[|:|,|\]', xi)
            ts = datetime.datetime.fromtimestamp(float(xi[4]))
            data.append([ts, float(xi[5]), float(xi[6]),
                         float(xi[7]), float(xi[8]), float(xi[9])])

        data = pd.DataFrame(data, columns=[
                            'datetime', 'open', 'high', 'low', 'close', 'volume']).set_index('datetime')
        data.insert(0, 'symbol', value=symbol)
        return data

    @staticmethod
    def __format_symbol(symbol, exchange, contract: int = None):

        if ':' in symbol:
            pass
        elif contract is None:
            symbol = f'{exchange}:{symbol}'

        elif isinstance(contract, int):
            symbol = f'{exchange}:{symbol}{contract}!'

        else:
            raise ValueError('not a valid contract')

        return symbol

    def get_hist(self, symbol: str, exchange: str = 'NSE', interval: Interval = Interval.in_daily, n_bars: int = 10, fut_contract: int = None) -> pd.DataFrame:
        """get historical data

        Args:
            symbol (str): symbol name
            exchange (str, optional): exchange, not required if symbol is in format EXCHANGE:SYMBOL. Defaults to None.
            interval (str, optional): chart interval. Defaults to 'D'.
            n_bars (int, optional): no of bars to download, max 5000. Defaults to 10.
            fut_contract (int, optional): None for cash, 1 for continuous current contract in front, 2 for continuous next contract in front . Defaults to None.

        Returns:
            pd.Dataframe: dataframe with sohlcv as columns
        """
        # self = self()
        symbol = self.__format_symbol(
            symbol=symbol, exchange=exchange, contract=fut_contract)

        interval = interval.value

        # logger.debug("chart_session generated {}".format(self.chart_session))
        self.__create_connection()
        # self.__send_message("set_auth_token", ["unauthorized_user_token"])

        self.__send_message("set_auth_token", [self.token])
        self.__send_message("chart_create_session", [self.chart_session, ""])
        self.__send_message("quote_create_session", [self.session])
        self.__send_message("quote_set_fields", [self.session, "ch", "chp", "current_session", "description", "local_description", "language", "exchange", "fractional", "is_tradable",
                                                 "lp", "lp_time", "minmov", "minmove2", "original_name", "pricescale", "pro_name", "short_name", "type", "update_mode", "volume", "currency_code", "rchp", "rtc"])

        self.__send_message("quote_add_symbols", [
            self.session, symbol, {"flags": ['force_permission']}])
        self.__send_message("quote_fast_symbols", [self.session, symbol])

        self.__send_message("resolve_symbol", [self.chart_session, "symbol_1",
                                               '={\"symbol\":\"' + symbol + '\",\"adjustment\":\"splits\",\"session\":\"extended\"}'])
        self.__send_message(
            "create_series", [self.chart_session, "s1", "s1", "symbol_1", interval, n_bars])

        raw_data = ""

        logger.debug(f'getting data for {symbol}...')
        while True:
            try:
                result = self.ws.recv()
                raw_data = raw_data + result + "\n"
            except Exception as e:
                print(raw_data)
                logger.error(e)
                break

            if 'series_completed' in result:
                break

        return self.__create_df(raw_data, symbol)

    # TODO: send_to_amibroker:

    # TODO: login using requests
