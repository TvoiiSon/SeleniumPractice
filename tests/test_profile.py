import os

import pytest
import allure
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.profile_page import ProfilePage
from helpers.data_generator import generate_user
from config import BASE_URL
from loguru import logger

IMAGE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "test_data", "images.jpeg"))

class TestProfile:
    @allure.epic("NewsPlatform")
    @allure.feature("Профиль пользователя")
    @allure.story("Успешное обновление профиля")
    @allure.description("Проверяет, что профиль обновляется при заполнении полей валидными значениями")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Позитивный")
    @pytest.mark.smoke
    @pytest.mark.ui
    def test_valid_update_profile(self, go_to_profile_page: ProfilePage):
        for_profile = generate_user()
        go_to_profile_page.update_profile(**for_profile)

        assert go_to_profile_page.success_update.wait_until_visible(), "Сообщение об успешном обновлении профиля не появилось"

    @allure.epic("NewsPlatform")
    @allure.feature("Профиль пользователя")
    @allure.story("Обновление профиля с загрузкой фото")
    @allure.description("Проверяет, что загруженное фото профиля доступно по своему URL")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Позитивный")
    @pytest.mark.smoke
    @pytest.mark.ui
    def test_update_profile_with_set_photo(self, go_to_profile_page: ProfilePage):
        with allure.step("Запрос /api/users/me с Bearer-токеном — получение photo_path текущего пользователя"):
            for_profile = generate_user()
            go_to_profile_page.update_profile(**for_profile, image_path=IMAGE_PATH)

            token = go_to_profile_page.driver.execute_script("return localStorage.getItem('token')")
            logger.info("Запрос /api/users/me с Bearer-токеном — получение photo_path текущего пользователя")
            request = go_to_profile_page.driver.request.get("https://archiscope.ru/api/users/me", headers={'Authorization': f'Bearer {token}'}).json()

            logger.info(f"Проверка доступности загруженного фото профиля: {BASE_URL + request['photo_path']}")
            second_request = go_to_profile_page.driver.request.get(BASE_URL + request["photo_path"])
            assert second_request.status == 200, f"Ожидали статус 200 при запросе загруженного фото профиля, получили {second_request.status}"

            avatar_img = go_to_profile_page.header.avatar_button.get_by_alt_text("Avatar", global_search=True)
            assert avatar_img.evaluate("return arguments[0].complete && arguments[0].naturalWidth === 0;"), "Аватар в шапке загрузился, хотя ожидали 404 по фото профиля"

    @allure.epic("NewsPlatform")
    @allure.feature("Профиль пользователя")
    @allure.story("Пустое обязательное поле профиля")
    @allure.description("Проверяет, что поля first_name, last_name и email в форме профиля настроены как обязательные")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("Негативный")
    @pytest.mark.parametrize("empty_field", ["first_name", "last_name", "email"])
    @pytest.mark.regression
    @pytest.mark.ui
    def test_update_profile_without_required_fields(self, go_to_profile_page: ProfilePage, empty_field):
        for_profile = generate_user()
        for_profile[empty_field] = ""
        go_to_profile_page.update_profile(**for_profile)
        validate_locator = getattr(go_to_profile_page, f"{empty_field}_input").locator
        assert go_to_profile_page.is_field_required(validate_locator), f"Поле {empty_field} является обязательным для заполнения"

    @allure.epic("NewsPlatform")
    @allure.feature("Профиль пользователя")
    @allure.story("Пустое необязательное поле профиля")
    @allure.description("Проверяет, что обновление профиля успешно проходит с пустыми необязательными полями")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("Позитивный")
    @pytest.mark.parametrize("empty_field", ["phone", "password", "image_path"])
    @pytest.mark.regression
    @pytest.mark.ui
    def test_update_profile_without_notrequired_fields(self, go_to_profile_page: ProfilePage, empty_field):
        for_profile = generate_user()
        if empty_field != "image_path":
            for_profile[empty_field] = ""
        go_to_profile_page.update_profile(**for_profile)

        assert go_to_profile_page.success_update.wait_until_visible(), "Сообщение об успешном обновлении профиля не появилось при пустых необязательных полях"
        