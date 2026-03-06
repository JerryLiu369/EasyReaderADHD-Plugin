/**
 * 词典加载和查询模块
 */

import { DICT_FILES } from "../shared/constants.js";
import { logger } from "../shared/logger.js";

const dictCache = new Map();
const pendingDictLoads = new Map(); // 防止并发重复加载同一词典
const wordSetCache = new Map(); // 缓存词集，避免重复构建
const pendingWordSets = new Map(); // 防止并发重复构建同一词集

export async function loadDictionary(dictId) {
  if (dictCache.has(dictId)) {
    return dictCache.get(dictId);
  }

  // 已有进行中的请求，直接复用，避免重复 fetch
  if (pendingDictLoads.has(dictId)) {
    return pendingDictLoads.get(dictId);
  }

  const filePath = DICT_FILES[dictId];
  if (!filePath) {
    logger.warn(`未知的词典ID: ${dictId}`);
    return null;
  }

  const promise = (async () => {
    try {
      const response = await fetch(chrome.runtime.getURL(filePath));
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      const dictData =
        data?.words && typeof data.words === "object" ? data.words : data;
      dictCache.set(dictId, dictData);
      logger.dict(`已加载词典: ${dictId} (${Object.keys(dictData).length} 条目)`);
      return dictData;
    } catch (error) {
      logger.error(`加载词典失败 ${dictId}:`, error);
      return null;
    } finally {
      pendingDictLoads.delete(dictId);
    }
  })();

  pendingDictLoads.set(dictId, promise);
  return promise;
}

export async function loadDictionaries(dictIds) {
  const loadPromises = dictIds.map((id) => loadDictionary(id));
  const results = await Promise.all(loadPromises);
  const dictMap = new Map();
  dictIds.forEach((id, index) => {
    if (results[index]) dictMap.set(id, results[index]);
  });
  return dictMap;
}

// 获取词集（用于分词），带缓存
export async function getWordSet(dictIds) {
  // 用副本排序，避免 mutate 传入的数组
  const cacheKey = [...dictIds].sort().join(",");

  if (wordSetCache.has(cacheKey)) {
    return wordSetCache.get(cacheKey);
  }

  // 已有进行中的构建，直接复用
  if (pendingWordSets.has(cacheKey)) {
    return pendingWordSets.get(cacheKey);
  }

  const promise = (async () => {
    try {
      const dictMap = await loadDictionaries(dictIds);
      const wordSet = new Set();
      dictMap.forEach((dictData) => {
        Object.keys(dictData).forEach((word) => wordSet.add(word));
      });
      wordSetCache.set(cacheKey, wordSet);
      logger.dict(`构建词集缓存: ${cacheKey} (${wordSet.size} 词)`);
      return wordSet;
    } finally {
      pendingWordSets.delete(cacheKey);
    }
  })();

  pendingWordSets.set(cacheKey, promise);
  return promise;
}

export async function lookupWord(word, dictIds) {
  if (!word || !dictIds?.length) return null;

  const dictMap = await loadDictionaries(dictIds);
  const lowerWord = word.toLowerCase();

  for (const [dictId, dictData] of dictMap) {
    if (dictData[word]) {
      return { dictId, pos: dictData[word].pos };
    }
    if (dictData[lowerWord]) {
      return { dictId, pos: dictData[lowerWord].pos };
    }
  }
  return null;
}

export function normalizePos(pos) {
  if (!pos) return "other";
  const posList = Array.isArray(pos) ? pos : [pos];
  if (posList.some((p) => p === "n" || p === "noun")) return "n";
  if (posList.some((p) => p === "v" || p === "verb")) return "v";
  if (posList.includes("adj")) return "a";
  return "other";
}
