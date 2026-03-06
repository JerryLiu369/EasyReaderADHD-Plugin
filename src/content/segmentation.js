/**
 * 文本分词模块
 */

import {
  lookupWord,
  normalizePos,
  loadDictionaries,
  getWordSet,
} from "./dictionary.js";

function getDictConfig(dictId, settings) {
  if (!settings?.dictionaries) return null;
  if (settings.dictionaries[dictId]) return settings.dictionaries[dictId];

  if (dictId && dictId.includes("_")) {
    const baseId = dictId.split("_")[0];
    if (settings.dictionaries[baseId]) return settings.dictionaries[baseId];
  }

  return null;
}

// 检查是否应该高亮某个词性
function shouldHighlightPos(dictId, normalizedPos, settings) {
  const dictConfig = getDictConfig(dictId, settings);
  const defaultHighlight =
    normalizedPos === "n" || normalizedPos === "v" || normalizedPos === "a";

  if (!dictConfig || !dictConfig.pos) {
    return defaultHighlight;
  }

  // normalizePos 只返回 "n" | "v" | "a" | "other"，与下面 key 一一对应
  const posMap = {
    n: "noun",
    v: "verb",
    a: "adj",
    other: "other",
  };

  const posKey = posMap[normalizedPos] || "other";
  return dictConfig.pos[posKey] === true;
}

function getHighlightDensity(settings) {
  const raw = settings?.appearance?.highlightDensity;
  const value = typeof raw === "number" ? raw : 50;
  return Math.min(100, Math.max(0, value));
}

function shouldHighlightByDensity(settings) {
  const density = getHighlightDensity(settings);
  if (density >= 100) return true;
  if (density <= 0) return false;
  return Math.random() < density / 100;
}

// 提取为常量，避免在每次调用中重新编译正则
const STRIP_NON_WORD = /[^\w\-']/g;

function forwardMaxMatch(text, wordSet) {
  const result = [];
  let i = 0;
  while (i < text.length) {
    let matchLen = 0;
    for (let len = Math.min(8, text.length - i); len > 0; len--) {
      const word = text.slice(i, i + len);
      if (wordSet.has(word)) {
        matchLen = len;
        break;
      }
    }
    if (matchLen > 0) {
      result.push(text.slice(i, i + matchLen));
      i += matchLen;
    } else {
      result.push(text[i]);
      i++;
    }
  }
  return result;
}

// 词性判断 + 密度控制后推入 segment，两处分词函数共用
function pushSegment(segments, displayText, result, settings) {
  if (result) {
    const normalized = normalizePos(result.pos);
    if (
      shouldHighlightPos(result.dictId, normalized, settings) &&
      normalized !== "other" &&
      shouldHighlightByDensity(settings)
    ) {
      segments.push({ text: displayText, className: `adhd-${normalized}` });
      return;
    }
  }
  segments.push({ text: displayText });
}

export async function segmentCJKText(text, dictIds, settings) {
  // 并行加载词集和词典（均有缓存，首次调用可节省等待时间）
  const [allWords, dictMap] = await Promise.all([
    getWordSet(dictIds),
    loadDictionaries(dictIds),
  ]);

  if (allWords.size === 0) return [{ text }];

  const tokens = forwardMaxMatch(text, allWords);
  const segments = [];

  for (const token of tokens) {
    if (!token || token.length === 0) {
      segments.push({ text: token });
      continue;
    }

    // 不要 trim()，保留原始空格！
    const testToken = token.trim();
    if (!testToken) {
      segments.push({ text: token }); // 纯空格保留
      continue;
    }

    // 忽略单字词，避免噪声高亮
    if (testToken.length === 1) {
      segments.push({ text: token });
      continue;
    }

    let result = null;
    for (const [dictId, dictData] of dictMap) {
      if (dictData[testToken]) {
        result = { dictId, pos: dictData[testToken].pos };
        break;
      }
    }

    pushSegment(segments, token, result, settings);
  }

  return segments;
}

export async function segmentSpaceBasedText(text, dictIds, settings) {
  const dictMap = await loadDictionaries(dictIds);
  if (dictMap.size === 0) return [{ text }];

  const words = text.split(/(\s+)/);
  const segments = [];

  for (const word of words) {
    if (/^\s+$/.test(word)) {
      segments.push({ text: word });
      continue;
    }

    const cleanWord = word.replace(STRIP_NON_WORD, "");
    if (!cleanWord) {
      segments.push({ text: word });
      continue;
    }

    // 忽略单字词，避免噪声高亮
    if (cleanWord.length === 1) {
      segments.push({ text: word });
      continue;
    }

    let result = await lookupWord(cleanWord, dictIds);

    // 尝试复数形式
    if (!result && cleanWord.endsWith("s") && cleanWord.length > 1) {
      result = await lookupWord(cleanWord.slice(0, -1), dictIds);
    }

    // 尝试去掉 -ed
    if (!result && cleanWord.endsWith("ed") && cleanWord.length > 3) {
      result = await lookupWord(cleanWord.slice(0, -2), dictIds);
    }

    // 尝试去掉 -ing
    if (!result && cleanWord.endsWith("ing") && cleanWord.length > 4) {
      result = await lookupWord(cleanWord.slice(0, -3), dictIds);
    }

    pushSegment(segments, word, result, settings);
  }

  return segments;
}
