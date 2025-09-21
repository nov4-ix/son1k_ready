import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as W
from selenium.webdriver.support import expected_conditions as E
from selenium.webdriver import Remote

try:
    from webdriver_manager.chrome import ChromeDriverManager
except Exception:
    ChromeDriverManager = None


def _apply_common_flags(opts: Options, headless: bool):
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,800")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    
    # Additional robustness flags
    opts.add_argument("--no-first-run")
    opts.add_argument("--no-default-browser-check")
    opts.add_argument("--disable-popup-blocking")
    opts.add_argument("--disable-features=Translate,ChromeWhatsNewUI")
    opts.add_argument("--restore-last-session=false")
    opts.add_argument("--homepage=about:blank")
    opts.add_argument("--new-window")


def make_driver(
    headless: bool = True,
    user_data_dir: Optional[str] = None,
    capabilities: Optional[Dict[str, Any]] = None,
    binary_location: Optional[str] = None,
    remote_url: Optional[str] = None,
):
    """Selenium 4 only. NO desired_capabilities in constructor."""
    opts = Options()
    _apply_common_flags(opts, headless)

    if user_data_dir:
        opts.add_argument(f"--user-data-dir={user_data_dir}")
    if binary_location:
        opts.binary_location = binary_location

    if capabilities:
        for k, v in capabilities.items():
            try:
                opts.set_capability(k, v)
            except Exception:
                if k.lower() == "loggingprefs":
                    opts.set_capability("goog:loggingPrefs", v)

    # Check for remote Selenium endpoint
    remote_url = remote_url or os.environ.get("SV_SELENIUM_URL", "").strip()
    if remote_url:
        logger.info(f"🌐 Using remote Selenium: {remote_url}")
        return Remote(command_executor=remote_url, options=opts)

    # Local driver
    if ChromeDriverManager:
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=opts)

    return webdriver.Chrome(options=opts)


def get_optimized_driver():
    logger.info("🚀 Setting up OPTIMIZED Chrome WebDriver for commercial speed...")
    profile = os.environ.get("SV_CHROME_PROFILE_DIR")
    binary = os.environ.get("SV_CHROME_BINARY")
    caps = {}
    return make_driver(
        headless=(os.environ.get("SV_HEADLESS","1")=="1"),
        user_data_dir=profile,
        capabilities=caps,
        binary_location=binary
    )


