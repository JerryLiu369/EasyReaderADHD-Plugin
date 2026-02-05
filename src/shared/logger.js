/**
 * 日志工具
 */

// 日志开关配置 - 仅开发者可修改此常量
// 设置为 false 可关闭所有日志输出，适用于生产环境
const ENABLE_LOGGING = false;

export const logger = {
  info: (...args) => {
    if (ENABLE_LOGGING) console.log("EasyReaderADHD:", ...args);
  },
  observer: (...args) => {
    if (ENABLE_LOGGING) console.log("EasyReaderADHD [Observer]", ...args);
  },
  dict: (...args) => {
    if (ENABLE_LOGGING) console.log("EasyReaderADHD [DICT]", ...args);
  },
  warn: (...args) => {
    if (ENABLE_LOGGING) console.warn("EasyReaderADHD [WARN]:", ...args);
  },
  error: (...args) => {
    if (ENABLE_LOGGING) console.error("EasyReaderADHD [ERROR]:", ...args);
  },
  debug: (...args) => {
    if (ENABLE_LOGGING && globalThis._adhdSettings?.debug) {
      console.debug("EasyReaderADHD [DEBUG]:", ...args);
    }
  },
};
