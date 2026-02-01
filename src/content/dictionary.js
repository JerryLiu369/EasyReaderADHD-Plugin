/**
 * 词典加载和查询模块
 */

import { DICT_FILES } from "../shared/constants.js";
import { logger } from "../shared/logger.js";

const dictCache = new Map();

export async function loadDictionary(dictId) {
  if (dictCache.has(dictId)) {
    return dictCache.get(dictId);
  }

  const filePath = DICT_FILES[dictId];
  if (!filePath) {
    logger.warn(`未知的词典ID: ${dictId}`);
    return null;
  }

  try {
    const response = await fetch(chrome.runtime.getURL(filePath));
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    dictCache.set(dictId, data);
    logger.dict(`已加载词典: ${dictId} (${Object.keys(data).length} 条目)`);
    return data;
  } catch (error) {
    logger.error(`加载词典失败 ${dictId}:`, error);
    return null;
  }
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

export async function lookupWord(word, dictIds) {
  if (!word || !dictIds?.length) return null;

  const dictMap = await loadDictionaries(dictIds);
  const lowerWord = word.toLowerCase();

  for (const [dictId, dictData] of dictMap) {
    for (const [dictWord, info] of Object.entries(dictData)) {
      if (dictWord.toLowerCase() === lowerWord) {
        return { dictId, pos: info.pos };
      }
    }
    if (word.includes(" ") && dictData[word]) {
      return { dictId, pos: dictData[word].pos };
    }
  }
  return null;
}

export function normalizePos(pos) {
  if (!pos) return "other";
  const posList = Array.isArray(pos) ? pos : [pos];
  if (posList.some((p) => p === "n" || p === "noun")) return "noun";
  if (posList.some((p) => p === "v" || p === "verb")) return "verb";
  if (posList.includes("adj")) return "adj";
  return "other";
}
