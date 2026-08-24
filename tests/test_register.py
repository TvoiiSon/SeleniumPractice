import time

import pytest
import allure
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import BASE_URL
from pages.register_page import RegisterPage
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
    def test_valid_register(self, driver: webdriver.Firefox):
        register_page = RegisterPage(driver)
        register_page.open()

        user = generate_user()
        register_page.register(**user)
        assert WebDriverWait(driver, 10).until(EC.url_to_be(BASE_URL + "/login")), "URL не изменился на /login после авторизации"

    @allure.epic("NewsPlatform")
    @allure.feature("Регистрация")
    @allure.story("Пустое обязательное поле регистрации")
    @allure.description("Проверяет, что поля формы регистрации настроены как обязательные")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Негативный")
    @pytest.mark.parametrize("empty_field", ["first_name", "last_name", "email", "password"])
    @pytest.mark.regression
    @pytest.mark.ui
    def test_empty_fields_register(self, driver: webdriver.Firefox, empty_field):
        register_page = RegisterPage(driver)
        register_page.open()

        user = generate_user()
        user[empty_field] = ""
        register_page.register(**user)
        validate_locator = getattr(register_page, f"{empty_field}_input").locator
        assert register_page.is_field_required(validate_locator), f"Поле {empty_field} является обязательным для заполнения"

    @allure.epic("NewsPlatform")
    @allure.feature("Регистрация")
    @allure.story("Слишком короткий пароль")
    @allure.description("Проверяет, что поле пароля отмечается как невалидное при пароле короче минимальной длины")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Негативный")
    @pytest.mark.regression
    @pytest.mark.ui
    def test_invalid_password_register(self, driver: webdriver.Firefox):
        register_page = RegisterPage(driver)
        register_page.open()

        user = generate_user()
        user["password"] = "12345"
        register_page.register(**user)
        assert register_page.is_field_required(register_page.password_input.locator), "Поле пароля должно быть отмечено как невалидное при слишком коротком пароле"

    @allure.epic("NewsPlatform")
    @allure.feature("Регистрация")
    @allure.story("Невалидный email вызывает краш страницы")
    @allure.description("Проверяет известный баг: страница падает с JS-ошибкой при регистрации с невалидным email")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Негативный")
    @pytest.mark.parametrize("invalid_email", ["qwe@qwe", "qwe@qwecom"])
    @pytest.mark.regression
    @pytest.mark.ui
    def test_invalid_fields_register(self, driver: webdriver.Firefox, invalid_email):
        collected = []

        def catch_it(item):
            collected.append(item)
            
        register_page = RegisterPage(driver)
        register_page.open()

        user = generate_user()
        user["email"] = invalid_email
        driver.script.add_javascript_error_handler(catch_it)
        register_page.register(**user)

        time.sleep(1)

        assert collected == [], f"Обнаружены JS-ошибки на странице при регистрации с невалидным email: {collected}"

    @allure.epic("NewsPlatform")
    @allure.feature("Регистрация")
    @allure.story("Пустой необязательный телефон")
    @allure.description("Проверяет, что регистрация успешно проходит с пустым необязательным полем телефона")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("Позитивный")
    @pytest.mark.regression
    @pytest.mark.ui
    def test_empty_phone_register(self, driver: webdriver.Firefox):
        register_page = RegisterPage(driver)
        register_page.open()

        user = generate_user()
        user["phone"] = ""
        register_page.register(**user)
        assert WebDriverWait(driver, 10).until(EC.url_to_be(BASE_URL + "/login")), "После регистрации с пустым необязательным телефоном не произошёл редирект на страницу логина"

    @allure.epic("NewsPlatform")
    @allure.feature("Регистрация")
    @allure.story("Регистрация на уже занятый email")
    @allure.description("Проверяет, что при регистрации на уже зарегистрированный email показывается соответствующая ошибка")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Негативный")
    @pytest.mark.regression
    @pytest.mark.ui
    def test_exists_email_register(self, driver: webdriver.Firefox):
        register_page = RegisterPage(driver)
        register_page.open()

        user = generate_user()
        user["email"] = "test@example.com"
        register_page.register(**user)
        assert register_page.error_message.wait_until_visible(), "Сообщение о том, что email уже зарегистрирован, не появилось"
        
    @allure.epic("NewsPlatform")
    @allure.feature("Регистрация")
    @allure.story("Переход на страницу авторизации из формы регистрации")
    @allure.description("Проверяет корректность ссылки на страницу авторизации под формой регистрации")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("Позитивный")
    @pytest.mark.regression
    @pytest.mark.ui
    def test_to_login(self, driver: webdriver.Firefox):
        register_page = RegisterPage(driver)
        register_page.open()

        register_page.go_to_login()
        assert WebDriverWait(driver, 10).until(EC.url_to_be(BASE_URL + "/login")), "Переход по ссылке на страницу авторизации не произошёл"
