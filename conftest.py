import pytest
import allure
from selenium import webdriver
from loguru import logger
from config import BASE_URL

logger.add("test_run.log", rotation="10MB", level="DEBUG")

@pytest.fixture(scope="session")
def browser_instance():
    driver = webdriver.Firefox()
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
