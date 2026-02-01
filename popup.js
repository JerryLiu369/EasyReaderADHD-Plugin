// EasyReaderADHD Popup Script

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

const DEFAULT_STYLE = {
  theme: "default",
  colors: { ...PRESETS.default },
  scale: 100,
  weight: 400,
  spacing: 0,
  underline: false,
};

const DEFAULT_DICTS = {
  en: {
    enabled: true,
    pos: { noun: true, verb: true, adj: true, other: false },
    name: "🇬🇧 英语",
  },
  zh: {
    enabled: true,
    pos: { noun: true, verb: true, adj: true, other: false },
    name: "🇨🇳 中文",
  },
  ja: {
    enabled: false,
    pos: { noun: true, verb: true, adj: true, other: false },
    name: "🇯🇵 日语",
  },
  fr: {
    enabled: false,
    pos: { noun: true, verb: true, adj: true, other: false },
    name: "🇫🇷 法语",
  },
  es: {
    enabled: false,
    pos: { noun: true, verb: true, adj: true, other: false },
    name: "🇪🇸 西班牙语",
  },
  ru: {
    enabled: false,
    pos: { noun: true, verb: true, adj: true, other: false },
    name: "🇷🇺 俄语",
  },
};

const SPECIAL_DICTS = {
  zh_chengyu: {
    enabled: false,
    pos: { noun: true, verb: true, adj: true, other: false },
    name: "📚 成语",
  },
  zh_poem: {
    enabled: false,
    pos: { noun: true, verb: true, adj: true, other: false },
    name: "🎭 诗词",
  },
  zh_it: {
    enabled: false,
    pos: { noun: true, verb: true, adj: true, other: false },
    name: "💻 IT技术",
  },
  zh_caijing: {
    enabled: false,
    pos: { noun: true, verb: true, adj: true, other: false },
    name: "💰 财经",
  },
  zh_law: {
    enabled: false,
    pos: { noun: true, verb: true, adj: true, other: false },
    name: "⚖️ 法律",
  },
  zh_medical: {
    enabled: false,
    pos: { noun: true, verb: true, adj: true, other: false },
    name: "🏥 医学",
  },
  zh_car: {
    enabled: false,
    pos: { noun: true, verb: true, adj: true, other: false },
    name: "🚗 汽车",
  },
  zh_food: {
    enabled: false,
    pos: { noun: true, verb: true, adj: true, other: false },
    name: "🍜 食物",
  },
  zh_animal: {
    enabled: false,
    pos: { noun: true, verb: true, adj: true, other: false },
    name: "🐾 动物",
  },
  zh_diming: {
    enabled: false,
    pos: { noun: true, verb: true, adj: true, other: false },
    name: "🗺️ 地名",
  },
  zh_lishimingren: {
    enabled: false,
    pos: { noun: true, verb: true, adj: true, other: false },
    name: "👤 历史人物",
  },
};

let currentState = {
  enabled: true,
  dictionaries: {},
  appearance: { ...DEFAULT_STYLE },
  // 新增：处理模式设置
  },
};

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  loadSettings();
});

function initTabs() {
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document
        .querySelectorAll(".tab-btn")
        .forEach((b) => b.classList.remove("active"));
      document
        .querySelectorAll(".tab-pane")
        .forEach((p) => p.classList.remove("active"));

      btn.classList.add("active");
      document.getElementById(btn.dataset.tab).classList.add("active");
    });
  });
}

function loadSettings() {
  chrome.storage.local.get(["adhdSettings"], async (result) => {
    if (result.adhdSettings) {
      // Merge with defaults to ensure new fields exist
      currentState = {
        ...currentState,
        ...result.adhdSettings,
        appearance: {
          ...DEFAULT_STYLE,
          ...(result.adhdSettings.appearance || {}),
        },
      };
      // Ensure all dicts exist
      for (const [key, val] of Object.entries({
        ...DEFAULT_DICTS,
        ...SPECIAL_DICTS,
      })) {
        if (!currentState.dictionaries[key]) {
          currentState.dictionaries[key] = val;
        }
      }
    } else {
      currentState.dictionaries = { ...DEFAULT_DICTS, ...SPECIAL_DICTS };
    }

      };
    }

    if (!currentState.processingMode) {
      currentState.processingMode = "dictionary";
    }

    renderDicts();
    renderAppearance();
    setupListeners();
  });
}

function renderDicts() {
  const basicContainer = document.getElementById("basic-dicts");
  const specialContainer = document.getElementById("special-dicts");
  basicContainer.innerHTML = "";
  specialContainer.innerHTML = "";

  // Render main toggle
  document.getElementById("enableToggle").checked = currentState.enabled;

  // Helper to create item
  const createItem = (key, config) => {
    const div = document.createElement("div");
    div.className = "dict-item";
    div.innerHTML = `
      <span class="dict-name">${config.name}</span>
      <div class="pos-toggles">
        <button class="pos-btn ${
          config.pos.noun ? "active" : ""
        }" data-pos="noun" data-dict="${key}">名</button>
        <button class="pos-btn ${
          config.pos.verb ? "active" : ""
        }" data-pos="verb" data-dict="${key}">动</button>
        <button class="pos-btn ${
          config.pos.adj ? "active" : ""
        }" data-pos="adj" data-dict="${key}">形</button>
        <button class="pos-btn ${
          config.pos.other ? "active" : ""
        }" data-pos="other" data-dict="${key}">他</button>
      </div>
      <label class="toggle-switch">
        <input type="checkbox" class="dict-enable" data-dict="${key}" ${
      config.enabled ? "checked" : ""
    }>
        <span class="toggle-slider"></span>
      </label>
    `;
    return div;
  };

  Object.keys(DEFAULT_DICTS).forEach((key) => {
    basicContainer.appendChild(createItem(key, currentState.dictionaries[key]));
  });

  Object.keys(SPECIAL_DICTS).forEach((key) => {
    specialContainer.appendChild(
      createItem(key, currentState.dictionaries[key])
    );
  });
}

