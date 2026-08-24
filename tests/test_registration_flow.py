import pytest
import allure
from config import BASE_URL
from playwright.sync_api import Page, expect
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
    def test_flow_register_login(self, page: Page):
        login_page = LoginPage(page)
        register_page = RegisterPage(page)

        register_page.open()

        user = generate_user()
        register_page.register(**user)

        expect(page, message="После регистрации не произошёл редирект на страницу логина").to_have_url(BASE_URL + "/login")

        login_page.login(user["email"], user["password"])

        expect(login_page.header.avatar_button, message="Аватар не появился после авторизации новым пользователем").to_be_visible()
