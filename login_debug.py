import os, time
from backend.selenium_worker.browser_manager import BrowserManager

BASE = os.getenv("SUNO_BASE_URL", "https://www.suno.com/").rstrip("/") + "/"
PROFILE = os.getenv("SV_CHROME_PROFILE_DIR") or (os.getcwd()+"/.selenium_profile")
os.makedirs(PROFILE, exist_ok=True)

print("BASE:", BASE)
print("PROFILE:", PROFILE)

bm = BrowserManager(
    headless=(os.getenv("SV_HEADLESS","0")=="1"),
    user_data_dir=PROFILE
)

d = bm.get_driver()
d.get(BASE+"login")
time.sleep(2)

# snapshots de depuración
d.save_screenshot("01_login_page.png")
open("01_login_page.html","w").write(d.page_source)

print("Before click, URL:", d.current_url)

# intenta hacer click en “Continuar con Google”
ok = False
try:
    # CSS típicos
    sels = [
        "[data-provider='google']",
        "button[aria-label*='google' i]",
        "button[data-testid*='google' i]",
    ]
    for sel in sels:
        try:
            el = bm.wait_clickable_css(sel, timeout=4)
            bm.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            el.click()
            ok = True
            break
        except: pass

    # XPaths por texto
    if not ok:
        xps = [
          "//button[contains(translate(., 'GOOGLE','google'),'google')]",
          "//span[contains(translate(., 'GOOGLE','google'),'google')]/ancestor::button",
          "//div[contains(translate(., 'GOOGLE','google'),'google')]/ancestor::button"
        ]
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait as W
        from selenium.webdriver.support import expected_conditions as E
        for xp in xps:
            try:
                el = W(d,5).until(E.element_to_be_clickable((By.XPATH, xp)))
                d.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                el.click()
                ok = True
                break
            except: pass

    time.sleep(2)
    d.save_screenshot("02_after_click_google.png")
    open("02_after_click_google.html","w").write(d.page_source)
    print("After click, URL:", d.current_url)
    print("Window handles:", d.window_handles)

    # si se abrió popup, cámbiate y llena correo/contraseña
    prev = d.current_window_handle
    if len(d.window_handles) > 1:
        for h in d.window_handles:
            if h != prev:
                d.switch_to.window(h)
                break

    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait as W
    from selenium.webdriver.support import expected_conditions as E
    from selenium.webdriver.common.keys import Keys

    email = os.getenv("SUNO_GOOGLE_EMAIL","").strip()
    password = os.getenv("SUNO_GOOGLE_PASSWORD","")
    if email and password:
        # email
        try:
            W(d,20).until(E.presence_of_element_located((By.CSS_SELECTOR, "#identifierId, input[type='email']")))
            try: el = d.find_element(By.CSS_SELECTOR, "#identifierId")
            except: el = d.find_element(By.CSS_SELECTOR, "input[type='email']")
            el.clear(); el.send_keys(email)
            try: d.find_element(By.ID,"identifierNext").click()
            except:
                try: d.find_element(By.XPATH, "//span[text()='Next']/ancestor::button").click()
                except: el.send_keys(Keys.ENTER)
        except Exception as e:
            print("No se pudo poner email:", e)

        # pass
        try:
            W(d,20).until(E.presence_of_element_located((By.CSS_SELECTOR, "input[type='password'][name='Passwd']")))
            pw = d.find_element(By.CSS_SELECTOR, "input[type='password'][name='Passwd']")
            pw.clear(); pw.send_keys(password)
            try: d.find_element(By.ID,"passwordNext").click()
            except:
                try: d.find_element(By.XPATH, "//span[text()='Next']/ancestor::button").click()
                except: pw.send_keys(Keys.ENTER)
        except Exception as e:
            print("No se pudo poner password:", e)

    # esperar volver a Suno/logged
    end = time.time()+90
    while time.time()<end:
        try:
            u = d.current_url
            if "suno" in u and ("create" in u or "studio" in u or "app" in u):
                break
        except: pass
        time.sleep(1)

    # vete a create y saca evidencia
    d.get(BASE+"create")
    time.sleep(3)
    d.save_screenshot("03_create_page.png")
    open("03_create_page.html","w").write(d.page_source)
    print("Final URL:", d.current_url)

finally:
    bm.quit()
    print("DONE")