function renderAppearance() {
  const app = currentState.appearance;

  // Theme Select
  document.getElementById("themeSelect").value = app.theme;

  // Colors
  document.getElementById("colorNoun").value = app.colors.noun;
  document.getElementById("colorVerb").value = app.colors.verb;
  document.getElementById("colorAdj").value = app.colors.adj;
  document.getElementById("colorOther").value = app.colors.other;

  // Controls
  document.getElementById("inputScale").value = app.scale;
  document.getElementById("valScale").textContent =
    (app.scale / 100).toFixed(1) + "x";

  document.getElementById("inputWeight").value = app.weight;
  document.getElementById("valWeight").textContent =
    app.weight === 400 ? "正常" : app.weight;

  document.getElementById("inputSpacing").value = app.spacing;
  document.getElementById("valSpacing").textContent = app.spacing + "px";

  document.getElementById("inputUnderline").checked = app.underline;
}

function setupListeners() {
  // Main Toggle
  document.getElementById("enableToggle").addEventListener("change", (e) => {
    currentState.enabled = e.target.checked;
    save();
  });

  // Dict Enable
  document.body.addEventListener("change", (e) => {
    if (e.target.classList.contains("dict-enable")) {
      const dict = e.target.dataset.dict;
      currentState.dictionaries[dict].enabled = e.target.checked;
      save();
    }
  });

  // Pos Buttons
  document.body.addEventListener("click", (e) => {
    if (e.target.classList.contains("pos-btn")) {
      const dict = e.target.dataset.dict;
      const pos = e.target.dataset.pos;
      currentState.dictionaries[dict].pos[pos] =
        !currentState.dictionaries[dict].pos[pos];
      e.target.classList.toggle("active");
      save();
    }
  });

  // Appearance Inputs
  const updateApp = () => {
    const themeVal = document.getElementById("themeSelect").value;

    // If theme changed
    if (themeVal !== currentState.appearance.theme && themeVal !== "custom") {
      currentState.appearance.colors = { ...PRESETS[themeVal] };
      // Update pickers
      document.getElementById("colorNoun").value =
        currentState.appearance.colors.noun;
      document.getElementById("colorVerb").value =
        currentState.appearance.colors.verb;
      document.getElementById("colorAdj").value =
        currentState.appearance.colors.adj;
      document.getElementById("colorOther").value =
        currentState.appearance.colors.other;
    } else {
      // Custom colors
      currentState.appearance.colors = {
        noun: document.getElementById("colorNoun").value,
        verb: document.getElementById("colorVerb").value,
        adj: document.getElementById("colorAdj").value,
        other: document.getElementById("colorOther").value,
      };
    }

    currentState.appearance.theme = themeVal;
    currentState.appearance.scale = parseInt(
      document.getElementById("inputScale").value
    );
    currentState.appearance.weight = parseInt(
      document.getElementById("inputWeight").value
    );
    currentState.appearance.spacing = parseInt(
      document.getElementById("inputSpacing").value
    );
    currentState.appearance.underline =
      document.getElementById("inputUnderline").checked;

    // Update labels
    document.getElementById("valScale").textContent =
      (currentState.appearance.scale / 100).toFixed(1) + "x";
    document.getElementById("valWeight").textContent =
      currentState.appearance.weight;
    document.getElementById("valSpacing").textContent =
      currentState.appearance.spacing + "px";

    save();
  };

  // Theme Select
  document.getElementById("themeSelect").addEventListener("change", updateApp);

  // Color Pickers (Switch to custom on input)
  ["colorNoun", "colorVerb", "colorAdj", "colorOther"].forEach((id) => {
    document.getElementById(id).addEventListener("input", () => {
      document.getElementById("themeSelect").value = "custom";
      updateApp();
    });
  });

  // Range Inputs
  ["inputScale", "inputWeight", "inputSpacing", "inputUnderline"].forEach(
    (id) => {
      document.getElementById(id).addEventListener("input", updateApp);
    }
  );
}

function save() {
  chrome.storage.local.set({ adhdSettings: currentState }, () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        chrome.tabs.sendMessage(tabs[0].id, {
          action: "settingsUpdated",
          settings: currentState,
        });
      }
    });
  });
}

  // 处理模式选择
  const modeRadios = document.querySelectorAll('input[name="processingMode"]');
  modeRadios.forEach((radio) => {
    radio.checked = radio.value === currentState.processingMode;
  });



}

const originalSetupListeners = setupListeners;
setupListeners = function () {
  originalSetupListeners();
};
