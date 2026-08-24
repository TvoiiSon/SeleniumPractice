from typing import Callable, Any, Tuple
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebElement # type: ignore

LocatorType = Tuple[str, str]
DriverPredicate = Callable[[Any], WebElement]

class LazyElement():
    def __init__(self, 
                 driver: Any | Callable[[], Any], 
                 locator: LocatorType | DriverPredicate
                ):

        self._driver_factory = driver
        self.locator = locator

    @property
    def driver(self) -> Any:
        if callable(self._driver_factory):
            return self._driver_factory()
        return self._driver_factory

    def _resolve_element(self, condition_factory, timeout: int = 10) -> WebElement:
        if callable(self.locator):
            return WebDriverWait(self.driver, timeout).until(self.locator)

        return WebDriverWait(self.driver, timeout).until(
            condition_factory(self.locator)
        )

    def click(self, timeout: int = 10):
        element = self._resolve_element(EC.element_to_be_clickable, timeout)
        element.click()

    def fill(self, text: str, timeout: int = 10):
        element = self._resolve_element(EC.visibility_of_element_located, timeout)
        element.clear()
        element.send_keys(text)

    def get_text(self, timeout: int = 10) -> str:
        element = self._resolve_element(EC.visibility_of_element_located, timeout)
        return element.text

    def upload(self, file_path: str, timeout: int = 10):
        element = self._resolve_element(EC.presence_of_element_located, timeout)
        element.send_keys(file_path)

    def get_by_text(self, text: str, global_search: bool, exact: bool = False) -> "LazyElement":
        if global_search:
            if exact:
                xpath = f"//*[text()='{text}']"
            else:
                xpath = f"//*[contains(text(), '{text}')]"

            return LazyElement(driver=self._driver_factory, locator=(By.XPATH, xpath))

        if exact:
            xpath = f".//*[text()='{text}']"
        else:
            xpath = f".//*[contains(text(), '{text}')]"
        
        def _find_within_parent(driver):
            parent = self._resolve_element(EC.presence_of_element_located)
            return parent.find_element(By.XPATH, xpath)

        return LazyElement(driver=self._driver_factory, locator=_find_within_parent)

    def get_by_alt_text(self, text: str, global_search: bool = False, exact: bool = False) -> "LazyElement":
            if global_search:
                if exact:
                    xpath = f"//*[@alt='{text}']"
                else:
                    xpath = f"//*[contains(@alt, '{text}')]"
    
                return LazyElement(driver=self._driver_factory, locator=(By.XPATH, xpath))
    
            if exact:
                xpath = f".//*[@alt='{text}']"
            else:
                xpath = f".//*[contains(@alt, '{text}')]"
            
            def _find_within_parent(driver):
                parent = self._resolve_element(EC.presence_of_element_located)
                return parent.find_element(By.XPATH, xpath)
    
            return LazyElement(driver=self._driver_factory, locator=_find_within_parent)
    
    def evaluate(self, js_script: str, timeout: int = 10):
        element = self._resolve_element(EC.presence_of_element_located, timeout)
        return self.driver.execute_script(js_script, element)

    def wait_until_visible(self, timeout: int = 10) -> bool:
        """Аналог expect(el).to_be_visible()"""
        try:
            self._resolve_element(EC.visibility_of_element_located, timeout)
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def wait_until_contains_text(self, text: str, timeout: int = 10) -> bool:
        """Аналог expect(el).to_have_text()"""
        try:
            element = self._resolve_element(EC.visibility_of_element_located, timeout)
            return WebDriverWait(self.driver, timeout).until(lambda d: text in element.text)
        except (TimeoutException, NoSuchElementException):
            return False
    