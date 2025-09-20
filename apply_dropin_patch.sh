#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(pwd)"
PY_HELPER="$REPO_DIR/backend/selenium_worker/click_utils.py"
SUNO_AUTOMATION="$REPO_DIR/backend/selenium_worker/suno_automation.py"

echo "🔧 Repo: $REPO_DIR"
[ -f "$SUNO_AUTOMATION" ] || { echo "❌ No existe: $SUNO_AUTOMATION"; exit 1; }
mkdir -p "$(dirname "$PY_HELPER")"

cat > "$PY_HELPER" <<'PY'
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
import time

SAFE_JS_CLICK = """
  try {
    window.scrollTo(0,0);
    const el = document.elementFromPoint(5,5) || document.body;
    el.dispatchEvent(new MouseEvent('mousedown', {bubbles:true}));
    el.dispatchEvent(new MouseEvent('mouseup',   {bubbles:true}));
    el.dispatchEvent(new MouseEvent('click',     {bubbles:true}));
    return true;
  } catch(e){ return false }
"""

def _fire_blur_and_change(d, el):
    d.execute_script("""
      const el = arguments[0];
      if (!el) return;
      el.dispatchEvent(new InputEvent('input',  {bubbles:true}));
      el.dispatchEvent(new Event('change',      {bubbles:true}));
      if (el.blur) el.blur();
    """, el)

def _safe_body_click(d):
    d.execute_script(SAFE_JS_CLICK)

def _nudge_validation(d, lyrics_el=None, styles_el=None):
    if styles_el: _fire_blur_and_change(d, styles_el)
    if lyrics_el: _fire_blur_and_change(d, lyrics_el)
    time.sleep(0.15)
    _safe_body_click(d)
    time.sleep(0.15)
    try:
        if styles_el and styles_el.is_displayed(): styles_el.send_keys("\t")
    except: pass
    try:
        if lyrics_el and lyrics_el.is_displayed(): lyrics_el.send_keys("\t")
    except: pass

def _button_disabled_state(btn):
    dis  = btn.get_attribute("disabled")
    aria = btn.get_attribute("aria-disabled")
    return (str(dis).lower() in ("true","disabled","1")) or (str(aria).lower() in ("true","disabled","1"))

def _find_create_button(d):
    XPS = [
        "//button[normalize-space()='Create']",
        "//span[normalize-space()='Create']/ancestor::button",
        "//*[@role='button' and normalize-space()='Create']",
    ]
    for xp in XPS:
        els = d.find_elements(By.XPATH, xp)
        if els: return els[0]
    return None

def click_create_when_enabled(d, lyrics_el=None, styles_el=None, timeout=90, screenshot_cb=None):
    act  = ActionChains(d)
    t0   = time.time()
    btn  = None
    while time.time() - t0 < timeout:
        btn = _find_create_button(d)
        if btn:
            try:
                d.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            except StaleElementReferenceException:
                btn=None

        if btn and not _button_disabled_state(btn):
            try: btn.click()
            except Exception: d.execute_script("arguments[0].click();", btn)
            if screenshot_cb: screenshot_cb("05_clicked_create")
            return True

        _nudge_validation(d, lyrics_el=lyrics_el, styles_el=styles_el)
        try:
            if btn: act.move_to_element(btn).pause(0.08).perform()
        except: pass
        time.sleep(0.35)

    if screenshot_cb: screenshot_cb("04_create_disabled_timeout")
    return False
PY
echo "✅ Escribí helper: $PY_HELPER"

# Inserta import si falta
if ! grep -q "from backend\.selenium_worker\.click_utils import click_create_when_enabled" "$SUNO_AUTOMATION"; then
  TMP="$(mktemp)"
  awk '
    BEGIN{inserted=0}
    {
      if(!inserted && $0 !~ /^(from|import) /){
        print "from backend.selenium_worker.click_utils import click_create_when_enabled"
        inserted=1
      }
      print
    }' "$SUNO_AUTOMATION" > "$TMP"
  cp "$SUNO_AUTOMATION" "$SUNO_AUTOMATION.bak" || true
  mv "$TMP" "$SUNO_AUTOMATION"
  echo "➕ Import agregado en: $SUNO_AUTOMATION"
else
  echo "ℹ️ Import ya presente."
fi

# Renombra función vieja si existiera
if grep -qE 'def\s+click_create_when_enabled\s*\(' "$SUNO_AUTOMATION"; then
  cp "$SUNO_AUTOMATION" "$SUNO_AUTOMATION.bak2" || true
  sed -i '' 's/def[[:space:]]\+click_create_when_enabled[[:space:]]*(/def click_create_when_enabled_legacy(/' "$SUNO_AUTOMATION"
  echo "🪄 Renombré función vieja → click_create_when_enabled_legacy()"
fi

# Smoke import
python - <<'PY' || true
from backend.selenium_worker.click_utils import click_create_when_enabled
print("✅ Test de import OK: click_create_when_enabled disponible.")
PY

echo "🎯 Drop-in patch aplicado."
