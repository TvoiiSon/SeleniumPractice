import allure
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from pages.base_page import BasePage
from pages.create_news_page import CreateNewsPage
from config import BASE_URL
from loguru import logger
from helpers.lazy_element import LazyElement

class NewsFeedPage(BasePage):
    URL = BASE_URL

    def __init__(self, driver: webdriver.Firefox):
        super().__init__(driver)
        self.logo_link = LazyElement(driver, (By.XPATH, "//a[text()='📰 NewsPlatform']"))
        self.login_link = LazyElement(driver, (By.XPATH, "//a[@href='/login']"))
        self.register_link = LazyElement(driver, (By.XPATH, "//a[@href='/register']"))
        self.add_news_link = LazyElement(driver, (By.XPATH, "//a[text()='+ Добавить новость']"))
        self.search_input = LazyElement(driver, (By.XPATH, "//input[@placeholder='Поиск...']"))
        self.clear_search_button = LazyElement(driver, (By.XPATH, "//button[text()='Очистить поиск']"))
        self.notfound_text = LazyElement(driver, (By.XPATH, "//*[contains(text(), 'Ничего не найдено')]"))
        self.next_page_button = LazyElement(driver, (By.XPATH, "//button[text()='»']"))
        self.prev_page_button = LazyElement(driver, (By.XPATH, "//button[text()='«']"))

    def open(self):
        self.driver.get(self.URL)

    def get_first_article_title(self, timeout: int = 10) -> str:
        WebDriverWait(self.driver, timeout).until(
            lambda d: len(d.find_elements(By.TAG_NAME, "h2")) > 0
        )
        return self.driver.find_elements(By.TAG_NAME, "h2")[0].text

    @allure.step("Поиск новости с Названием: {query}")
    def search(self, query: str):
        logger.info(f"Поиск новости с Названием: {query}")
        self.search_input.fill(query)

    @allure.step("Нажатие на кнопку очистки формы поиска")
    def clear_search(self):
        logger.info("Нажатие на кнопку очистки формы поиска")
        self.clear_search_button.click()

    @allure.step("Переход на страницу новости, по нажатию на ссылку в Названии: {title}")
    def open_article(self, title: str):
        logger.info(f"Переход на страницу новости, по нажатию на ссылку в Названии: {title}")
        LazyElement(self.driver, (By.XPATH, f"//a[text()='{title}']")).click()

    @allure.step("Переход на страницу пагинации №{number}")
    def go_to_page(self, number: str):
        logger.info(f"Переход на страницу пагинации №{number}")
        LazyElement(self.driver, (By.XPATH, f"//button[text()='{number}']")).click()

    @allure.step("Переход на страницу создания новости")
    def open_create_news_page(self) -> CreateNewsPage:
        logger.info("Переход на страницу создания новости")
        self.add_news_link.click()
        return CreateNewsPage(self.driver)
