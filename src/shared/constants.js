/**
 * 常量定义
 */

export const DICT_FILES = {
  en: "src/dictionaries/EN_word.json",
  zh: "src/dictionaries/ZH_word.json",
  ja: "src/dictionaries/JA_word.json",
  fr: "src/dictionaries/FR_word.json",
  es: "src/dictionaries/ES_word.json",
  ru: "src/dictionaries/RU_word.json",
  zh_chengyu: "src/dictionaries/ZH/ZH_word_chengyu.json",
  zh_poem: "src/dictionaries/ZH/ZH_word_poem.json",
  zh_it: "src/dictionaries/ZH/ZH_word_it.json",
  zh_caijing: "src/dictionaries/ZH/ZH_word_caijing.json",
  zh_law: "src/dictionaries/ZH/ZH_word_law.json",
  zh_medical: "src/dictionaries/ZH/ZH_word_medical.json",
  zh_car: "src/dictionaries/ZH/ZH_word_car.json",
  zh_food: "src/dictionaries/ZH/ZH_word_food.json",
  zh_animal: "src/dictionaries/ZH/ZH_word_animal.json",
  zh_diming: "src/dictionaries/ZH/ZH_word_diming.json",
  zh_lishimingren: "src/dictionaries/ZH/ZH_word_lishimingren.json",
};

export const IGNORED_TAGS = [
  "script",
  "style",
  "noscript",
  "textarea",
  "input",
  "pre",
  "code",
];

export const DEFAULT_COLORS = {
  noun: "#4299e1",
  verb: "#f56565",
  adj: "#48bb78",
  other: "#805ad5",
};

export const DEFAULT_APPEARANCE = {
  theme: "default",
  colors: { ...DEFAULT_COLORS },
  highlightDensity: 50,
  scale: 100,
  weight: 400,
  spacing: 0,
  underline: false,
};

export const DEFAULT_DICTIONARIES = {
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

export const DEFAULT_SETTINGS = {
  enabled: true,
  processingWaitForIdle: true,
  debug: true,
  appearance: DEFAULT_APPEARANCE,
  dictionaries: DEFAULT_DICTIONARIES,
};
