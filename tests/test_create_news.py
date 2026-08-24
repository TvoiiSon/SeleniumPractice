import pytest
import allure
from playwright.sync_api import Page, expect
from pages.create_news_page import CreateNewsPage
from helpers.data_generator import generate_article
from config import BASE_URL
from loguru import logger

class TestCreateNews:
    @allure.epic("NewsPlatform")
    @allure.feature("Создание новости")
    @allure.story("Успешное создание новости")
    @allure.description("Проверяет, что новость создаётся при заполнении всех полей валидными значениями и отображается в ленте")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Позитивный")
    @pytest.mark.smoke
    @pytest.mark.ui
    def test_correct_create_article(self, go_to_create_news_page: CreateNewsPage):
        article = generate_article()

        with go_to_create_news_page.page.expect_response("**/api/news/*") as response_info:
            go_to_create_news_page.create_news(**article)
        response = response_info.value

        assert response.status == 200, f"Ожидали получить статус 200, а получили {response.status}"
        expect(go_to_create_news_page.page.get_by_text(article["title"]), message="Ожидали создание новости, но случилась ошибка").to_be_visible()

    @allure.epic("NewsPlatform")
    @allure.feature("Создание новости")
    @allure.story("Создание новости с изображением")
    @allure.description("Проверяет, что загруженное при создании новости изображение доступно по своему URL")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Позитивный")
    @pytest.mark.regression
    @pytest.mark.ui
    def test_create_article_with_image(self, go_to_create_news_page: CreateNewsPage):
        article = generate_article()
        with allure.step(f"Поиск image_path для новости с Названием: {article['title']} через /api/news"):
            go_to_create_news_page.create_news(**article, image_path="test_data/images.jpeg")

            logger.info(f"Поиск image_path для новости с Названием: {article['title']} через /api/news")
            request = go_to_create_news_page.page.request.get("https://archiscope.ru/api/news").json()
            image_path = ""
            for item in request["items"]:
                if item["title"] == article["title"]:
                    image_path = item["image_path"]

            logger.info(f"Проверка доступности загруженной картинки: {BASE_URL + image_path}")
            second_request = go_to_create_news_page.page.request.get(BASE_URL + image_path)
            assert second_request.status == 200, f"Ожидали получить статус 200, а получили {second_request.status}"

    @allure.epic("NewsPlatform")
    @allure.feature("Создание новости")
    @allure.story("Пустое обязательное поле формы создания новости")
    @allure.description("Проверяет, что поля title и text в форме создания новости настроены как обязательные")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Негативный")
    @pytest.mark.parametrize("empty_field", ["title", "text"])
    @pytest.mark.regression
    @pytest.mark.ui
    def test_empty_required_field(self, go_to_create_news_page: CreateNewsPage, empty_field):
        article = generate_article()
        article[empty_field] = ""

        go_to_create_news_page.create_news(**article, image_path="test_data/images.jpeg")

        validate_locator = getattr(go_to_create_news_page, f"{empty_field}_input")
        assert go_to_create_news_page.is_field_required(validate_locator), f"Поле {empty_field} является обязательным для заполнения"

    @allure.epic("NewsPlatform")
    @allure.feature("Создание новости")
    @allure.story("Пустое необязательное поле формы создания новости")
    @allure.description("Проверяет, что создание новости успешно проходит с пустыми необязательными полями subtitle и tags")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("Позитивный")
    @pytest.mark.parametrize("empty_field", ["subtitle", "tags"])
    @pytest.mark.regression
    @pytest.mark.ui
    def test_empty_notrequired_field(self, go_to_create_news_page: CreateNewsPage, empty_field):
        article = generate_article()
        article[empty_field] = ""

        with go_to_create_news_page.page.expect_response("**/api/news/*") as response_info:
            go_to_create_news_page.create_news(**article)
        response = response_info.value

        assert response.status == 200, f"Ожидали получить статус 200, а получили {response.status}"
        expect(go_to_create_news_page.page.get_by_text(article["title"]), message="Ожидали создание новости с необязательными пустыми полями, но случилась ошибка").to_be_visible()
