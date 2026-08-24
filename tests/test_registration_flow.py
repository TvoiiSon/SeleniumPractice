import pytest
import allure
from config import BASE_URL
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.register_page import RegisterPage
from pages.login_page import LoginPage
from helpers.data_generator import generate_user

class TestRegistrationFlow:
    @allure.epic("NewsPlatform")
    @allure.feature("Аутентификация")
    @allure.story("Полный цикл: регистрация → редирект → логин")
    @allure.description("Проверяет полный цикл от регистрации нового пользователя до успешной авторизации под ним")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Позитивный")
    @pytest.mark.regression
    @pytest.mark.ui
    def test_flow_register_login(self, driver: webdriver.Firefox):
        login_page = LoginPage(driver)
        register_page = RegisterPage(driver)

        register_page.open()

        user = generate_user()
        register_page.register(**user)

        assert WebDriverWait(driver, 10).until(EC.url_to_be(BASE_URL + "/login")), "После регистрации не произошёл редирект на страницу логина"

        login_page.login(user["email"], user["password"])

        assert login_page.header.avatar_button.wait_until_visible(), "Аватар не появился после авторизации"
