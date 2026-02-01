/**
 * DOM 处理和观察模块
 */

import {
  IGNORED_TAGS,
  DEFAULT_APPEARANCE,
  DEFAULT_COLORS,
  DEFAULT_DICTIONARIES,
} from "../shared/constants.js";
import { logger } from "../shared/logger.js";
import { detectLanguage } from "../shared/language.js";
import { segmentCJKText, segmentSpaceBasedText } from "./segmentation.js";

export function getEnabledDicts(settings) {
  if (!settings?.dictionaries) return [];
  return Object.entries(settings.dictionaries)
    .filter(([_, config]) => config?.enabled)
    .map(([dictId]) => dictId);
}

export async function processTextNode(textNode, settings) {
  const text = textNode.textContent;
  if (!text.trim()) return false;

  const dictIds = getEnabledDicts(settings);
  if (dictIds.length === 0) return false;

  const language = detectLanguage(text);
  const html =
    language === "zh" || language === "ja"
      ? await segmentCJKText(text, dictIds)
      : await segmentSpaceBasedText(text, dictIds);

  if (!html.includes('class="adhd-')) return false;

  try {
    const wrapper = document.createElement("span");
    wrapper.innerHTML = html;
    wrapper.className = "adhd-processed";
    wrapper.setAttribute("data-adhd-processed", "1");
    textNode.parentNode.replaceChild(wrapper, textNode);
    return true;
  } catch (error) {
    logger.error("DOM替换失败:", error);
    return false;
  }
}

export function collectAllTextNodes() {
  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode: (node) => {
        const parent = node.parentElement;
        if (!parent) return NodeFilter.FILTER_REJECT;
        const tag = parent.tagName.toLowerCase();
        if (IGNORED_TAGS.includes(tag)) return NodeFilter.FILTER_REJECT;
        if (!node.textContent.trim()) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      },
    },
  );

  const nodes = [];
  let node;
  while ((node = walker.nextNode())) nodes.push(node);
  return nodes;
}

export function collectTextNodesInContainer(container) {
  const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, {
    acceptNode: (node) => {
      const parent = node.parentElement;
      if (!parent) return NodeFilter.FILTER_REJECT;
      const tag = parent.tagName.toLowerCase();
      if (IGNORED_TAGS.includes(tag)) return NodeFilter.FILTER_REJECT;
      if (!node.textContent.trim()) return NodeFilter.FILTER_REJECT;
      return NodeFilter.FILTER_ACCEPT;
    },
  });

  const nodes = [];
  let node;
  while ((node = walker.nextNode())) nodes.push(node);
  return nodes;
}

export async function waitForStablePage(maxWait = 15000, checkInterval = 500) {
  return new Promise((resolve) => {
    let lastLength = document.body.innerHTML.length;
    let stableTime = 0;
    const startTime = Date.now();

    const check = () => {
      const currentLength = document.body.innerHTML.length;
      if (currentLength === lastLength) {
        stableTime += checkInterval;
      } else {
        stableTime = 0;
        lastLength = currentLength;
      }

      if (stableTime >= 1000 || Date.now() - startTime >= maxWait) {
        resolve(true);
      } else {
        setTimeout(check, checkInterval);
      }
    };

    setTimeout(check, checkInterval);
  });
}

export async function processPage(settings) {
  if (!settings?.enabled) {
    logger.info("跳过处理: 已禁用");
    return;
  }

  logger.info("开始处理页面...");

  try {
    const textNodes = collectAllTextNodes();
    logger.info(`找到 ${textNodes.length} 个文本节点`);

    let processedCount = 0;
    for (const textNode of textNodes) {
      if (await processTextNode(textNode, settings)) {
        processedCount++;
      }
    }

    logger.info(`页面处理完成: ${processedCount} 个节点已高亮`);
  } catch (error) {
    logger.error("页面处理失败:", error);
  }
}

export function removeHighlights() {
  const processed = document.querySelectorAll(".adhd-processed");
  processed.forEach((el) => {
    try {
      const text = el.textContent;
      el.parentNode.replaceChild(document.createTextNode(text), el);
    } catch (e) {}
  });
  logger.info("已清除所有高亮");
}

export function setupDOMObserver(settings, onNodesAdded) {
  let observer = null;
  let pendingNodes = [];
  let pendingNodesSet = new WeakSet();
  let processingTimeout = null;
  let observerSuspended = false;

  function handleMutations(mutations) {
    if (!settings?.enabled || observerSuspended) return;

    for (const mutation of mutations) {
      for (const node of mutation.addedNodes) {
        if (node.nodeType !== Node.ELEMENT_NODE) continue;
        if (node.closest?.(".adhd-processed")) continue;
        if (pendingNodesSet.has(node)) continue;

        let shouldAdd = true;
        for (let i = pendingNodes.length - 1; i >= 0; i--) {
          const existing = pendingNodes[i];
          if (!existing?.isConnected) {
            pendingNodesSet.delete(existing);
            pendingNodes.splice(i, 1);
            continue;
          }
          if (node.contains(existing)) {
            pendingNodesSet.delete(existing);
            pendingNodes.splice(i, 1);
            continue;
          }
          if (existing.contains(node)) {
            shouldAdd = false;
            break;
          }
        }
        if (!shouldAdd) continue;

        pendingNodesSet.add(node);
        pendingNodes.push(node);
      }
    }

    if (pendingNodes.length > 0 && !processingTimeout) {
      processingTimeout = setTimeout(() => {
        if (onNodesAdded) {
          onNodesAdded([...pendingNodes]);
        }
        pendingNodes = [];
        pendingNodesSet = new WeakSet();
        processingTimeout = null;
      }, 200);
    }
  }

  observer = new MutationObserver(handleMutations);
  observer.observe(document.body, { childList: true, subtree: true });

  logger.info("DOM观察器已启动");

  return {
    stop() {
      if (observer) {
        observer.disconnect();
        observer = null;
      }
      pendingNodes = [];
      pendingNodesSet = new WeakSet();
      if (processingTimeout) {
        clearTimeout(processingTimeout);
        processingTimeout = null;
      }
    },
  };
}
