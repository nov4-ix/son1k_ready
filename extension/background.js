let API = "";
chrome.storage.sync.get(["api"], v => API = (v.api || ""));

chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === "TRIGGER_TEST") openSuno();
});

async function openSuno() {
  const url = "https://www.suno.ai/app";
  await chrome.tabs.create({ url, active: true });
}
