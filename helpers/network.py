from typing import Any, Callable

from selenium.webdriver.support.ui import WebDriverWait


def wait_for_response(driver: Any, url_pattern: str, action: Callable[[], None], timeout: int = 10) -> Any:
    """Аналог Playwright's `page.expect_response(url_pattern)` — выполняет action()
    и возвращает первый Response, чей url совпал с url_pattern."""
    captured = []
    handler_id = driver.network.add_response_handler([url_pattern], lambda response: captured.append(response))
    try:
        action()
        WebDriverWait(driver, timeout).until(lambda d: len(captured) > 0)
        return captured[0]
    finally:
        driver.network.remove_response_handler(handler_id)


def mock_response(driver: Any, url_pattern: str, status: int, body: str, content_type: str = "application/json") -> str:
    """Аналог Playwright's `page.route(url_pattern, handler)` + `route.fulfill(...)` —
    подменяет ответ на запросы, совпавшие с url_pattern, статусом/телом из аргументов.
    Возвращает handler_id для driver.network.remove_request_handler(handler_id)."""
    def handler(request):
        request.provide_response(status=status, headers={"content-type": content_type}, body=body)

    return driver.network.add_request_handler([url_pattern], handler)
