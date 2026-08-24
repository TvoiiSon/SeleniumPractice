import allure
from selenium import webdriver
from loguru import logger
from pages.header_component import HeaderComponent
from helpers.lazy_element import LazyElement

class BasePage:
    def __init__(self, driver: webdriver.Firefox):
        self.driver = driver
        self.header = HeaderComponent(driver)

    @allure.step("Проверка поля на обязательное")
    def is_field_required(self, locator) -> bool:
        logger.info("Проверка поля на обязательное")
        el = LazyElement(self.driver, locator)
        is_required = el.evaluate("return !arguments[0].checkValidity()")
        return is_required
    