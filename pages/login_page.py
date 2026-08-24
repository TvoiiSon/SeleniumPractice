import allure
from config import BASE_URL
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from helpers.lazy_element import LazyElement

class LoginPage(BasePage):
    URL = BASE_URL + "/login"

    def __init__(self, driver: webdriver.Firefox):
        super().__init__(driver)
        self.email_input = LazyElement(driver, (By.XPATH, "//input[@placeholder='user@example.com']"))
        self.password_input = LazyElement(driver, (By.XPATH, "//input[@placeholder='••••••']"))
        self.login_button = LazyElement(driver, (By.XPATH, "//button[text()='Войти']"))
        self.register_link = LazyElement(driver, (By.XPATH, "//a[@href='/register']"))
        self.error_message = LazyElement(driver, (By.CSS_SELECTOR, ".alert.alert-error"))

    def open(self):
        self.driver.get(self.URL)

    @allure.step("Прохождение авторизации с email: {email}")
    def login(self, email: str, password: str):
        self.email_input.fill(email)
        self.password_input.fill(password)
        logger.info(f"Прохождение авторизации с email: {email}")
        self.login_button.click()

    def get_error_message(self) -> str:
        return self.error_message.get_text()

    @allure.step("Переход на страницу Регистрации по ссылке внизу формы Авторизации")
    def go_to_register(self):
        logger.info("Переход на страницу Регистрации по ссылке внизу формы Авторизации")
        self.register_link.click()
