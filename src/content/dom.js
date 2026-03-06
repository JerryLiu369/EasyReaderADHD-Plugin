/**
 * DOM 处理和观察模块
 */

import { IGNORED_TAGS } from "../shared/constants.js";
import { logger } from "../shared/logger.js";
import { detectLanguage } from "../shared/language.js";
import { segmentCJKText, segmentSpaceBasedText } from "./segmentation.js";
import { loadDictionaries, getWordSet } from "./dictionary.js";

const STABLE_TEXT_DELAY = 800;
const MAX_PENDING_NODES = 2000; // 防止动态页面节点无限积累
const pendingTextNodes = new Set();
let lastChangeMap = new WeakMap();
let stableTimer = null;
let latestSettings = null;

function shouldSkipTextNode(node) {
  const parent = node?.parentElement;
  if (!parent) return true;
  if (
    typeof parent.closest === "function" &&
    parent.closest(".adhd-processed")
  ) {
    return true;
  }
  const tag = parent.tagName.toLowerCase();
  if (IGNORED_TAGS.includes(tag)) return true;
  if (!node.textContent || !node.textContent.trim()) return true;
  return false;
}

function clearPendingProcessing() {
  pendingTextNodes.clear();
  if (stableTimer) {
    clearTimeout(stableTimer);
    stableTimer = null;
  }
  lastChangeMap = new WeakMap();
}

export function updateProcessingSettings(settings) {
  latestSettings = settings;
  if (!settings?.enabled) {
    clearPendingProcessing();
  }
}

export function enqueueTextNodesForProcessing(nodes, settings) {
  latestSettings = settings;
  if (!settings?.enabled) {
    clearPendingProcessing();
    return 0;
  }
  if (!nodes || nodes.length === 0) return 0;

  const now = Date.now();
  let queued = 0;

  for (const node of nodes) {
    if (!node || node.nodeType !== Node.TEXT_NODE) continue;
    if (shouldSkipTextNode(node)) continue;
    // 超过上限则丢弃，避免无限滚动页面内存无限增长
    if (pendingTextNodes.size >= MAX_PENDING_NODES) break;
    lastChangeMap.set(node, now);
    pendingTextNodes.add(node);
    queued++;
  }

  if (queued > 0) {
    scheduleStableProcessing();
  }
  return queued;
}

function scheduleStableProcessing() {
  if (stableTimer) return;
  stableTimer = setTimeout(async () => {
    stableTimer = null;

    if (!latestSettings?.enabled) {
      clearPendingProcessing();
      return;
    }

    const now = Date.now();
    const ready = [];

    for (const node of Array.from(pendingTextNodes)) {
      if (!node.isConnected) {
        pendingTextNodes.delete(node);
        continue;
      }
      const last = lastChangeMap.get(node) || 0;
      if (now - last >= STABLE_TEXT_DELAY) {
        pendingTextNodes.delete(node);
        ready.push(node);
      }
    }

    if (ready.length > 0) {
      await processNodeList(ready, latestSettings);
    }

    // 只有仍处于启用状态才重新调度，否则直接清空，避免僵尸计时器
    if (pendingTextNodes.size > 0 && latestSettings?.enabled) {
      scheduleStableProcessing();
    } else if (pendingTextNodes.size > 0) {
      pendingTextNodes.clear();
    }
  }, STABLE_TEXT_DELAY);
}

export function getEnabledDicts(settings) {
  if (!settings?.dictionaries) return [];
  return Object.entries(settings.dictionaries)
    .filter(([_, config]) => config?.enabled)
    .map(([dictId]) => dictId);
}

export async function processTextNode(textNode, settings, dictIds) {
  if (shouldSkipTextNode(textNode)) return false;
  const text = textNode.textContent;
  if (!text.trim()) return false;

  // dictIds 由 processNodeList 批量计算后传入，避免每个节点重复调用 getEnabledDicts
  if (!dictIds) dictIds = getEnabledDicts(settings);
  if (dictIds.length === 0) return false;

  const language = detectLanguage(text);
  const segments =
    language === "zh" || language === "ja"
      ? await segmentCJKText(text, dictIds, settings)
      : await segmentSpaceBasedText(text, dictIds, settings);

  const hasHighlight = Array.isArray(segments)
    ? segments.some((segment) => segment?.className)
    : false;

  if (!hasHighlight) return false;

  // 提前捕获 parent 引用，避免 replaceChild 前后 parentNode 发生变化
  const parent = textNode.parentNode;
  if (!parent) return false;

  try {
    const wrapper = document.createElement("span");
    wrapper.className = "adhd-processed";
    wrapper.setAttribute("data-adhd-processed", "1");

    const fragment = document.createDocumentFragment();
    segments.forEach((segment) => {
      if (!segment || segment.text === undefined || segment.text === null)
        return;
      if (segment.className) {
        const span = document.createElement("span");
        span.className = segment.className;
        span.textContent = segment.text;
        fragment.appendChild(span);
      } else {
        fragment.appendChild(document.createTextNode(segment.text));
      }
    });

    wrapper.appendChild(fragment);
    parent.replaceChild(wrapper, textNode);
    return true;
  } catch (error) {
    // replaceChild 失败时节点仍在原位，静默跳过即可
    logger.warn("DOM替换跳过:", error.message);
    return false;
  }
}

export function collectAllTextNodes() {
  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode: (node) => {
        return shouldSkipTextNode(node)
          ? NodeFilter.FILTER_REJECT
          : NodeFilter.FILTER_ACCEPT;
      },
    },
  );

  const nodes = [];
  let node;
  while ((node = walker.nextNode())) nodes.push(node);
  return nodes;
}

