import pytest
import allure
from config import BASE_URL
from playwright.sync_api import Page, expect
from pages.register_page import RegisterPage
from pages.login_page import LoginPage
from helpers.data_generator import generate_user

class TestRegister:
    @allure.epic("NewsPlatform")
    @allure.feature("Регистрация")
    @allure.story("Успешная регистрация")
    @allure.description("Проверяет, что после регистрации с валидными данными происходит редирект на страницу логина")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Позитивный")
    @pytest.mark.smoke
    @pytest.mark.ui
    def test_valid_register(self, page: Page):
        register_page = RegisterPage(page)
        register_page.open()

        user = generate_user()
        register_page.register(**user)
        expect(page, message="После регистрации не произошёл редирект на страницу логина").to_have_url(BASE_URL + "/login")

    @allure.epic("NewsPlatform")
    @allure.feature("Регистрация")
    @allure.story("Пустое обязательное поле регистрации")
    @allure.description("Проверяет, что поля формы регистрации настроены как обязательные")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Негативный")
    @pytest.mark.parametrize("empty_field", ["first_name", "last_name", "email", "password"])
    @pytest.mark.regression
    @pytest.mark.ui
    def test_empty_fields_register(self, page: Page, empty_field):
        register_page = RegisterPage(page)
        register_page.open()

        user = generate_user()
        user[empty_field] = ""
        register_page.register(**user)
        validate_locator = getattr(register_page, f"{empty_field}_input")
        assert register_page.is_field_required(validate_locator), f"Поле {empty_field} является обязательным для заполнения"

    @allure.epic("NewsPlatform")
    @allure.feature("Регистрация")
    @allure.story("Слишком короткий пароль")
    @allure.description("Проверяет, что поле пароля отмечается как невалидное при пароле короче минимальной длины")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Негативный")
    @pytest.mark.regression
    @pytest.mark.ui
    def test_invalid_password_register(self, page: Page):
        register_page = RegisterPage(page)
        register_page.open()

        user = generate_user()
        user["password"] = "12345"
        register_page.register(**user)
        assert register_page.is_field_required(register_page.password_input), "Поле пароля должно быть отмечено как невалидное при слишком коротком пароле"

    @allure.epic("NewsPlatform")
    @allure.feature("Регистрация")
    @allure.story("Невалидный email вызывает краш страницы")
    @allure.description("Проверяет известный баг: страница падает с JS-ошибкой при регистрации с невалидным email")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Негативный")
    @pytest.mark.parametrize("invalid_email", ["qwe@qwe", "qwe@qwecom"])
    @pytest.mark.regression
    @pytest.mark.ui
    def test_invalid_fields_register(self, page: Page, invalid_email):
        collected = []

        def catch_it(item):
            collected.append(item)
            
        register_page = RegisterPage(page)
        register_page.open()

        user = generate_user()
        user["email"] = invalid_email
        page.on("pageerror", catch_it)
        register_page.register(**user)

        page.wait_for_load_state("networkidle")

        assert collected == [], f"Обнаружены JS-ошибки на странице при регистрации с невалидным email: {collected}"

    @allure.epic("NewsPlatform")
    @allure.feature("Регистрация")
    @allure.story("Пустой необязательный телефон")
    @allure.description("Проверяет, что регистрация успешно проходит с пустым необязательным полем телефона")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("Позитивный")
    @pytest.mark.regression
    @pytest.mark.ui
    def test_empty_phone_register(self, page: Page):
        register_page = RegisterPage(page)
        register_page.open()

        user = generate_user()
        user["phone"] = ""
        register_page.register(**user)
        expect(page, message="После регистрации с пустым необязательным телефоном не произошёл редирект на страницу логина").to_have_url(BASE_URL + "/login")

    @allure.epic("NewsPlatform")
    @allure.feature("Регистрация")
    @allure.story("Регистрация на уже занятый email")
    @allure.description("Проверяет, что при регистрации на уже зарегистрированный email показывается соответствующая ошибка")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Негативный")
    @pytest.mark.regression
    @pytest.mark.ui
    def test_exists_email_register(self, page: Page):
        register_page = RegisterPage(page)
        register_page.open()

        user = generate_user()
        user["email"] = "test@example.com"
        register_page.register(**user)
        expect(page.get_by_text("Email already registered"), message="Сообщение о том, что email уже зарегистрирован, не появилось").to_be_visible()

    @allure.epic("NewsPlatform")
    @allure.feature("Регистрация")
    @allure.story("Переход на страницу авторизации из формы регистрации")
    @allure.description("Проверяет корректность ссылки на страницу авторизации под формой регистрации")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("Позитивный")
    @pytest.mark.regression
    @pytest.mark.ui
    def test_to_login(self, page: Page):
        register_page = RegisterPage(page)
        register_page.open()

        register_page.go_to_login()
        expect(page, message="Переход по ссылке на страницу авторизации не произошёл").to_have_url(LoginPage.URL)