class BrowserManager:
    def _query_shadow_all(self, selector: str):
        d = self.get_driver()
        return d.execute_script(
            '''
            const sel = arguments[0];
            function allShadow(root){
              const out=[]; const walker=[root];
              while(walker.length){
                const n=walker.pop();
                if(n.shadowRoot){ walker.push(n.shadowRoot); }
                out.push(...(n.querySelectorAll? n.querySelectorAll(sel): []));
                if(n.shadowRoot) out.push(...n.shadowRoot.querySelectorAll(sel));
              }
              return out;
            }
            return allShadow(document);
            ''', selector)
    def _click_google_in_context(self, ctx, timeout=8):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait as W
        from selenium.webdriver.support import expected_conditions as E
        d=self.get_driver()
        css = [
          "[data-provider='google']",
          "button[aria-label*='google' i]",
          "button[data-testid*='google' i]",
          "a[href*='google']",
        ]
        xps = [
          "//button[contains(translate(.,'GOOGLE','google'),'google')]",
          "//span[contains(translate(.,'GOOGLE','google'),'google')]/ancestor::button",
          "//div[contains(translate(.,'GOOGLE','google'),'google')]/ancestor::button",
        ]
        # CSS
        for sel in css:
            try:
                el = W(d, timeout).until(lambda dd: E.element_to_be_clickable((By.CSS_SELECTOR, sel))(ctx))
                dd=d
                dd.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                el.click(); return True
            except Exception: pass
        # XPATH
        for xp in xps:
            try:
                el = W(d, timeout).until(lambda dd: E.element_to_be_clickable((By.XPATH, xp))(ctx))
                d.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                el.click(); return True
            except Exception: pass
        return False
    def _click_google_anywhere(self, timeout=12):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait as W
        from selenium.webdriver.support import expected_conditions as E
        d=self.get_driver()
        # 1) Documento principal
        try:
            if self._click_google_in_context(d, timeout=timeout//2):
                return True
        except Exception:
            pass
        # 2) Iframes (API Selenium 4)
        try:
            iframes = d.find_elements(By.TAG_NAME, 'iframe')
            for frame in iframes:
                try:
                    d.switch_to.frame(frame)
                    if self._click_google_in_context(d, timeout=timeout//2):
                        d.switch_to.default_content()
                        return True
                except Exception:
                    pass
                finally:
                    d.switch_to.default_content()
        except Exception:
            pass
        # 3) Shadow DOM: buscar botones/enlaces cuyo texto contenga 'google'
        try:
            nodes = self._query_shadow_all("button, a")
            for idx in range(min(len(nodes), 50)):
                try:
                    el = nodes[idx]
                    txt = d.execute_script(
                        "return (arguments[0].innerText || arguments[0].textContent || '').toLowerCase();",
                        el
                    )
                    if txt and 'google' in txt:
                        d.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                        try:
                            el.click()
                        except Exception:
                            d.execute_script(
                                "const r=arguments[0].getBoundingClientRect();"
                                "const evt=new MouseEvent('click',{bubbles:true,cancelable:true,"
                                "clientX:r.x+r.width/2,clientY:r.y+r.height/2});"
                                "arguments[0].dispatchEvent(evt);", el
                            )
                        return True
                except Exception:
                    pass
        except Exception:
            pass
        return False

    """
    Wrapper compatible con tests legacy.
    Métodos: setup_driver(), get_driver(), close(), quit(),
    open()/goto(), waits, ensure_logged_in(), navigate_to_create(), take_screenshot()
    """
    def __init__(self, headless: bool = True, user_data_dir: str | None = None,
                 binary_location: str | None = None, capabilities: dict | None = None,
                 default_timeout: int = 20):
        self._headless = headless
        self._user_data_dir = user_data_dir
        self._binary_location = binary_location
        self._capabilities = capabilities or {}
        self._timeout = default_timeout
        self.driver = None

    # ===== API esperada por los tests =====
    def setup_driver(self):
        return self.get_driver()

    def get_driver(self):
        if self.driver is None:
            logger.info("🌐 Inicializando ChromeDriver…")
            self.driver = make_driver(
                headless=self._headless,
                user_data_dir=self._user_data_dir,
                capabilities=self._capabilities,
                binary_location=self._binary_location,
                remote_url=os.environ.get("SV_SELENIUM_URL", "").strip() or None,
            )
        return self.driver

    def close(self):
        try:
            if self.driver:
                try:
                    self.driver.close()
                except Exception:
                    pass
                self.driver.quit()
        finally:
            self.driver = None

    def quit(self):
        try:
            if self.driver:
                self.driver.quit()
        finally:
            self.driver = None

    # ===== Helpers básicos =====
    def open(self, url: str):
        return self.goto(url)

    def goto(self, url: str):
        d = self.get_driver()
        d.get(url)
        return d

    def wait_for_css(self, selector: str, timeout: Optional[int] = None):
        d = self.get_driver()
        t = timeout or self._timeout
        return W(d, t).until(E.presence_of_element_located((By.CSS_SELECTOR, selector)))

    def wait_clickable_css(self, selector: str, timeout: Optional[int] = None):
        d = self.get_driver()
        t = timeout or self._timeout
        return W(d, t).until(E.element_to_be_clickable((By.CSS_SELECTOR, selector)))

    def wait_for_xpath(self, xpath: str, timeout: Optional[int] = None):
        d = self.get_driver()
        t = timeout or self._timeout
        return W(d, t).until(E.presence_of_element_located((By.XPATH, xpath)))

    def click_css(self, selector: str, timeout: Optional[int] = None):
        el = self.wait_clickable_css(selector, timeout)
        el.click()
        return el

    def type_css(self, selector: str, text: str, clear: bool = True, timeout: Optional[int] = None):
        el = self.wait_for_css(selector, timeout)
        if clear:
            el.clear()
        el.send_keys(text)
        return el

    # ===== Login helpers =====
    def _cookie_session_present(self) -> bool:
        try:
            d = self.get_driver()
            names = {c.get("name","") for c in d.get_cookies()}
            probes = {"session","suno_session","__Secure-next-auth.session-token","next-auth.session-token"}
            return any(n in names for n in probes)
        except Exception:
            return False

    def _ui_logged_in(self) -> bool:
        try:
            html = self.get_driver().page_source.lower()
            return ("logout" in html or "create" in html) or self._cookie_session_present()
        except Exception:
            return False

    def ensure_logged_in(self, base_url: str = "https://www.suno.com/") -> bool:
        d = self.get_driver()
        if not (d.current_url.startswith("https://www.suno.com") or d.current_url.startswith("https://suno.ai")):
            d.get(base_url)
        try:
            W(d, 20).until(E.presence_of_element_located((By.TAG_NAME, "body")))
        except Exception:
            pass
        if self._ui_logged_in():
            return True

        email = os.environ.get("SUNO_EMAIL", "").strip()
        password = os.environ.get("SUNO_PASSWORD", "")

        if email and password:
            try:
                for url in [f"{base_url.rstrip('/')}/login", "https://suno.ai/login"]:
                    d.get(url)
                    try:
                        W(d, 10).until(E.presence_of_element_located((By.TAG_NAME, "body")))
                    except Exception:
                        pass
                    try:
                        self.type_css("input[type='email'], input[name='email']", email, clear=True, timeout=5)
                    except Exception:
                        pass
                    try:
                        self.type_css("input[type='password'], input[name='password']", password, clear=True, timeout=5)
                    except Exception:
                        pass
                    try:
                        self.click_css("button[type='submit'], button", timeout=5)
                    except Exception:
                        pass
                    import time
                    for _ in range(30):
                        if self._ui_logged_in():
                            return True
                        time.sleep(0.5)
            except Exception:
                pass

        if not self._headless:
            try:
                d.get(base_url)
                import time
                deadline = time.time() + 120
                while time.time() < deadline:
                    if self._ui_logged_in():
                        return True
                    time.sleep(1)
            except Exception:
                pass
        return False

    # ===== Navegación específica de Suno =====
    def get_base_url(self) -> str:
        return os.environ.get("SUNO_BASE_URL", "https://www.suno.com/").rstrip("/") + "/"

    def _looks_like_create_page(self) -> bool:
        try:
            html = self.get_driver().page_source.lower()
            for n in ["create", "generate", "make song", "make music"]:
                if n in html:
                    return True
            return False
        except Exception:
            return False

    def navigate_to_create(self, timeout: int = 20) -> bool:
        d = self.get_driver()
        base = self.get_base_url()
        candidates = [
            base + "create",
            base + "studio",
            base + "app/create",
            base,
        ]
        for url in candidates:
            try:
                d.get(url)
                try:
                    W(d, timeout).until(E.presence_of_element_located((By.TAG_NAME, "body")))
                except Exception:
                    pass
                if self._looks_like_create_page():
                    return True
                # intenta click CTA genérico
                for sel in [
                    "[data-testid='create-track']",
                    "button[data-testid*='create']",
                    "a[href*='create']",
                    "button"
                ]:
                    try:
                        W(d, 3).until(E.element_to_be_clickable((By.CSS_SELECTOR, sel))).click()
                        try:
                            W(d, 5).until(E.presence_of_element_located((By.TAG_NAME, "body")))
                        except Exception:
                            pass
                        if self._looks_like_create_page():
                            return True
                    except Exception:
                        continue
            except Exception:
                continue
        return self._looks_like_create_page()

    def take_screenshot(self, path: str) -> str:
        try:
            d = self.get_driver()
            folder = os.path.dirname(path) or "."
            os.makedirs(folder, exist_ok=True)
            d.save_screenshot(path)
            return path
        except Exception:
            return path

    # context manager
    def __enter__(self):
        self.get_driver()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.quit()


__all__ = ["make_driver", "get_optimized_driver", "BrowserManager"]
