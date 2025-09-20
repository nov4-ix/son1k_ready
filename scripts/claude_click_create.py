import os, time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as W
from selenium.webdriver.support import expected_conditions as E
from backend.selenium_worker.browser_manager import BrowserManager

LYRICS  = os.getenv("SV_LYRICS",  "Neon rain over midnight streets\nEngines hum, hearts don’t sleep")
PROMPT  = os.getenv("SV_PROMPT",  "cyberpunk synthwave, 120 BPM, dark & cinematic")
PROFILE = os.getenv("SV_CHROME_PROFILE_DIR", os.path.abspath("./.selenium_profile_suno"))
HEADLESS = os.getenv("SV_HEADLESS","0") == "1"

bm = BrowserManager(headless=HEADLESS, user_data_dir=PROFILE)
d  = bm.get_driver()

def snap(tag): 
    try: d.save_screenshot(f"create_{tag}.png")
    except: pass

def ready():
    return d.execute_script("return document.readyState") == "complete"

def go_create():
    for _ in range(5):
        d.get("https://suno.com/create")
        W(d, 30).until(lambda drv: ready())
        try:
            W(d, 20).until(E.url_contains("/create"))
            return True
        except: time.sleep(1)
    return False

def ensure_custom():
    try:
        btn = d.find_element(By.XPATH, "//button[normalize-space()='Custom']")
        btn.click()
    except: pass

def find_lyrics_textarea():
    X = "//*[.//span[normalize-space()='Lyrics']]//textarea[contains(@placeholder,'Write some lyrics') or @aria-label]"
    try: return d.find_element(By.XPATH, X)
    except: return None

def find_styles_editor():
    # Card por header "Styles" y luego editor (textarea o contenteditable)
    try:
        card = d.find_element(By.XPATH, "//*[.//span[normalize-space()='Styles']]")
    except:
        return None
    for xp in [".//textarea",
               ".//*[@contenteditable='true' or @role='textbox' or @data-slate-editor='true']"]:
        els = card.find_elements(By.XPATH, xp)
        if els: return els[0]
    return None

def set_text(el, txt):
    if el is None: return False
    tag = el.tag_name.lower()
    if tag == "textarea":
        d.execute_script("""
          const el=arguments[0], v=arguments[1];
          el.focus(); el.value=v;
          el.dispatchEvent(new InputEvent('input',{bubbles:true}));
          el.dispatchEvent(new Event('change',{bubbles:true}));
          el.blur && el.blur();
        """, el, txt)
    else:
        d.execute_script("""
          const el=arguments[0], v=arguments[1];
          el.focus();
          const sel=window.getSelection(); sel.removeAllRanges();
          const r=document.createRange(); r.selectNodeContents(el);
          r.deleteContents(); el.innerHTML='';
          el.appendChild(document.createTextNode(v));
          el.dispatchEvent(new InputEvent('input',{bubbles:true}));
          el.dispatchEvent(new Event('change',{bubbles:true}));
          el.blur && el.blur();
        """, el, txt)
    time.sleep(0.2)
    return True

def get_value(el):
    if el is None: return ""
    tag = el.tag_name.lower()
    if tag == "textarea":
        return (el.get_attribute("value") or "").strip()
    return (d.execute_script("return (arguments[0].innerText||'').trim();", el) or "").strip()

def find_create_button():
    for xp in ["//button[normalize-space()='Create']",
               "//span[normalize-space()='Create']/ancestor::button",
               "//*[@role='button' and normalize-space()='Create']"]:
        els = d.find_elements(By.XPATH, xp)
        if els: return els[0]
    return None

def is_disabled(btn):
    dis  = (btn.get_attribute("disabled") or "").lower()
    aria = (btn.get_attribute("aria-disabled") or "").lower()
    return dis in ("true","disabled","1") or aria in ("true","disabled","1")

# --- run ---
assert go_create(), "No pude llegar a /create"
ensure_custom(); snap("00_loaded")

lyrics = find_lyrics_textarea()
styles = find_styles_editor()

# Si están vacíos, (re)escribe. Si Claude ya los dejó, solo los leemos.
lv = get_value(lyrics)
sv = get_value(styles)

if len(lv) < 2:
    set_text(lyrics, LYRICS)
    lv = get_value(lyrics)

if len(sv) < 3:
    set_text(styles, PROMPT)
    sv = get_value(styles)

print("Lyrics len:", len(lv), "| Styles len:", len(sv))
snap("01_filled")

# habilitar Create y click
btn = None
t0 = time.time()
clicked = False
while time.time() - t0 < 90:
    btn = find_create_button()
    if btn:
        d.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        if not is_disabled(btn):
            try:
                btn.click()
            except:
                d.execute_script("arguments[0].click();", btn)
            clicked = True
            snap("02_clicked_create")
            break
    # pequeño nudge de validación sin tocar chips
    d.execute_script("window.scrollTo(0,0); (document.elementFromPoint(2,2)||document.body).click();")
    time.sleep(0.4)

print("CREATE_CLICKED:", clicked)
time.sleep(6)
bm.quit()
