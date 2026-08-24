import pytest
import allure
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.article_page import ArticlePage
from models.article import Comment
from helpers.data_generator import generate_comment
from loguru import logger

class TestArticle():
    @allure.epic("NewsPlatform")
    @allure.feature("Детальная страница новости")
    @allure.story("Успешное добавление комментария")
    @allure.description("Проверяет, что комментарий добавляется к статье и отображается на странице")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Позитивный")
    @pytest.mark.smoke
    @pytest.mark.ui
    def test_correct_create_comment(self, go_to_article_page: ArticlePage):
        comment = generate_comment()
        go_to_article_page.add_comment(comment)

        assert go_to_article_page.comment.get_by_text(comment, global_search=True, exact=True).wait_until_visible(), "Ожидали добавление комментария к новости, но комментарий не добавился"

    @allure.epic("NewsPlatform")
    @allure.feature("Детальная страница новости")
    @allure.story("Пустое поле комментария")
    @allure.description("Проверяет, что поле комментария в форме добавления настроено как обязательное")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Негативный")
    @pytest.mark.regression
    @pytest.mark.ui
    def test_incorrect_create_comment(self, go_to_article_page: ArticlePage):
        go_to_article_page.add_comment("")
        assert go_to_article_page.is_field_required(go_to_article_page.comment_input.locator), "Поле для содержимого комментария является обязательным для заполнения"

    @allure.epic("NewsPlatform")
    @allure.feature("Детальная страница новости")
    @allure.story("Отсутствие PII в комментариях")
    @allure.description("Проверяет, что ответ API с комментариями статьи не содержит email и phone автора")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Негативный")
    @pytest.mark.api
    def test_pii_article_id_returns(self, driver: webdriver.Firefox):
        with allure.step("Запрос комментариев статьи id=39 — проверка отсутствия email/phone автора в ответе"):
            logger.info("Запрос комментариев статьи id=39 — проверка отсутствия email/phone автора в ответе")
            request = driver.request.get("https://archiscope.ru/api/news/39/comments").json()

            for item in request:
                assert "email" not in item["author"] and "phone" not in item["author"], "Утечка полей email и phone на странице новости"

    @allure.epic("NewsPlatform")
    @allure.feature("Детальная страница новости")
    @allure.story("Валидная схема комментариев из API")
    @allure.description("Проверяет, что комментарии статьи соответствуют схеме модели Comment")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("Позитивный")
    @pytest.mark.api
    def test_valid_article_id_returns(self, driver: webdriver.Firefox):
        with allure.step("Запрос комментариев статьи id=39 — проверка схемы через Pydantic-модель Comment"):
            logger.info("Запрос комментариев статьи id=39 — проверка схемы через Pydantic-модель Comment")
            request = driver.request.get("https://archiscope.ru/api/news/39/comments").json()
            for item in request:
                assert Comment(**item)

    @allure.epic("NewsPlatform")
    @allure.feature("Детальная страница новости")
    @allure.story("Запрос комментариев несуществующей статьи")
    @allure.description("Проверяет, что запрос комментариев по несуществующему id статьи возвращает статус 404")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("Негативный")
    @pytest.mark.parametrize("article_id", [-1, 0, 9999])
    @pytest.mark.api
    def test_invalid_article_id_returns_404(self, driver: webdriver.Firefox, article_id):
        with allure.step(f"Запрос комментариев несуществующей статьи id={article_id} — ожидаем 404"):
            logger.info(f"Запрос комментариев несуществующей статьи id={article_id} — ожидаем 404")
            request = driver.request.get(f"https://archiscope.ru/api/news/{article_id}/comments")
            assert request.status == 404, f"Ожидали получить статус 404, получили {request.status}"
