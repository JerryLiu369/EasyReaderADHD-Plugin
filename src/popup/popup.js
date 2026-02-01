// EasyReaderADHD Popup Script
// 严格遵守 CSP：无内联脚本，所有逻辑在此文件中

// 1. 全局错误捕获 (必须最先执行)
window.addEventListener("unhandledrejection", (event) => {
  try {
    const reason = event.reason;
    const msg = reason && reason.message ? reason.message : String(reason);
    // 忽略扩展通信中常见的"接收端不存在"错误
    if (
      msg &&
      (msg.includes("Receiving end does not exist") ||
        msg.includes("Could not establish connection"))
    ) {
      event.preventDefault();
    }
  } catch (e) {
    // ignore
  }
});

// 2. 常量定义
const PRESETS = {
  default: {
    noun: "#4299e1",
    verb: "#f56565",
    adj: "#48bb78",
    other: "#805ad5",
  },
  soft: { noun: "#90cdf4", verb: "#feb2b2", adj: "#9ae6b4", other: "#d6bcfa" },
  forest: {
    noun: "#2c7a7b",
    verb: "#2f855a",
    adj: "#38a169",
    other: "#285e61",
  },
  pink: { noun: "#ed64a6", verb: "#f687b3", adj: "#fbb6ce", other: "#d53f8c" },
  "high-contrast": {
    noun: "#0000ff",
    verb: "#ff0000",
    adj: "#008000",
    other: "#800080",
  },
};

const DEFAULT_APPEARANCE = {
  theme: "default",
  colors: { ...PRESETS.default },
  highlightDensity: 50,
  scale: 100,
  weight: 400,
  spacing: 0,
  underline: false,
};

const DEFAULT_DICTIONARIES = {
  en: { enabled: true, name: "🇬🇧 英语" },
  zh: { enabled: true, name: "🇨🇳 中文" },
  ja: { enabled: false, name: "🇯🇵 日语" },
  fr: { enabled: false, name: "🇫🇷 法语" },
  es: { enabled: false, name: "🇪🇸 西班牙语" },
  ru: { enabled: false, name: "🇷🇺 俄语" },
  zh_chengyu: { enabled: false, name: "📚 成语" },
  zh_poem: { enabled: false, name: "🎭 诗词" },
  zh_it: { enabled: false, name: "💻 IT技术" },
  zh_caijing: { enabled: false, name: "💰 财经" },
  zh_law: { enabled: false, name: "⚖️ 法律" },
  zh_medical: { enabled: false, name: "🏥 医学" },
  zh_car: { enabled: false, name: "🚗 汽车" },
  zh_food: { enabled: false, name: "🍜 食物" },
  zh_animal: { enabled: false, name: "🐾 动物" },
  zh_diming: { enabled: false, name: "🗺️ 地名" },
  zh_lishimingren: { enabled: false, name: "👤 历史人物" },
};

const SPECIAL_KEYS = [
  "zh_chengyu",
  "zh_poem",
  "zh_it",
  "zh_caijing",
  "zh_law",
  "zh_medical",
  "zh_car",
  "zh_food",
  "zh_animal",
  "zh_diming",
  "zh_lishimingren",
];

// 3. 状态管理
let currentState = {
  enabled: true,
  dictionaries: { ...DEFAULT_DICTIONARIES },
  appearance: { ...DEFAULT_APPEARANCE },
};

// 4. 初始化
document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  loadSettings();
});

// 5. 核心功能函数
function initTabs() {
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach((btn) => {
    btn.addEventListener("click", () => {
      // 移除所有激活状态
      document
        .querySelectorAll(".tab-btn")
        .forEach((b) => b.classList.remove("active"));
      document
        .querySelectorAll(".tab-pane")
        .forEach((p) => p.classList.remove("active"));

      // 激活当前标签
      btn.classList.add("active");
      const targetId = btn.dataset.tab;
      const targetPane = document.getElementById(targetId);
      if (targetPane) {
        targetPane.classList.add("active");
      }
    });
  });
}

function loadSettings() {
  chrome.storage.sync.get(["adhdSettings"], (result) => {
    if (result.adhdSettings) {
      const remote = result.adhdSettings;
      // 深度合并设置，防止字段丢失
      currentState = {
        ...currentState,
        ...remote,
        appearance: {
          ...DEFAULT_APPEARANCE,
          ...(remote.appearance || {}),
        },
        dictionaries: {
          ...DEFAULT_DICTIONARIES,
          ...(remote.dictionaries || {}),
        },
      };
    }
    renderUI();
    setupEventListeners();
  });
}

function saveSettings() {
  // 只写入 storage，不发送 sendMessage，完全依赖 storage.onChanged 事件
  chrome.storage.sync.set({ adhdSettings: currentState }, () => {
    if (chrome.runtime.lastError) {
      console.error("保存设置失败:", chrome.runtime.lastError);
    }
  });
}

