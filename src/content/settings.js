/**
 * 设置管理模块
 */

import { DEFAULT_SETTINGS } from "../shared/constants.js";
import { logger } from "../shared/logger.js";

const STORAGE_KEY = "adhdSettings";

export async function loadSettings() {
  try {
    const stored = await chrome.storage.sync.get(STORAGE_KEY);
    return ensureSettingsStructure(
      stored[STORAGE_KEY] || { ...DEFAULT_SETTINGS },
    );
  } catch (error) {
    logger.error("加载设置失败:", error);
    return { ...DEFAULT_SETTINGS };
  }
}

export async function saveSettings(settings) {
  try {
    const toSave = ensureSettingsStructure(settings);
    await chrome.storage.sync.set({ [STORAGE_KEY]: toSave });
    logger.info("设置已保存");
    return toSave;
  } catch (error) {
    logger.error("保存设置失败:", error);
    return null;
  }
}

export function mergeSettings(current, updates) {
  if (!current || !updates) return current || {};

  const merged = JSON.parse(JSON.stringify(current)); // 深拷贝

  // 合并基本字段
  if (updates.enabled !== undefined) merged.enabled = updates.enabled;

  // 合并 appearance
  if (updates.appearance) {
    merged.appearance = merged.appearance || {};
    Object.keys(updates.appearance).forEach((key) => {
      if (key === "colors" && typeof updates.appearance.colors === "object") {
        merged.appearance.colors = merged.appearance.colors || {};
        Object.assign(merged.appearance.colors, updates.appearance.colors);
      } else {
        merged.appearance[key] = updates.appearance[key];
      }
    });
  }

  // 合并 dictionaries
  if (updates.dictionaries && typeof updates.dictionaries === "object") {
    merged.dictionaries = merged.dictionaries || {};
    Object.keys(updates.dictionaries).forEach((key) => {
      if (typeof updates.dictionaries[key] === "object") {
        merged.dictionaries[key] = {
          ...merged.dictionaries[key],
          ...updates.dictionaries[key],
        };
      } else {
        merged.dictionaries[key] = updates.dictionaries[key];
      }
    });
  }

  return merged;
}

export function ensureSettingsStructure(settings) {
  if (!settings) return { ...DEFAULT_SETTINGS };
  const ensured = { ...settings };
  if (typeof ensured.enabled !== "boolean") {
    ensured.enabled = DEFAULT_SETTINGS.enabled;
  }
  if (!ensured.appearance)
    ensured.appearance = { ...DEFAULT_SETTINGS.appearance };
  if (typeof ensured.appearance.highlightDensity !== "number") {
    ensured.appearance.highlightDensity =
      DEFAULT_SETTINGS.appearance.highlightDensity;
  }
  if (!ensured.appearance.colors)
    ensured.appearance.colors = { ...DEFAULT_SETTINGS.appearance.colors };
  if (!ensured.dictionaries)
    ensured.dictionaries = { ...DEFAULT_SETTINGS.dictionaries };
  return ensured;
}

export function onSettingsChange(callback) {
  if (typeof callback !== "function") {
    logger.warn("onSettingsChange: callback 不是函数");
    return;
  }

  try {
    chrome.storage.onChanged.addListener((changes, areaName) => {
      if (areaName === "sync" && changes[STORAGE_KEY]) {
        const newSettings = ensureSettingsStructure(
          changes[STORAGE_KEY].newValue || DEFAULT_SETTINGS,
        );
        callback(newSettings);
      }
    });
  } catch (error) {
    logger.error("监听设置变化失败:", error);
  }
}
