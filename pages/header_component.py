import re
import allure
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from helpers.lazy_element import LazyElement

AVATAR_INITIAL_PATTERN = re.compile(r"^[A-ZА-Я]$")

def _find_avatar_button(driver):
    for element in driver.find_elements(By.XPATH, "//span"):
        if AVATAR_INITIAL_PATTERN.match(element.text):
            return element
    return None

class HeaderComponent:
    def __init__(self, driver: webdriver.Firefox):
        self.driver = driver
        self.logo_link = LazyElement(driver, (By.XPATH, "//a[text()='📰 NewsPlatform']"))
        self.login_link = LazyElement(driver, (By.XPATH, "//a[href='/login']"))
        self.register_link = LazyElement(driver, (By.XPATH, "//a[href='/register']"))
        self.add_news_link = LazyElement(driver, (By.XPATH, "//a[text()='+ Добавить новость']"))
        self.avatar_button = LazyElement(driver, _find_avatar_button) # type: ignore
        self.profile_link = LazyElement(driver, (By.XPATH, "//a[text()='Профиль']"))
        self.logout_button = LazyElement(driver, (By.XPATH, "//button[text()='Выйти']"))

    @allure.step("Переход на страницу Профиля через нажатие по аватару, затем кнопке Профиль")
    def open_profile(self):
        logger.info("Переход на страницу Профиля через нажатие по аватару, затем кнопке Профиль")
        self.avatar_button.click()
        self.profile_link.click()

    @allure.step("Выход из аккаунта пользователя через нажатие по аватару, затем кнопке Выйти")
    def logout(self):
        logger.info("Выход из аккаунта пользователя через нажатие по аватару, затем кнопке Выйти")
        self.avatar_button.click()
        self.logout_button.click()