function renderUI() {
  // 渲染总开关
  const enableToggle = document.getElementById("enableToggle");
  if (enableToggle) enableToggle.checked = !!currentState.enabled;

  // 渲染词典
  renderDictionaries();

  // 渲染外观
  renderAppearance();
}

function renderDictionaries() {
  const basic = document.getElementById("basic-dicts");
  const special = document.getElementById("special-dicts");

  if (basic) basic.innerHTML = "";
  if (special) special.innerHTML = "";

  if (!basic && !special) return;

  Object.entries(currentState.dictionaries).forEach(([key, cfg]) => {
    const isSpecial = SPECIAL_KEYS.includes(key);
    const container = isSpecial ? special : basic;
    if (!container) return;

    const div = document.createElement("div");
    div.className = "dict-item";
    div.innerHTML = `
      <label class="dict-label">
        <input type="checkbox" class="dict-checkbox" data-dict="${key}" ${
          cfg.enabled ? "checked" : ""
        }>
        <span class="dict-name">${cfg.name}</span>
      </label>
    `;
    container.appendChild(div);
  });
}

function renderAppearance() {
  const app = currentState.appearance || DEFAULT_APPEARANCE;
  const colors = app.colors || PRESETS.default;

  // 设置值
  setValue("themeSelect", app.theme || "default");
  setValue("colorNoun", colors.noun);
  setValue("colorVerb", colors.verb);
  setValue("colorAdj", colors.adj);
  setValue("colorOther", colors.other);

  setValue("inputScale", app.scale || 100);
  setText("valScale", ((app.scale || 100) / 100).toFixed(1) + "x");

  setValue("inputWeight", app.weight || 400);
  setText("valWeight", (app.weight || 400) === 400 ? "正常" : app.weight);

  setValue("inputDensity", app.highlightDensity ?? 50);
  setText("valDensity", `${app.highlightDensity ?? 50}%`);

  setValue("inputSpacing", app.spacing || 0);
  setText("valSpacing", (app.spacing || 0) + "px");

  setChecked("inputUnderline", !!app.underline);
}

// 6. 事件监听
function setupEventListeners() {
  // 总开关
  bindChange("enableToggle", (e) => {
    currentState.enabled = !!e.target.checked;
    saveSettings();
  });

  // 词典开关 (事件委托)
  document.body.addEventListener("change", (e) => {
    if (e.target.classList.contains("dict-checkbox")) {
      const key = e.target.dataset.dict;
      if (key && currentState.dictionaries[key]) {
        currentState.dictionaries[key].enabled = !!e.target.checked;
        saveSettings();
      }
    }
  });

  // 主题选择
  bindChange("themeSelect", (e) => {
    const val = e.target.value;
    currentState.appearance.theme = val;
    if (val !== "custom" && PRESETS[val]) {
      currentState.appearance.colors = { ...PRESETS[val] };
      renderAppearance(); // 重新渲染颜色选择器
    }
    saveSettings();
  });

  // 颜色选择器
  ["colorNoun", "colorVerb", "colorAdj", "colorOther"].forEach((id) => {
    bindInput(id, () => {
      currentState.appearance.theme = "custom";
      setValue("themeSelect", "custom");
      updateColorsFromUI();
      saveSettings();
    });
  });

  // 滑块 (实时预览 + 保存)
  bindInput("inputScale", (e) => {
    const val = parseInt(e.target.value, 10);
    currentState.appearance.scale = val;
    setText("valScale", (val / 100).toFixed(1) + "x");
    saveSettings();
  });

  bindInput("inputWeight", (e) => {
    const val = parseInt(e.target.value, 10);
    currentState.appearance.weight = val;
    setText("valWeight", val === 400 ? "正常" : val);
    saveSettings();
  });

  bindInput("inputSpacing", (e) => {
    const val = parseInt(e.target.value, 10);
    currentState.appearance.spacing = val;
    setText("valSpacing", val + "px");
    saveSettings();
  });

  bindInput("inputDensity", (e) => {
    const val = Math.max(0, Math.min(100, parseInt(e.target.value, 10)));
    currentState.appearance.highlightDensity = val;
    setText("valDensity", `${val}%`);
    saveSettings();
  });

  bindChange("inputUnderline", (e) => {
    currentState.appearance.underline = !!e.target.checked;
    saveSettings();
  });
}

// 7. 辅助函数
function setValue(id, value) {
  const el = document.getElementById(id);
  if (el) el.value = value;
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function setChecked(id, checked) {
  const el = document.getElementById(id);
  if (el) el.checked = checked;
}

function bindChange(id, handler) {
  const el = document.getElementById(id);
  if (el) el.addEventListener("change", handler);
}

function bindInput(id, handler) {
  const el = document.getElementById(id);
  if (el) el.addEventListener("input", handler);
}

function updateColorsFromUI() {
  currentState.appearance.colors = {
    noun: document.getElementById("colorNoun").value,
    verb: document.getElementById("colorVerb").value,
    adj: document.getElementById("colorAdj").value,
    other: document.getElementById("colorOther").value,
  };
}
