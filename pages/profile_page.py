import allure
from selenium import webdriver
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from config import BASE_URL
from loguru import logger
from helpers.lazy_element import LazyElement

class ProfilePage(BasePage):
    URL = BASE_URL + "/profile"

    def __init__(self, driver: webdriver.Firefox):
        super().__init__(driver)
        self.first_name_input = LazyElement(driver, (By.CSS_SELECTOR, 'input[name="first_name"]'))
        self.last_name_input = LazyElement(driver, (By.CSS_SELECTOR, 'input[name="last_name"]'))
        self.email_input = LazyElement(driver, (By.CSS_SELECTOR, 'input[name="email"]'))
        self.phone_input = LazyElement(driver, (By.CSS_SELECTOR, 'input[name="phone"]'))
        self.password_input = LazyElement(driver, (By.CSS_SELECTOR, 'input[name="password"]'))
        self.image_input = LazyElement(driver, (By.CSS_SELECTOR, 'input[type="file"]'))
        self.save_button = LazyElement(driver, (By.XPATH, "//button[text()='Сохранить']"))
        self.success_update = LazyElement(driver, (By.XPATH, "//div[text()='Профиль обновлён']"))

    def open(self):
        self.driver.get(self.URL)

    @allure.step("Обновления профиля с новым Именем: {first_name}, Фамилией: {last_name}, Email: {email}")
    def update_profile(self, first_name: str, last_name: str, email: str, phone: str = "", password: str = "", image_path: str = ""):
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.email_input.fill(email)
        if phone:
            self.phone_input.fill(phone)
        if password:
            self.password_input.fill(password)
        if image_path:
            self.image_input.upload(image_path)
        logger.info(f"Обновления профиля с новым Именем: {first_name}, Фамилией: {last_name}, Email: {email}")
        self.save_button.click()
