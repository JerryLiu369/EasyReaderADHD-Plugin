/**
 * 日志工具
 *
 * process.env.NODE_ENV 由 esbuild define 在编译期注入。
 * 开发构建（npm run dev/watch）：DEV=true，所有日志输出。
 * 生产构建（npm run build）：esbuild 将 if (false) 分支完全删除，零运行时开销。
 *
 * warn / error 无论构建模式始终输出，确保线上问题可见。
 */

// eslint-disable-next-line no-undef
const DEV = process.env.NODE_ENV === "development";

export const logger = {
  info: (...args) => {
    if (DEV) console.log("EasyReaderADHD:", ...args);
  },
  observer: (...args) => {
    if (DEV) console.log("EasyReaderADHD [Observer]", ...args);
  },
  dict: (...args) => {
    if (DEV) console.log("EasyReaderADHD [DICT]", ...args);
  },
  warn: (...args) => {
    // 始终输出，不受构建模式影响
    console.warn("EasyReaderADHD [WARN]:", ...args);
  },
  error: (...args) => {
    // 始终输出，不受构建模式影响
    console.error("EasyReaderADHD [ERROR]:", ...args);
  },
  debug: (...args) => {
    if (DEV) console.debug("EasyReaderADHD [DEBUG]:", ...args);
  },
};

