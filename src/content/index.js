/**
 * Content Script 入口点
 */

import { loadSettings, mergeSettings, onSettingsChange } from "./settings.js";
import { applyStyles, removeStyles } from "./styles.js";
import {
  processPage,
  removeHighlights,
  setupDOMObserver,
  enqueueTextNodesForProcessing,
  updateProcessingSettings,
} from "./dom.js";
import { logger, setLogEnabled } from "../shared/logger.js";

let currentSettings = null;
let domObserver = null;

// 证明模块已执行：打印版本与 URL，设置全局标识，便于调试
try {
  const _manifest = chrome.runtime.getManifest();
  const _version =
    _manifest && _manifest.version ? _manifest.version : "unknown";
  logger.info(
    `🚀 EasyReaderADHD content script loaded — v${_version} — ${location.href}`,
  );
  // 供开发者在控制台交互确认
  globalThis.__EasyReaderADHD = globalThis.__EasyReaderADHD || {};
  globalThis.__EasyReaderADHD.version = _version;
  globalThis.__EasyReaderADHD.startedAt = Date.now();
} catch (e) {
  // 仅记录到控制台，不中断执行
  logger.warn("无法读取扩展清单信息:", e);
}

async function initialize() {
  logger.info("初始化 EasyReaderADHD 插件...");

  try {
    currentSettings = await loadSettings();
    setLogEnabled(currentSettings?.debug !== false);
    logger.info("加载的设置:", currentSettings);
    updateProcessingSettings(currentSettings);

    if (!currentSettings?.enabled) {
      logger.info("插件已禁用");
      return;
    }

    applyStyles(currentSettings);
    await processPage(currentSettings);

    // 启动高性能观察者
    if (currentSettings.enabled) {
      domObserver = setupDOMObserver(currentSettings, async (textNodes) => {
        if (textNodes.length > 0) {
          logger.observer(`动态内容: 处理 ${textNodes.length} 个文本节点`);
          enqueueTextNodesForProcessing(textNodes, currentSettings);
        }
      });
    }

    logger.info("插件初始化完成");
  } catch (error) {
    logger.error("初始化失败:", error);
  }
}

function handleMessage(request, sender, sendResponse) {
  logger.debug("接收消息:", request.action);

  if (!currentSettings) {
    currentSettings = { enabled: true, appearance: {}, dictionaries: {} };
  }

  if (request.action === "enable") {
    currentSettings.enabled = true;
    updateProcessingSettings(currentSettings);
    applyStyles(currentSettings);
    processPage(currentSettings).catch((e) => logger.error("启用后处理失败:", e));
    sendResponse({ success: true, message: "已启用" });
  } else if (request.action === "disable") {
    currentSettings.enabled = false;
    updateProcessingSettings(currentSettings);
    removeHighlights();
    removeStyles();
    if (domObserver) {
      domObserver.disconnect();
      domObserver = null;
    }
    sendResponse({ success: true, message: "已禁用" });
  } else if (request.action === "updateSettings") {
    currentSettings = mergeSettings(currentSettings, request.settings);
    updateProcessingSettings(currentSettings);
    applyStyles(currentSettings);
    if (currentSettings.enabled) {
      removeHighlights();
      processPage(currentSettings).catch((e) => logger.error("设置更新后处理失败:", e));
      // 确保观察者已启动
      if (!domObserver) {
        domObserver = setupDOMObserver(currentSettings, async (textNodes) => {
          if (textNodes.length > 0) {
            enqueueTextNodesForProcessing(textNodes, currentSettings);
          }
        });
      }
    } else {
      removeHighlights();
      removeStyles();
      if (domObserver) {
        domObserver.disconnect();
        domObserver = null;
      }
    }
    sendResponse({ success: true, message: "设置已更新" });
  } else if (request.action === "reprocess") {
    if (currentSettings.enabled) {
      updateProcessingSettings(currentSettings);
      removeHighlights();
      processPage(currentSettings).catch((e) => logger.error("重新处理失败:", e));
      sendResponse({ success: true, message: "已重新处理" });
    } else {
      sendResponse({ success: false, message: "插件已禁用" });
    }
  }
}

chrome.runtime.onMessage.addListener(handleMessage);

// 监听 storage changes，当 popup 写入 chrome.storage.sync 时会触发此回调
onSettingsChange((newSettings) => {
  logger.info("onSettingsChange: 接收到设置变更:", newSettings);
  currentSettings = newSettings;
  updateProcessingSettings(currentSettings);
  if (currentSettings?.enabled) {
    applyStyles(currentSettings);
    removeHighlights();
    processPage(currentSettings).catch((error) => {
      logger.error("设置变化后处理失败:", error);
    });
  } else {
    removeHighlights();
    removeStyles();
  }
});

initialize();
