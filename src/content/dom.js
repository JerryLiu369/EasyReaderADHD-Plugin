/**
 * DOM 处理和观察模块
 */

import { IGNORED_TAGS } from "../shared/constants.js";
import { logger } from "../shared/logger.js";
import { detectLanguage } from "../shared/language.js";
import { segmentCJKText, segmentSpaceBasedText } from "./segmentation.js";
import { loadDictionaries, getWordSet } from "./dictionary.js";

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
      ? await segmentCJKText(text, dictIds, settings)
      : await segmentSpaceBasedText(text, dictIds, settings);

  if (!html.includes('class="adhd-')) return false;

  try {
    // 防御性检查：确保节点仍在文档树中（动态页面很常见，静默跳过）
    if (!textNode.parentNode) {
      return false;
    }

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

// 批量处理节点 - 直接同步处理，快速完成
async function processBatch(tasks, processor) {
  let processed = 0;

  // 直接并发处理所有任务，不做过度分片
  const results = await Promise.all(tasks.map((task) => processor(task)));
  processed = results.filter(Boolean).length;

  return processed;
}

export async function processPage(settings) {
  if (!settings?.enabled) {
    logger.info("跳过处理: 已禁用");
    return;
  }

  logger.info("开始处理页面...");

  try {
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

    // 3. 串行处理节点（词典已缓存，每个节点处理很快）
    const count = await processBatch(textNodes, (node) =>
      processTextNode(node, settings),
    );

    logger.info(`页面处理完成: ${count} 个节点已高亮`);
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
    } catch (e) {}
  });
  logger.info("已清除所有高亮");
}

// 高性能 DOM 观察者
export function setupDOMObserver(settings, callback) {
  let timeout = null;
  const queue = new Set(); // 使用 Set 去重

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
            queue.add(node);
            hasNewNodes = true;
          }
        }
      }
    }

    if (hasNewNodes && !timeout) {
      // 防抖：500ms 后处理一批，避免频繁触发
      timeout = setTimeout(() => {
        const nodes = Array.from(queue);
        queue.clear();
        timeout = null;
        if (nodes.length > 0) {
          callback(nodes);
        }
      }, 500);
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });

  logger.observer("启动高性能 DOM 监听");

  return {
    disconnect: () => {
      observer.disconnect();
      if (timeout) clearTimeout(timeout);
      queue.clear();
      logger.observer("停止监听");
    },
  };
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

export async function processNodeList(nodes, settings) {
  if (!nodes || nodes.length === 0) return 0;
  return await processBatch(nodes, (node) => processTextNode(node, settings));
}
