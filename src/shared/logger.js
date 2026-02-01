/**
 * 日志工具
 */

export const logger = {
  info: (...args) => console.log("EasyReaderADHD:", ...args),
  observer: (...args) => console.log("EasyReaderADHD [Observer]", ...args),
  dict: (...args) => console.log("EasyReaderADHD [DICT]", ...args),
  warn: (...args) => console.warn("EasyReaderADHD [WARN]:", ...args),
  error: (...args) => console.error("EasyReaderADHD [ERROR]:", ...args),
  debug: (...args) => {
    if (globalThis._adhdSettings?.debug) {
      console.debug("EasyReaderADHD [DEBUG]:", ...args);
    }
  },
};