function waitForIdle(timeout = 1000) {
  return new Promise((resolve) => {
    if (typeof requestIdleCallback === "function") {
      requestIdleCallback((deadline) => resolve(deadline), { timeout });
    } else {
      setTimeout(
        () =>
          resolve({
            timeRemaining: () => 0,
            didTimeout: true,
          }),
        0,
      );
    }
  });
}

// 批量处理节点 - 大页面分片+空闲调度，降低卡顿
async function processBatch(tasks, processor, options = {}) {
  let processed = 0;
  if (!tasks || tasks.length === 0) return processed;

  const batchSize = options.batchSize || 200;
  const idleTimeout = options.idleTimeout || 1000;

  if (tasks.length <= batchSize) {
    const results = await Promise.all(tasks.map((task) => processor(task)));
    return results.filter(Boolean).length;
  }

  let index = 0;
  while (index < tasks.length) {
    await waitForIdle(idleTimeout);
    const slice = tasks.slice(index, index + batchSize);
    index += batchSize;
    const results = await Promise.all(slice.map((task) => processor(task)));
    processed += results.filter(Boolean).length;
  }

  return processed;
}

export async function processPage(settings) {
  if (!settings?.enabled) {
    logger.info("跳过处理: 已禁用");
    return;
  }

  // 注意：latestSettings 由调用方通过 updateProcessingSettings 设置，
  // 这里不重复调用，避免覆盖并发消息带来的更新值。

  logger.info("开始处理页面...");

  try {
    // 清空上一轮残留的待处理节点，避免重新处理时混入旧引用
    clearPendingProcessing();

    // 1. 预加载所有启用的词典和词集（关键优化！）
    const dictIds = getEnabledDicts(settings);
    if (dictIds.length === 0) {
      logger.info("没有启用的词典");
      return;
    }

    logger.info(`预加载词典: ${dictIds.join(", ")}`);
    await Promise.all([loadDictionaries(dictIds), getWordSet(dictIds)]);
    logger.info("词典预加载完成");

    // 2. 快速收集所有节点 (同步操作，通常很快)
    const textNodes = collectAllTextNodes();
    logger.info(`找到 ${textNodes.length} 个文本节点`);

    // 3. 将节点加入稳定队列（避免流式输出被提前替换）
    // 词典加载期间可能收到新的设置更新，优先使用 latestSettings
    const settingsForQueue = latestSettings || settings;
    if (!settingsForQueue?.enabled) {
      logger.info("跳过入队: 词典加载期间设置已切换为禁用");
      return;
    }
    const queued = enqueueTextNodesForProcessing(textNodes, settingsForQueue);
    logger.info(`页面文本已加入处理队列: ${queued} 个节点`);
  } catch (error) {
    logger.error("页面处理失败:", error);
  }
}

export function removeHighlights() {
  const processed = document.querySelectorAll(".adhd-processed");
  processed.forEach((el) => {
    try {
      if (!el.parentNode) return; // 防御性检查
      const text = el.textContent;
      el.parentNode.replaceChild(document.createTextNode(text), el);
    } catch (e) {
      logger.warn("清除高亮失败:", e);
    }
  });
  logger.info("已清除所有高亮");
}

// 高性能 DOM 观察者
export function setupDOMObserver(settings, callback) {
  let timeout = null;
  const elementQueue = new Set();
  const textQueue = new Set();

  const observer = new MutationObserver((mutations) => {
    if (!settings?.enabled) return;

    let hasNewNodes = false;
    for (const mutation of mutations) {
      if (mutation.type === "childList") {
        for (const node of mutation.addedNodes) {
          if (
            node.nodeType === Node.ELEMENT_NODE &&
            !node.hasAttribute("data-adhd-processed")
          ) {
            elementQueue.add(node);
            hasNewNodes = true;
          } else if (node.nodeType === Node.TEXT_NODE) {
            textQueue.add(node);
            hasNewNodes = true;
          }
        }
      } else if (mutation.type === "characterData") {
        const target = mutation.target;
        if (target && target.nodeType === Node.TEXT_NODE) {
          textQueue.add(target);
          hasNewNodes = true;
        }
      }
    }

    if (hasNewNodes && !timeout) {
      // 防抖：500ms 后处理一批，避免频繁触发
      timeout = setTimeout(() => {
        const elements = Array.from(elementQueue);
        const directTextNodes = Array.from(textQueue);
        elementQueue.clear();
        textQueue.clear();
        timeout = null;

        const allTextNodes = [];
        for (const el of elements) {
          allTextNodes.push(...collectTextNodesInContainer(el));
        }
        allTextNodes.push(...directTextNodes);

        if (allTextNodes.length > 0 && typeof callback === "function") {
          callback(allTextNodes);
        }
      }, 500);
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
    characterData: true,
  });

  logger.observer("启动高性能 DOM 监听");

  return {
    disconnect: () => {
      observer.disconnect();
      if (timeout) clearTimeout(timeout);
      elementQueue.clear();
      textQueue.clear();
      logger.observer("停止监听");
    },
  };
}

export function collectTextNodesInContainer(container) {
  const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, {
    acceptNode: (node) => {
      return shouldSkipTextNode(node)
        ? NodeFilter.FILTER_REJECT
        : NodeFilter.FILTER_ACCEPT;
    },
  });

  const nodes = [];
  let node;
  while ((node = walker.nextNode())) nodes.push(node);
  return nodes;
}

export async function processNodeList(nodes, settings) {
  if (!nodes || nodes.length === 0) return 0;
  // 计算一次 dictIds，通过闭包传给每个节点，避免每节点重复 O(n) 过滤
  const dictIds = getEnabledDicts(settings);
  if (dictIds.length === 0) return 0;
  return await processBatch(nodes, (node) => processTextNode(node, settings, dictIds), {
    batchSize: 200,
    idleTimeout: 1000,
  });
}
