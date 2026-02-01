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
  other: "#805ad6",
};

export const DEFAULT_APPEARANCE = {
  colors: { ...DEFAULT_COLORS },
  highlightDensity: 50,
  scale: 100,
  weight: 400,
  spacing: 0,
  underline: false,
};

export const DEFAULT_DICTIONARIES = {
  zh: { enabled: true, pos: { noun: true, verb: true, adj: true } },
  en: { enabled: true, pos: { noun: true, verb: true, adj: true } },
};

export const DEFAULT_SETTINGS = {
  enabled: true,
  processingWaitForIdle: true,
  debug: true,
  appearance: DEFAULT_APPEARANCE,
  dictionaries: DEFAULT_DICTIONARIES,
};
