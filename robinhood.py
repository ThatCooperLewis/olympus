# Get chrome and driver
# https://tecadmin.net/setup-selenium-chromedriver-on-ubuntu/

import email
from collections.abc import Callable
from queue import Queue
from threading import Thread
from time import sleep
import traceback
from os import getenv

from pyotp import TOTP
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from crosstower.models import Order, Balance
from utils.config import RobinhoodConfig, CrosstowerConfig
from utils.discord import DiscordWebhook
from utils.environment import env
from utils.logger import Logger

# TODO: 
# Public method for returning order status, to populate SQL table
# Should include current price & balance. Grab it from buy/sell modals
# 
# 
#
# Reload page if __fill_order fails
# 
# Make thread for keeping page active
# 
# Handle captcha modal in login()
# 
# Make test class, maybe redo old listener
# 
# Add unit tests for logging into BTC page   

class RobinhoodTrading:

    def __init__(self):
        self.mfa = TOTP(env.robinhood_mfa)
        self.chrome = Chrome(service=Service('./chromedriver'))
        self.chrome.implicitly_wait(5)

    #### Public methods ####

    def prepare_instance(self):
        self.chrome.get(RobinhoodConfig.BTC_URL)
        if not self.__is_logged_in():
            self.__login()
        self.__navigate_to_btc_page()
        self.__toggle_trade_quantity_type()

    def submit_order(self, side: str, quantity: float):
        if not self.__is_logged_in():
            self.__login()
        if not self.__is_navigated_to_btc_page():
            self.__navigate_to_btc_page()
        self.__fill_order(side, quantity)

    def instance_is_healthy(self):
        return self.__is_logged_in() and self.__is_navigated_to_btc_page()
    
    def close_instance(self):
        self.chrome.quit()

    #### Selenium helpers ####

    def __find_button_with_text(self, expected_text) -> WebElement:
        buttons = self.chrome.find_elements(by=By.XPATH, value=".//button[@type='button']")
        for button in buttons:
            if expected_text in  button.text:
                return button
        return None

    def __find_submit_button(self) -> WebElement:
        return self.chrome.find_element(by=By.XPATH, value="//button[@type='submit']")

    #### Trading methods ####

    def __toggle_trade_quantity_type(self):
        amount_toggle: WebElement = self.__find_button_with_text("USD")
        if amount_toggle is not None:
            amount_toggle.click()
            list_elements = self.chrome.find_elements(by=By.TAG_NAME, value="li")
            for element in list_elements:
                if "BTC" in element.text:
                    element.click()
                    break

    def __fill_order(self, side: str, quantity: float):
        # Click buy tab
        if side == "buy":
            element_text = "Buy BTC"
        elif side == "sell":
            element_text = "Sell BTC"
        else:
            raise Exception("Invalid side")
        try:
            buy_tab = self.chrome.find_element(by=By.XPATH, value=f"//*[contains(text(), '{element_text}')]")
            buy_tab.click()
            sleep(1)
            # Enter amount
            amount_field = self.chrome.find_element(by=By.XPATH, value=f'//input[@placeholder="0"]')
            amount_field.send_keys(str(quantity))
        except NoSuchElementException:
            print("Likely on wrong page")
        except Exception:
            print("Ugh something else happened")
        sleep(1)
        # Click "Review Order"
        review_button = self.__find_submit_button()
        review_button.click()
        sleep(2)
        # Click "Buy"
        submit_button = self.__find_submit_button()
        submit_button.click()
        # Return to default state
        sleep(5)
        # done_button = self.__find_button_with_text("Done")
        done_button = self.chrome.find_element(by=By.XPATH, value="//button[@type='submit']")
        done_button.click()

    #### Authentication methods ####
    
    def __is_logged_in(self) -> bool:
        try:
            self.chrome.find_element(by=By.XPATH, value=f'//a[@href="/messages"]')
            return True
        except:
            return False

    def __login(self):
        self.chrome.get(RobinhoodConfig.LOGIN_URL)
        email_field = self.chrome.find_element(by=By.NAME, value="username")
        if not email_field:
            raise Exception("Login page has not loaded")
        email_field.send_keys(env.robinhood_email)
        pw_field = self.chrome.find_element(by=By.NAME, value="password")
        pw_field.send_keys(env.robinhood_password)
        login_button = self.__find_submit_button()
        login_button.click()
        sleep(10)

        try:
            self.__enter_mfa_code()
        except NoSuchElementException:
            print("Login failed")
            input("Do captcha and press enter:")
            self.__enter_mfa_code()
        except Exception as e:
            raise e

        if not self.__is_logged_in():
            raise Exception("Login failed")

    def __enter_mfa_code(self):
        mfa_field = self.chrome.find_element(by=By.XPATH, value=f'//input[@placeholder="000000"]')
        mfa_field.click()
        mfa_field.send_keys(str(self.mfa.now()))
        continue_button = self.__find_button_with_text("Continue")
        continue_button.click()

    def __navigate_to_btc_page(self):
        if self.__is_navigated_to_btc_page():
            return
        # Search for BTC and navigate to page
        search = self.chrome.find_element(by=By.TAG_NAME, value="input")
        search.send_keys("BTC")
        sleep(3)
        options = self.chrome.find_elements(by=By.XPATH, value="//a[@role='option']")
        if len(options) == 0:
            raise Exception("No search results found for BTC!")
        for option in options:
            print("Got an option")
            print(option.text)
            if "Bitcoin" in option.text:
                option.click()
                break
        sleep(1)

    def __is_navigated_to_btc_page(self):
        try:
            self.chrome.find_element(by=By.XPATH, value="//*[contains(text(), 'Bitcoin (BTC) was founded in 2008')]")
            return True
        except:
            return False

