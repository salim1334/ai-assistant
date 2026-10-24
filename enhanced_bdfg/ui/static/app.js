const $ = (id) => document.getElementById(id);
let lang = localStorage.getItem("bdfg_lang") || "en";
let strings = {};
let setupProfile = {};
let setupComplete = false;

function show(id) {
  ["screen-ready", "screen-setup", "screen-home"].forEach((s) => {
    $(s).hidden = s !== id;
  });
}

async function loadCopy() {
  const res = await fetch("/api/copy?language=" + encodeURIComponent(lang));
  const data = await res.json();
  strings = data.strings || {};
  $("title").textContent = strings.title || "BDFG";
  $("lang-label").textContent = strings.language || "Language";
  $("ready-heading").textContent = strings.getting_ready || "Getting ready";
  $("setup-heading").textContent = strings.setup_title || "Setup";
  $("setup-hint").textContent = strings.setup_hint || "";
  $("setup-send").textContent = strings.send || "Send";
  $("chat-send").textContent = strings.send || "Send";
  $("btn-start").textContent = strings.start || "Start";
  $("btn-continue").textContent = strings.continue || "Continue";
  $("btn-install").textContent = strings.install || "Install Ollama";
  $("home-heading").textContent = strings.home_title || "Your assistant";
  $("remember-label").textContent = strings.remember || "What I remember";
  $("cloud-label").textContent = strings.cloud || "Cloud key";
  $("provider-label").textContent = strings.provider || "Provider";
  $("key-label").textContent = strings.api_key || "API key";
  $("save-key").textContent = strings.save_key || "Save key";
  $("setup-input").placeholder = strings.chat_placeholder || "";
  $("chat-input").placeholder = strings.chat_placeholder || "";
  $("language").value = lang;
}

function appendLog(el, who, text) {
  el.textContent += who + ": " + text + "\n\n";
  el.scrollTop = el.scrollHeight;
}

async function pollBootstrap() {
  await fetch("/api/bootstrap");
  const tick = async () => {
    const res = await fetch("/api/bootstrap/status");
    const st = await res.json();
    $("ready-msg").textContent = st.message || strings.finding || "";
    $("ready-bar").style.width = Math.max(5, st.percent || 0) + "%";
    const err = $("ready-error");
    if (st.error) {
      err.hidden = false;
      err.textContent = st.error;
    } else {
      err.hidden = true;
    }
    $("need-ollama").hidden = st.phase !== "need_ollama";
    $("install-cmd").textContent = st.install_command || "";
    $("btn-continue").hidden = !(st.phase === "ready" || st.phase === "need_ollama" || st.phase === "error");
        if (st.phase === "ready") {
      const state = await (await fetch("/api/state")).json();
      if (state.has_assistant) {
        await enterHome();
        return;
      }
      show("screen-setup");
      if (!$("setup-log").textContent) {
        const first = await (await fetch("/api/setup/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: "", language: lang }),
        })).json();
        appendLog($("setup-log"), "Assistant", first.reply || "");
        setupProfile = first.profile || {};
      }
      return;
    }
    if (st.phase === "need_ollama" || st.phase === "error") {
      return;
    }
    setTimeout(tick, 800);
  };
  tick();
}

async function enterHome() {
  show("screen-home");
  const [mem, moves, chips] = await Promise.all([
    fetch("/api/memory").then((r) => r.json()),
    fetch("/api/next-moves").then((r) => r.json()),
    fetch("/api/chips?language=" + encodeURIComponent(lang)).then((r) => r.json()),
  ]);
  $("memory").textContent = mem.text || "";
  $("moves").innerHTML = "";
  (moves.moves || []).forEach((m) => {
    const d = document.createElement("div");
    d.className = "card";
    d.innerHTML = "<strong>" + (m.title || "") + "</strong><div>" + (m.body || "") + "</div>";
    $("moves").appendChild(d);
  });
  $("chips").innerHTML = "";
  (chips.chips || []).forEach((label) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "chip";
    b.textContent = label;
    b.onclick = () => sendChat(label);
    $("chips").appendChild(b);
  });
}

$("language").addEventListener("change", async (e) => {
  lang = e.target.value;
  localStorage.setItem("bdfg_lang", lang);
  await loadCopy();
});

$("btn-install").addEventListener("click", async () => {
  $("ready-msg").textContent = strings.install || "Installing…";
  await fetch("/api/bootstrap/confirm-install", { method: "POST" });
  pollBootstrap();
});

$("btn-continue").addEventListener("click", async () => {
  const state = await (await fetch("/api/state")).json();
  if (state.has_assistant) enterHome();
  else show("screen-setup");
});

$("setup-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const msg = $("setup-input").value.trim();
  if (!msg) return;
  appendLog($("setup-log"), "You", msg);
  $("setup-input").value = "";
  const data = await (await fetch("/api/setup/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: msg, language: lang }),
  })).json();
  appendLog($("setup-log"), "Assistant", data.reply || "");
  setupProfile = data.profile || setupProfile;
  setupComplete = !!data.complete;
  $("btn-start").hidden = !setupComplete;
});

$("btn-start").addEventListener("click", async () => {
  await fetch("/api/setup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ profile: setupProfile, backend: "local" }),
  });
  await enterHome();
});

async function sendChat(msg) {
  appendLog($("chat-log"), "You", msg);
  const data = await (await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: msg, language: lang }),
  })).json();
  appendLog($("chat-log"), "Assistant", data.reply || data.error || "");
  const mem = await (await fetch("/api/memory")).json();
  $("memory").textContent = mem.text || "";
  const moves = await (await fetch("/api/next-moves")).json();
  $("moves").innerHTML = "";
  (moves.moves || []).forEach((m) => {
    const d = document.createElement("div");
    d.className = "card";
    d.innerHTML = "<strong>" + (m.title || "") + "</strong><div>" + (m.body || "") + "</div>";
    $("moves").appendChild(d);
  });
}

$("chat-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const msg = $("chat-input").value.trim();
  if (!msg) return;
  $("chat-input").value = "";
  await sendChat(msg);
});

$("settings-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const provider = $("provider").value;
  await fetch("/api/settings/model", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      backend: provider === "local" ? "local" : provider,
      provider,
      api_key: $("api-key").value,
    }),
  });
  $("api-key").value = "";
  alert("Saved.");
});

loadCopy().then(async () => {
  const state = await (await fetch("/api/state")).json();
  if (state.has_assistant && state.bootstrap && state.bootstrap.phase === "ready") {
    await enterHome();
    return;
  }
  show("screen-ready");
  pollBootstrap();
});
