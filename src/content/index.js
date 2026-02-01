/**
 * Content Script 入口点
 */

import {
  loadSettings,
  saveSettings,
  mergeSettings,
  onSettingsChange,
} from "./settings.js";
import { applyStyles, removeStyles } from "./styles.js";
import {
  processPage,
  removeHighlights,
  setupDOMObserver,
  collectTextNodesInContainer,
} from "./dom.js";
import { processTextNode, waitForStablePage } from "./dom.js";
import { logger } from "../shared/logger.js";

let currentSettings = null;
let domObserver = null;

async function initialize() {
  logger.info("初始化 EasyReaderADHD 插件...");

  try {
    currentSettings = await loadSettings();

    if (!currentSettings.enabled) {
      logger.info("插件已禁用");
      return;
    }

    applyStyles(currentSettings);

    await waitForStablePage();

    await processPage(currentSettings);

    domObserver = setupDOMObserver(currentSettings, async (addedNodes) => {
      for (const node of addedNodes) {
        const textNodes = collectTextNodesInContainer(node);
        for (const textNode of textNodes) {
          try {
            await processTextNode(textNode, currentSettings);
          } catch (error) {
            logger.error("处理新节点失败:", error);
          }
        }
      }
    });

    logger.info("插件初始化完成");
  } catch (error) {
    logger.error("初始化失败:", error);
  }
}

function handleMessage(request, sender, sendResponse) {
  logger.debug("接收消息:", request.action);

  if (request.action === "enable") {
    currentSettings.enabled = true;
    applyStyles(currentSettings);
    processPage(currentSettings);
    sendResponse({ success: true, message: "已启用" });
  } else if (request.action === "disable") {
    currentSettings.enabled = false;
    removeHighlights();
    removeStyles();
    if (domObserver?.stop) domObserver.stop();
    sendResponse({ success: true, message: "已禁用" });
  } else if (request.action === "updateSettings") {
    currentSettings = mergeSettings(currentSettings, request.settings);
    applyStyles(currentSettings);
    if (currentSettings.enabled) {
      removeHighlights();
      processPage(currentSettings);
    } else {
      removeHighlights();
      removeStyles();
    }
    sendResponse({ success: true, message: "设置已更新" });
  } else if (request.action === "reprocess") {
    if (currentSettings.enabled) {
      removeHighlights();
      processPage(currentSettings);
      sendResponse({ success: true, message: "已重新处理" });
    } else {
      sendResponse({ success: false, message: "插件已禁用" });
    }
  }
}

chrome.runtime.onMessage.addListener(handleMessage);

onSettingsChange((newSettings) => {
  currentSettings = newSettings;
  if (currentSettings.enabled) {
    applyStyles(currentSettings);
    removeHighlights();
    processPage(currentSettings).catch((error) => {
      logger.error("设置变化后处理失败:", error);
    });
  } else {
    removeHighlights();
    removeStyles();
    if (domObserver?.stop) domObserver.stop();
  }
});

initialize();
