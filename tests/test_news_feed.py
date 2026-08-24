import pytest
import allure
from selenium import webdriver
from pages.news_feed_page import NewsFeedPage
from pages.article_page import ArticlePage
from models.article import Article
from helpers.network import mock_response
from loguru import logger

class TestNewsFeed:
    @allure.epic("NewsPlatform")
    @allure.feature("Лента новостей")
    @allure.story("Количество новостей на странице")
    @allure.description("Проверяет, что на странице ленты отображается 10 новостей")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("Позитивный")
    @pytest.mark.smoke
    @pytest.mark.ui
    def test_correct_count_news(self, driver: webdriver.Firefox):
        news_feed_page = NewsFeedPage(driver)
        news_feed_page.open()

        assert news_feed_page.get_articles_count() == 10, "Ожидали 10 новостей на странице ленты"

    @allure.epic("NewsPlatform")
    @allure.feature("Лента новостей")
    @allure.story("Сортировка новостей по дате создания")
    @allure.description("Проверяет, что новости в ленте отсортированы по убыванию даты создания через API")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("Позитивный")
    @pytest.mark.smoke
    @pytest.mark.ui
    def test_correct_sorted_news(self, driver: webdriver.Firefox):
        with allure.step("Запрос списка новостей: page=1, per_page=10 — проверка сортировки по created_at"):
            logger.info("Запрос списка новостей: page=1, per_page=10 — проверка сортировки по created_at")
            request = driver.request.get("https://archiscope.ru/api/news/?page=1&per_page=10").json()
            items = []
            for item in request["items"]:
                items.append(item["created_at"])

            assert items == sorted(items, reverse=True), "Новости в ленте отсортированы не по убыванию даты создания"

    @allure.epic("NewsPlatform")
    @allure.feature("Лента новостей")
    @allure.story("Переход на страницу новости из ленты")
    @allure.description("Проверяет, что клик по названию новости в ленте открывает страницу этой новости")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Позитивный")
    @pytest.mark.smoke
    @pytest.mark.ui
    def test_correct_redirect_article(self, driver: webdriver.Firefox):
        news_feed_page = NewsFeedPage(driver)
        news_feed_page.open()

        title_article = news_feed_page.get_first_article_title()

        news_feed_page.open_article(title_article)
        article_page = ArticlePage(driver, title_article)

        assert article_page.heading.wait_until_visible(), "Заголовок статьи не отобразился после перехода по ссылке из ленты"

    @allure.epic("NewsPlatform")
    @allure.feature("Лента новостей")
    @allure.story("Валидная схема новости из API")
    @allure.description("Проверяет, что новость из API соответствует схеме модели Article")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Позитивный")
    @pytest.mark.api
    def test_correct_answer_api_article(self, driver: webdriver.Firefox):
        with allure.step("Запрос одной новости: page=1, per_page=1 — проверка схемы через Pydantic-модель Article"):
            logger.info("Запрос одной новости: page=1, per_page=1 — проверка схемы через Pydantic-модель Article")
            request = driver.request.get("https://archiscope.ru/api/news/?page=1&per_page=1").json()

            assert Article(**request["items"][0])

    @allure.epic("NewsPlatform")
    @allure.feature("Пагинация")
    @allure.story("Невалидный номер страницы")
    @allure.description("Проверяет, что запрос списка новостей с невалидным номером страницы возвращает статус 422")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("Негативный")
    @pytest.mark.parametrize("params_page", [-1, 0])
    @pytest.mark.api
    def test_incorrect_page_api_article(self, driver: webdriver.Firefox, params_page):
        with allure.step(f"Запрос списка новостей с невалидным page={params_page} — ожидаем 422"):
            logger.info(f"Запрос списка новостей с невалидным page={params_page} — ожидаем 422")
            request = driver.request.get(f"https://archiscope.ru/api/news/?page={params_page}&per_page=10")

            assert request.status == 422, f"Ожидали статус 422 для невалидного page={params_page}, получили {request.status}"

    @allure.epic("NewsPlatform")
    @allure.feature("Пагинация")
    @allure.story("Страница за пределами диапазона")
    @allure.description("Проверяет, что запрос страницы за пределами доступного диапазона возвращает статус 200 и пустой список")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("Негативный")
    @pytest.mark.parametrize("params_page", [9999])
    @pytest.mark.api
    def test_incorrect_page_api_article_empty(self, driver: webdriver.Firefox, params_page):
        with allure.step(f"Запрос списка новостей за пределами доступных страниц page={params_page} — ожидаем 200 и пустой items"):
            logger.info(f"Запрос списка новостей за пределами доступных страниц page={params_page} — ожидаем 200 и пустой items")
            request = driver.request.get(f"https://archiscope.ru/api/news/?page={params_page}&per_page=10")
            answer = request.json()
            assert answer["items"] == [] and request.status == 200, f"Ожидали пустой items и статус 200 для page={params_page} за пределами диапазона, получили status={request.status}, items={answer['items']}"

    @allure.epic("NewsPlatform")
    @allure.feature("Пагинация")
    @allure.story("Невалидный per_page")
    @allure.description("Проверяет, что запрос списка новостей с невалидным значением per_page возвращает статус 422")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("Негативный")
    @pytest.mark.parametrize("params_per_page", [-1, 0, 9999])
    @pytest.mark.api
    def test_incorrect_per_page_api_article(self, driver: webdriver.Firefox, params_per_page):
        with allure.step(f"Запрос списка новостей с невалидным per_page={params_per_page} — ожидаем 422"):
            logger.info(f"Запрос списка новостей с невалидным per_page={params_per_page} — ожидаем 422")
            request = driver.request.get(f"https://archiscope.ru/api/news/?page=1&per_page={params_per_page}")

            assert request.status == 422, f"Ожидали статус 422 для невалидного per_page={params_per_page}, получили {request.status}"

    @allure.epic("NewsPlatform")
    @allure.feature("Пагинация")
    @allure.story("Переход на вторую страницу")
    @allure.description("Проверяет, что переход на страницу 2 меняет отображаемый список новостей")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Позитивный")
    @pytest.mark.smoke
    @pytest.mark.ui
    def test_correct_change_content(self, driver: webdriver.Firefox):
        news_feed_page = NewsFeedPage(driver)
        news_feed_page.open()
        assert news_feed_page.get_articles_count() == 10, "Ожидали 10 новостей на странице ленты"

        title_article_first = news_feed_page.get_first_article_title()

        news_feed_page.go_to_page("2")

        assert news_feed_page.wait_until_first_article_changes(title_article_first), "Контент не сменился после перехода на страницу 2"

    @allure.epic("NewsPlatform")
    @allure.feature("Пагинация")
    @allure.story("Возврат на первую страницу")
    @allure.description("Проверяет, что после перехода на страницу 2 и обратно на страницу 1 отображается исходный список новостей")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Позитивный")
    @pytest.mark.smoke
    @pytest.mark.ui
    def test_correct_return_to_first_page(self, driver: webdriver.Firefox):
        news_feed_page = NewsFeedPage(driver)
        news_feed_page.open()
        assert news_feed_page.get_articles_count() == 10, "Ожидали 10 новостей на странице ленты"

        title_article_first = news_feed_page.get_first_article_title()
        news_feed_page.go_to_page("2")

        assert news_feed_page.wait_until_first_article_changes(title_article_first), "Контент не сменился после перехода на страницу 2"

        news_feed_page.go_to_page("1")
        assert news_feed_page.wait_until_first_article_is(title_article_first), "После возврата на страницу 1 контент не совпал с исходным"

    @allure.epic("NewsPlatform")
    @allure.feature("Пагинация")
    @allure.story("Сверка содержимого страниц с API")
    @allure.description("Проверяет, что содержимое ленты на страницах 1 и 2 совпадает с данными из API")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Позитивный")
    @pytest.mark.smoke
    @pytest.mark.ui
    def test_correct_change_content_api(self, driver: webdriver.Firefox):
        news_feed_page = NewsFeedPage(driver)
        news_feed_page.open()
        assert news_feed_page.get_articles_count() == 10, "Ожидали 10 новостей на странице ленты"

        title_article_first = news_feed_page.get_first_article_title()
        with allure.step("Запрос страницы 1 через API — сверка с тем, что показывает UI"):
            logger.info("Запрос страницы 1 через API — сверка с тем, что показывает UI")
            request = driver.request.get("https://archiscope.ru/api/news/?page=1&per_page=10").json()
            assert request["items"][0]["title"] == title_article_first, f"Первая новость в API (page=1) не совпала с тем, что показано в UI: API={request['items'][0]['title']!r}, UI={title_article_first!r}"

        news_feed_page.go_to_page("2")
        assert news_feed_page.wait_until_first_article_changes(title_article_first), "Контент не сменился после перехода на страницу 2"

        title_article_second = news_feed_page.get_first_article_title()
        with allure.step("Запрос страницы 2 через API — сверка с тем, что показывает UI"):
            logger.info("Запрос страницы 2 через API — сверка с тем, что показывает UI")
            request_s = driver.request.get("https://archiscope.ru/api/news/?page=2&per_page=10").json()
            assert request_s["items"][0]["title"] == title_article_second, f"Первая новость в API (page=2) не совпала с тем, что показано в UI: API={request_s['items'][0]['title']!r}, UI={title_article_second!r}"

    @allure.epic("NewsPlatform")
    @allure.feature("Поиск")
    @allure.story("Поиск по полному названию")
    @allure.description("Проверяет, что поиск по полному названию новости возвращает эту новость")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Позитивный")
    @pytest.mark.smoke
    @pytest.mark.ui
    def test_correct_search_article(self, driver: webdriver.Firefox):
        news_feed_page = NewsFeedPage(driver)
        news_feed_page.open()
        assert news_feed_page.get_articles_count() == 10

        title_before_search = news_feed_page.get_first_article_title()
        news_feed_page.search(title_before_search)
        assert news_feed_page.wait_until_first_article_is(title_before_search), f"Поиск по полному названию вернул другую новость: искали {title_before_search!r}"

    @allure.epic("NewsPlatform")
    @allure.feature("Поиск")
    @allure.story("Поиск несуществующей новости")
    @allure.description("Проверяет, что поиск по несуществующему запросу показывает сообщение об отсутствии результатов")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Негативный")
    @pytest.mark.smoke
    @pytest.mark.ui
    def test_incorrect_search_article(self, driver: webdriver.Firefox):
        news_feed_page = NewsFeedPage(driver)
        news_feed_page.open()
        assert news_feed_page.get_articles_count() == 10

        news_feed_page.search("asdkfjhqwerty12345")

        assert news_feed_page.notfound_text.wait_until_visible(), "Сообщение 'Ничего не найдено' не появилось при поиске несуществующей новости"

    @allure.epic("NewsPlatform")
    @allure.feature("Поиск")
    @allure.story("Очистка поиска")
    @allure.description("Проверяет, что очистка поля поиска возвращает полный список новостей")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("Позитивный")
    @pytest.mark.smoke
    @pytest.mark.ui
    def test_correct_clear_search_article(self, driver: webdriver.Firefox):
        news_feed_page = NewsFeedPage(driver)
        news_feed_page.open()
        assert news_feed_page.get_articles_count() == 10

        title_before_search = news_feed_page.get_first_article_title()
        news_feed_page.search(title_before_search)

        news_feed_page.clear_search()

        assert news_feed_page.get_articles_count() == 10, "После очистки поиска не вернулись все 10 новостей"

    @allure.epic("NewsPlatform")
    @allure.feature("Лента новостей")
    @allure.story("Отсутствие PII в списке новостей")
    @allure.description("Проверяет, что ответ API со списком новостей не содержит email и phone автора")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("Негативный")
    @pytest.mark.api
    def test_no_pii_leak_api_article(self, driver: webdriver.Firefox):
        with allure.step("Запрос списка новостей — проверка отсутствия email/phone автора в ответе"):
            logger.info("Запрос списка новостей — проверка отсутствия email/phone автора в ответе")
            request = driver.request.get("https://archiscope.ru/api/news/?page=1&per_page=1").json()

            for item in request["items"]:
                assert "email" not in item["author"] and "phone" not in item["author"], "Утечка полей email и phone в списке новостей"

    @allure.epic("NewsPlatform")
    @allure.feature("Лента новостей")
    @allure.story("Пустая лента новостей (mock API)")
    @allure.description("Проверяет через мок API, что при пустом списке новостей UI показывает сообщение об отсутствии результатов, а не пустую страницу")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("Негативный")
    @pytest.mark.mock
    def test_empty_news_feed(self, driver: webdriver.Firefox):
        mock_response(driver, "**/api/news/**", 200, '{"items": [], "total": 0}')

        news_feed_page = NewsFeedPage(driver)
        news_feed_page.open()

        assert news_feed_page.notfound_text.wait_until_visible(), "Сообщение 'Ничего не найдено' не появилось при пустом ответе API"

    @allure.epic("NewsPlatform")
    @allure.feature("Лента новостей")
    @allure.story("Ошибка сервера при загрузке ленты (mock API)")
    @allure.description("Проверяет через мок API, что при ответе 500 от сервера UI не падает, а показывает сообщение об отсутствии результатов")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("Негативный")
    @pytest.mark.mock
    def test_news_feed_server_error(self, driver: webdriver.Firefox):
        mock_response(driver, "**/api/news/**", 500, '{"detail": "Internal Server Error"}')

        news_feed_page = NewsFeedPage(driver)
        news_feed_page.open()

        assert news_feed_page.notfound_text.wait_until_visible(), "Сообщение 'Ничего не найдено' не появилось при ошибке 500 от сервера"
