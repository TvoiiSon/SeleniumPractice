import allure
from selenium import webdriver
from loguru import logger
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from helpers.lazy_element import LazyElement

class ArticlePage(BasePage):
    def __init__(self, driver: webdriver.Firefox, title: str):
        super().__init__(driver)
        self.title = title
        self.comment_input = LazyElement(driver, (By.XPATH, "//textarea[@placeholder='Оставьте комментарий']"))
        self.submit_comment_button = LazyElement(driver, (By.XPATH, "//button[text()='Отправить']"))
        self.heading = LazyElement(driver, (By.XPATH, f"//h1[text()='{title}']"))

    @allure.step("Создание комментария: {text}")
    def add_comment(self, text: str):
        self.comment_input.fill(text)
        logger.info(f"Создание комментария: {text} для новости с Названием: {self.title}")
        self.submit_comment_button.click()
