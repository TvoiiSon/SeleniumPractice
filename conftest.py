import pytest
import allure
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from loguru import logger
from config import BASE_URL
from helpers.data_generator import generate_user
from pages.article_page import ArticlePage
from pages.create_news_page import CreateNewsPage
from pages.header_component import HeaderComponent
from pages.login_page import LoginPage
from pages.news_feed_page import NewsFeedPage
from pages.profile_page import ProfilePage
from pages.register_page import RegisterPage

logger.add("test_run.log", rotation="10MB", level="DEBUG")

@pytest.fixture(scope="session")
def browser_instance():
    opts = FirefoxOptions()
    opts.web_socket_url = True
    driver = webdriver.Firefox(options=opts)
    yield driver
    driver.quit()

@pytest.fixture(scope="function")
def driver(browser_instance):
    browser_instance.get(BASE_URL)

    browser_instance.delete_all_cookies()
    blank_pages = ("data:", "about:blank")

    if not any(page in browser_instance.current_url for page in blank_pages):
        browser_instance.execute_script("window.localStorage.clear();")
        browser_instance.execute_script("window.sessionStorage.clear();")

    browser_instance.network.clear_response_handlers()
    browser_instance.network.clear_request_handlers()

    yield browser_instance

    if len(browser_instance.window_handles) > 1:
        for handle in browser_instance.window_handles[1:]:
            browser_instance.switch_to.window(handle)
            browser_instance.close()
        browser_instance.switch_to.window(browser_instance.window_handles[0])
    
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

    if rep.when == "call" and rep.failed:
        try:
            web_driver = item.funcargs["driver"]

            allure.attach(
                web_driver.get_screenshot_as_png(),
                name="Screenshot on failure",
                attachment_type=allure.attachment_type.PNG
            )
            allure.attach(
                web_driver.page_source,
                name="HTML Source on failure",
                attachment_type=allure.attachment_type.HTML
            )
        except Exception as e:
            logger.error(f"Не удалось сделать скриншот: {e}")

@pytest.fixture
def authenticated_page(driver: webdriver.Firefox):
    login_page = LoginPage(driver)
    login_page.open()
    login_page.login("test@example.com", "password123")
    logger.info("Авторизация под общим аккаунтом email: test@example.com")
    assert login_page.header.avatar_button.wait_until_visible(), "Аватар не появился после авторизации"
    assert driver.execute_script("return localStorage.getItem('token')"), "Токен не сохранился в localStorage после авторизации"

    return driver

@pytest.fixture
def register_page(driver: webdriver.Firefox):
    register_page = RegisterPage(driver)
    register_page.open()
    generated_user = generate_user()
    register_page.register(**generated_user)
    logger.info(f"Регистрация пользователя email: {generated_user["email"]}")
    assert WebDriverWait(driver, 10).until(EC.url_to_be(BASE_URL + "/login")), "URL не изменился на /login после регистрации"

    login_page = LoginPage(driver)
    login_page.login(generated_user["email"], generated_user["password"])
    logger.info(f"Авторизация под новым пользователем email: {generated_user["email"]}")
    assert login_page.header.avatar_button.wait_until_visible(), "Аватар не появился после авторизации"
    assert driver.execute_script("return localStorage.getItem('token')"), "Токен не сохранился в localStorage после авторизации нового пользователя"

    return driver

@pytest.fixture
def go_to_article_page(authenticated_page: webdriver.Firefox):
    news_feed_page = NewsFeedPage(authenticated_page)
    news_feed_page.open()

    title_article = news_feed_page.get_first_article_title()
    
    news_feed_page.open_article(title_article)
    logger.info(f"Переход на страницу новости с названием {title_article}, после прохождения авторизации")
    article_page = ArticlePage(authenticated_page, title_article)
    assert article_page.heading.wait_until_visible(), "Заголовок новости не появился после перехода на страницу статьи"

    return article_page

@pytest.fixture
def go_to_create_news_page(authenticated_page: webdriver.Firefox):
    create_new_article_page = CreateNewsPage(authenticated_page)
    create_new_article_page.open()
    logger.info("Переход на страницу создания новости, после прохождения авторизации")
    assert WebDriverWait(authenticated_page, 10).until(EC.url_to_be(BASE_URL + "/news/create")), "URL не изменился на /news/create после перехода на страницу создания новости"

    return create_new_article_page

@pytest.fixture
def go_to_profile_page(register_page: webdriver.Firefox):
    header = HeaderComponent(register_page)
    header.open_profile()
    logger.info("Переход на страницу Профиля, после прохождения авторизации")
    assert WebDriverWait(register_page, 10).until(EC.url_to_be(BASE_URL + "/profile")), "URL не изменился на /profile после перехода на страницу профиля"

    profile_page = ProfilePage(register_page)
    
    return profile_page
