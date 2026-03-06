/**
 * 日志工具
 */

import { DEFAULT_SETTINGS } from "./constants.js";

// 初始值从默认设置读取；运行时可通过 setLogEnabled() 动态调整
let enabled = DEFAULT_SETTINGS.debug === true;

/** 由 content script 在加载真实设置后调用，以便按用户配置开关日志 */
export function setLogEnabled(value) {
  enabled = !!value;
}

export const logger = {
  info: (...args) => {
    if (enabled) console.log("EasyReaderADHD:", ...args);
  },
  observer: (...args) => {
    if (enabled) console.log("EasyReaderADHD [Observer]", ...args);
  },
  dict: (...args) => {
    if (enabled) console.log("EasyReaderADHD [DICT]", ...args);
  },
  warn: (...args) => {
    if (enabled) console.warn("EasyReaderADHD [WARN]:", ...args);
  },
  error: (...args) => {
    if (enabled) console.error("EasyReaderADHD [ERROR]:", ...args);
  },
  debug: (...args) => {
    if (enabled) console.debug("EasyReaderADHD [DEBUG]:", ...args);
  },
};
