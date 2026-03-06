/**
 * Content Script 入口点
 */

import { loadSettings, mergeSettings, onSettingsChange, ensureSettingsStructure } from "./settings.js";
import { applyStyles, removeStyles } from "./styles.js";
import {
  processPage,
  removeHighlights,
  setupDOMObserver,
  enqueueTextNodesForProcessing,
  updateProcessingSettings,
} from "./dom.js";
import { logger } from "../shared/logger.js";

let currentSettings = null;
let domObserver = null;
let processPageInFlight = false; // 防止并发 processPage 调用互相覆盖设置

// 证明模块已执行：打印版本与 URL，设置全局标识，便于调试
try {
  const _manifest = chrome.runtime.getManifest();
  const _version =
    _manifest && _manifest.version ? _manifest.version : "unknown";
  logger.info(
    `🚀 EasyReaderADHD content script loaded — v${_version} — ${location.href}`,
  );
  globalThis.__EasyReaderADHD = globalThis.__EasyReaderADHD || {};
  globalThis.__EasyReaderADHD.version = _version;
  globalThis.__EasyReaderADHD.startedAt = Date.now();
} catch (e) {
  logger.warn("无法读取扩展清单信息:", e);
}

// 停用插件：清除高亮、移除样式、断开观察者
function disablePlugin() {
  removeHighlights();
  removeStyles();
  if (domObserver) {
    domObserver.disconnect();
    domObserver = null;
  }
}

// 启动 DOM 观察者（复用同一回调逻辑）
function startObserver() {
  domObserver = setupDOMObserver(currentSettings, (textNodes) => {
    if (textNodes.length > 0) {
      logger.observer(`动态内容: 处理 ${textNodes.length} 个文本节点`);
      enqueueTextNodesForProcessing(textNodes, currentSettings);
    }
  });
}

async function initialize() {
  logger.info("初始化 EasyReaderADHD 插件...");

  try {
    currentSettings = await loadSettings();
    logger.info("加载的设置:", currentSettings);
    updateProcessingSettings(currentSettings);

    if (!currentSettings?.enabled) {
      logger.info("插件已禁用");
      return;
    }

    applyStyles(currentSettings);
    await processPage(currentSettings);
    startObserver();

    logger.info("插件初始化完成");
  } catch (error) {
    logger.error("初始化失败:", error);
  }
}

function handleMessage(request, sender, sendResponse) {
  logger.debug("接收消息:", request.action);

  if (!currentSettings) {
    currentSettings = ensureSettingsStructure(null);
  }

  // 包裹在 async IIFE 中，以便正确 await processPage 并统一捕获错误
  // 外层函数 return true 告知 Chrome 消息通道保持开启，等待异步 sendResponse
  (async () => {
    if (request.action === "enable") {
      currentSettings.enabled = true;
      updateProcessingSettings(currentSettings);
      applyStyles(currentSettings);
      await processPage(currentSettings);
      sendResponse({ success: true, message: "已启用" });
    } else if (request.action === "disable") {
      currentSettings.enabled = false;
      updateProcessingSettings(currentSettings);
      disablePlugin();
      sendResponse({ success: true, message: "已禁用" });
    } else if (request.action === "updateSettings") {
      currentSettings = mergeSettings(currentSettings, request.settings);
      updateProcessingSettings(currentSettings);
      applyStyles(currentSettings);
      if (currentSettings.enabled) {
        removeHighlights();
        await processPage(currentSettings);
        if (!domObserver) startObserver();
      } else {
        disablePlugin();
      }
      sendResponse({ success: true, message: "设置已更新" });
    } else if (request.action === "reprocess") {
      if (currentSettings.enabled) {
        updateProcessingSettings(currentSettings);
        removeHighlights();
        await processPage(currentSettings);
        sendResponse({ success: true, message: "已重新处理" });
      } else {
        sendResponse({ success: false, message: "插件已禁用" });
      }
    }
  })().catch((error) => {
    logger.error("消息处理失败:", error);
    sendResponse({ success: false, message: "内部错误" });
  });

  return true; // 保持消息通道开启，等待异步 sendResponse
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
    if (!processPageInFlight) {
      processPageInFlight = true;
      processPage(currentSettings)
        .catch((error) => {
          logger.error("设置变化后处理失败:", error);
        })
        .finally(() => {
          processPageInFlight = false;
        });
    } else {
      logger.info("onSettingsChange: processPage 正在运行，跳过重复启动");
    }
  } else {
    removeHighlights();
    removeStyles();
  }
});

initialize();
