# Get chrome and driver
# https://tecadmin.net/setup-selenium-chromedriver-on-ubuntu/

import email
from time import sleep

from pyotp import TOTP
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from utils.config import RobinhoodConfig
from utils.environment import env


class Robinhood:

    def __init__(self):
        self.mfa = TOTP(env.robinhood_mfa)
        self.chrome = Chrome('./chromedriver')
        self.chrome.implicitly_wait(10)

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
        buy_tab = self.chrome.find_element(by=By.XPATH, value=f"//*[contains(text(), '{element_text}')]")
        buy_tab.click()
        sleep(1)
        # Enter amount
        amount_field = self.chrome.find_element(by=By.XPATH, value=f'//input[@placeholder="0"]')
        amount_field.send_keys(str(quantity))
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
        done_button = self.__find_button_with_text("Done")
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
        sleep(3)
        try:
            self.chrome.find_element(by=By.XPATH, value="//button[contains(text(), 'Start')]")
            # TODO: Make this not suck
            print("Login failed")
            input("Do captcha and press enter")
        except:
            pass

        # Populate MFA field & submit
        mfa_field = self.chrome.find_element(by=By.XPATH, value=f'//input[@placeholder="000000"]')
        mfa_field.click()
        mfa_field.send_keys(str(self.mfa.now()))
        continue_button = self.__find_button_with_text("Continue")
        continue_button.click()
        if not self.__is_logged_in():
            raise Exception("Login failed")

    def __navigate_to_btc_page(self):
        if self.__is_navigated_to_btc_page():
            return
        # Search for BTC and navigate to page
        search = self.chrome.find_element(by=By.TAG_NAME, value="input")
        search.send_keys("BTC")
        sleep(3)
        options = self.chrome.find_elements(by=By.XPATH, value="//div[@role='option']")
        for option in options:
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

rh = Robinhood()
print('init')
rh.prepare_instance()
print('logged in')
rh.submit_order("buy", 0.0001)
print('order submit')