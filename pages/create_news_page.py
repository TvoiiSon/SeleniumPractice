import allure
from selenium import webdriver
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from config import BASE_URL
from loguru import logger
from helpers.lazy_element import LazyElement

class CreateNewsPage(BasePage):
    def __init__(self, driver: webdriver.Firefox):
        super().__init__(driver)
        self.title_input = LazyElement(driver, (By.CSS_SELECTOR, 'input[name="title"]'))
        self.subtitle_input = LazyElement(driver, (By.CSS_SELECTOR, 'input[name="subtitle"]'))
        self.text_input = LazyElement(driver, (By.CSS_SELECTOR, 'textarea[name="text"]'))
        self.tags_input = LazyElement(driver, (By.CSS_SELECTOR, 'input[name="tags"]'))
        self.image_input = LazyElement(driver, (By.CSS_SELECTOR, 'input[type="file"]'))
        self.create_button = LazyElement(driver, (By.XPATH, "//button[text()='Создать']"))

    @allure.step("Создание новости с Названием: {title}")
    def create_news(self, title: str, text: str, subtitle: str = "", tags: str = "", image_path: str = ""):
        self.title_input.fill(title)
        self.text_input.fill(text)
        if subtitle:
            self.subtitle_input.fill(subtitle)
        if tags:
            self.tags_input.fill(tags)
        if image_path:
            self.image_input.upload(image_path)
        logger.info(f"Создание новости с Названием: {title}")
        self.create_button.click()

    @allure.step("Переход на страницу создания новости")
    def open(self):
        logger.info("Переход на страницу создания новости")
        self.driver.get(BASE_URL + "/news/create")
