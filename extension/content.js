// PoC: ajusta selectores al DOM real de Suno
(async function() {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const getApi = () => new Promise(res => chrome.storage.sync.get(["api"], v => res(v.api || "")));

  async function waitFor(sel, t=20000) {
    const st = Date.now();
    while (Date.now()-st < t) {
      const el = document.querySelector(sel);
      if (el) return el;
      await sleep(250);
    } throw new Error("Elemento no encontrado: "+sel);
  }

  const API = await getApi();
  const prompt = "Emotional cyberpunk ballad, 90 BPM, minor key, airy female vox, glitch textures";

  try {
    // TODO: Reemplazar por el selector real del textarea/botón en Suno
    const txt = await waitFor('textarea, [contenteditable="true"]');
    txt.value = prompt;
    txt.dispatchEvent(new Event('input', { bubbles:true }));

    // Disparar generación (ajusta selector)
    const btn = document.querySelector('button');
    if (btn) btn.click();

    // Espera y toma fuente del audio/video
    await sleep(9000);
    const media = document.querySelector('audio, video');
    const src = media?.src || media?.getAttribute('src');

    if (src && API) {
      await fetch(API.replace(/\/$/, '') + "/api/suno/results", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ src, prompt, ts: Date.now() })
      });
    }
  } catch (e) {
    console.warn("Suno PoC content.js:", e);
  }
})();
