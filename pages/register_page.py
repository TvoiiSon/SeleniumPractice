import allure
from selenium import webdriver
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from config import BASE_URL
from loguru import logger
from helpers.lazy_element import LazyElement

class RegisterPage(BasePage):
    URL = BASE_URL + "/register"

    def __init__(self, driver: webdriver.Firefox):
        super().__init__(driver)
        self.first_name_input = LazyElement(driver, (By.CSS_SELECTOR, 'input[name="first_name"]'))
        self.last_name_input = LazyElement(driver, (By.CSS_SELECTOR, 'input[name="last_name"]'))
        self.email_input = LazyElement(driver, (By.CSS_SELECTOR, 'input[name="email"]'))
        self.password_input = LazyElement(driver, (By.CSS_SELECTOR, 'input[name="password"]'))
        self.phone_input = LazyElement(driver, (By.CSS_SELECTOR, 'input[name="phone"]'))
        self.register_button = LazyElement(driver, (By.XPATH, "//button[text()='Зарегистрироваться']"))
        self.to_login_button = LazyElement(driver, (By.XPATH, "//a[@href='/login']"))

    def open(self):
        self.driver.get(self.URL)

    @allure.step("Прохождение регистрации с использованием Имени: {first_name}, Фамилии: {last_name}, Email: {email}")
    def register(self, first_name: str, last_name: str, email: str,
                 password: str, phone: str = ""):
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.email_input.fill(email)
        self.password_input.fill(password)
        if phone:
            self.phone_input.fill(phone)
        logger.info(f"Прохождение регистрации с использованием Имени: {first_name}, Фамилии: {last_name}, Email: {email}")
        self.register_button.click()

    @allure.step("Переход на страницу Авторизации по ссылке внизу формы Регистрации")
    def go_to_login(self):
        logger.info("Переход на страницу Авторизации по ссылке внизу формы Регистрации")
        self.to_login_button.click()