# class Trading:

#     def __init__(self, symbol: str = CrosstowerConfig.DEFAULT_SYMBOL):
#         self.symbol = symbol
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         self.websocket: Connection = loop.run_until_complete(
#             SocketAPI.get_authenticated_socket()
#         )

#     def get_trading_balance(self, currencies: list = []) -> List[Balance]:
#         """
#         `getTradingBalance`

#         Returns the user's trading balance.

#         Requires the "Orderbook, History, Trading balance" API key Access Right.

#         Parameters
#         ----------
#         currencies : list
#             Optional string array of desired currencies. Output will only contain these currencies.

#         Returns
#         ----------
#         A list of `Balance` objects
#         """
#         result = self.__request_until_complete('spot_balances', {})
#         balance = []
#         count = len(currencies)
#         for coin in result:
#             if count == 0:
#                 balance.append(Balance(coin))
#             elif coin['currency'] in currencies:
#                 balance.append(Balance(coin))
#         return balance


# class OrderListener:

#     class OrderListenerObject:
        
#         def __init__(self, order: Order, on_submission: Callable[[Order], None] = None, on_complete: Callable[[Order], None] = None):
#             '''Container for Order object, along with callbacks for submission (before API response) and completion (after API response)'''
#             self.order = order
#             self.__on_submission: Callable[[Order], None] = on_submission
#             self.__on_complete: Callable[[Order], None] = on_complete
            
#         def on_submission(self):
#             if self.__on_submission:
#                 self.__on_submission(self.order)
            
#         def on_complete(self):
#             if self.on_complete:
#                 self.__on_complete(self.order)

#     def __init__(self, headless=False) -> None:
#         self.log = Logger.setup(self.__class__.__name__)
#         self.discord = DiscordWebhook(self.__class__.__name__)
#         self.__listener_thread: Thread = Thread(target=self.__listener_loop, daemon=True)
#         self.__queue: Queue = Queue()
#         self.__quit = False
#         self.__robhinhood = RobinhoodTrading()

#     def __listener_loop(self):
#         self.__robhinhood.prepare_instance()
#         try:
#             while not self.__quit:
#                 if self.__queue.qsize() > 0:
#                     order_object: self.OrderListenerObject = self.__queue.get()
#                     order_object.on_submission()
#                     self.__robhinhood.submit_order(side=order_object.order.side, quantity=order_object.order.quantity)
#                     order_object.on_complete()
#                 else:
#                     sleep(0.1)
#             self.log.debug('self.__orders_coroutine() is quitting')
#         except KeyboardInterrupt:
#             self.log.debug('KeyboardInterrupt during listener loop')
#         except Exception as e:
#             self.log.error(f'Exception in listener loop: {traceback.format_exc()}')
#             self.discord.send_alert(f'Exception in listener loop: {traceback.format_exc()}')

#     def submit_order(self, order: Order, on_submission: Callable[[Order], None], on_complete: Callable[[Order], None]):
#         """Put `Order` in queue for execution"""
#         order_object = self.OrderListenerObject(order, on_submission, on_complete)
#         self.__queue.put(order_object)

#     # Make the whole class behave like a thread

#     def start(self):
#         self.__listener_thread.start()

#     def end(self):
#         self.__quit = True

#     def join(self, timeout: int =None):
#         self.__quit = True
#         self.__listener_thread.join(timeout=timeout)

#     def is_alive(self):
#         return self.__listener_thread.is_alive()

rh = RobinhoodTrading()
try:
    aborted = False
    print('init')
    rh.prepare_instance()
    print('logged in')
    # rh.submit_order("buy", 0.0001)
    # print('order submit')
except KeyboardInterrupt:
    aborted = True
    rh.close_instance()
except Exception as e:
    if not aborted:
        raise e
finally:
    print("Done!")
    # rh.close_instance()