import pytest
import allure
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger
from config import BASE_URL
from pages.login_page import LoginPage
from pages.header_component import HeaderComponent
from models.user import User, UserLoginAPIResponse

class TestLoginPage():
    @allure.epic("NewsPlatform")
    @allure.feature("Аутентификация")
    @allure.story("Успешный вход по логину и паролю")
    @allure.description("Проверяет, что валидный пользователь может авторизоваться и получить токен в localStorage")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Позитивный")
    @pytest.mark.smoke
    @pytest.mark.ui
    def test_valid_login(self, driver: webdriver.Firefox):
        login_page = LoginPage(driver)
        login_page.open()

        login_page.login("test@example.com", "password123")

        assert login_page.header.avatar_button.wait_until_visible(), "Аватар не появился после авторизации"
        assert driver.execute_script("return localStorage.getItem('token')"), "Токен не сохранился в localStorage после авторизации"

    @allure.epic("NewsPlatform")
    @allure.feature("Аутентификация")
    @allure.story("Валидные данные пользователя из API через GET запрос")
    @allure.description("Проверяет, что ответ /api/users/me соответствует схеме модели User")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("Позитивный")
    @pytest.mark.api
    def test_valid_answer_me_api(self, authenticated_page: webdriver.Firefox):
        with allure.step("Запрос /api/users/me с Bearer-токеном — проверка схемы через Pydantic-модель User"):
            token = authenticated_page.execute_script("return localStorage.getItem('token')")

            logger.info("Запрос /api/users/me с Bearer-токеном — проверка схемы через Pydantic-модель User")
            request = authenticated_page.request.get("https://archiscope.ru/api/users/me", headers={'Authorization': f'Bearer {token}'}).json()
            assert User(**request)

    @allure.epic("NewsPlatform")
    @allure.feature("Аутентификация")
    @allure.story("Корректность статуса и схемы ответа, через прямой POST запрос с параметрами пользователя")
    @allure.description("Проверяет, что валидный ответ статуса и схемы ответа из API при помощи прямого POST запроса")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("Позитивный")
    @pytest.mark.api
    def test_valid_answer_login_api(self, driver: webdriver.Firefox):
        with allure.step("Запрос POST /api/auth/login напрямую, username: test@example.com — проверка статуса и схемы ответа"):
            logger.info("Запрос POST /api/auth/login напрямую, username: test@example.com — проверка статуса и схемы ответа")
            request = driver.request.post(url="https://archiscope.ru/api/auth/login", form={"username": "test@example.com", "password": "password123"})
            assert request.status == 200, f"Ожидали статус 200, получили {request.status}"
            request = request.json()
            assert UserLoginAPIResponse(**request)

    @allure.epic("NewsPlatform")
    @allure.feature("Аутентификация")
    @allure.story("Некорректный логин")
    @allure.description("Проверяет, что сервер обрабатывает некорректный логин при отправке формы")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Негативный")
    @pytest.mark.regression
    @pytest.mark.ui
    def test_invalid_login(self, driver: webdriver.Firefox):
        login_page = LoginPage(driver)
        login_page.open()
        login_page.login("wrong@example.com", "wpassword")
        assert login_page.error_message.wait_until_visible(), "Сообщение об ошибке неверных учётных данных не появилось"

    @allure.epic("NewsPlatform")
    @allure.feature("Аутентификация")
    @allure.story("Пустое поле логина")
    @allure.description("Проверяет, что поле логина в форме авторизации настроено как обязательное")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("Негативный")
    @pytest.mark.parametrize("empty_field", ["email", "password"])
    @pytest.mark.regression
    @pytest.mark.ui
    def test_empty_fields_login(self, driver: webdriver.Firefox, empty_field):
        login_page = LoginPage(driver)
        login_page.open()

        if empty_field == "email":
            login_page.login("", "password123")
        elif empty_field == "password":
            login_page.login("test@example.com", "")

        validate_locator = getattr(login_page, f"{empty_field}_input").locator
        assert login_page.is_field_required(validate_locator), f"Поле {empty_field} является обязательным для заполнения"

    @allure.epic("NewsPlatform")
    @allure.feature("Аутентификация")
    @allure.story("Выход из аккаунта")
    @allure.description("Проверка корректности действий при выходе из аккаунта")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("Позитивный")
    @pytest.mark.regression
    @pytest.mark.ui
    def test_logout(self, authenticated_page: webdriver.Firefox):
        header_component = HeaderComponent(authenticated_page)
        header_component.logout()
        assert authenticated_page.execute_script("return localStorage.getItem('token')") is None, "Токен остался в localStorage после выхода из аккаунта"

    @allure.epic("NewsPlatform")
    @allure.feature("Аутентификация")
    @allure.story("Переход на страницу регистрации из формы авторизации")
    @allure.description("Проверка корректности ссылки на регистрацию под формой авторизации")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("Позитивный")
    @pytest.mark.regression
    @pytest.mark.ui
    def test_go_to_register(self, driver: webdriver.Firefox):
        login_page = LoginPage(driver)
        login_page.open()

        login_page.go_to_register()
        assert WebDriverWait(driver, 10).until(EC.url_to_be(BASE_URL + "/register")), "URL не изменился на /register после авторизации"
