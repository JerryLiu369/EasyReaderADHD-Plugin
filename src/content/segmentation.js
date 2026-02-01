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

  const posMap = {
    n: "noun",
    v: "verb",
    a: "adj",
    adv: "adj",
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

export async function segmentCJKText(text, dictIds, settings) {
  // 使用缓存的词集，避免每次都遍历词典
  const allWords = await getWordSet(dictIds);
  const dictMap = await loadDictionaries(dictIds);

  if (allWords.size === 0) return text;

  const tokens = forwardMaxMatch(text, allWords);
  let html = "";

  for (const token of tokens) {
    if (!token || token.length === 0) {
      html += token;
      continue;
    }

    // 不要 trim()，保留原始空格！
    const testToken = token.trim();
    if (!testToken) {
      html += token; // 纯空格保留
      continue;
    }

    let result = null;
    dictMap.forEach((dictData, dictId) => {
      if (!result && dictData[testToken]) {
        result = { dictId, pos: dictData[testToken].pos };
      }
    });

    if (result) {
      const normalized = normalizePos(result.pos);

      // 检查是否应该高亮这个词性 + 密度控制
      if (
        shouldHighlightPos(result.dictId, normalized, settings) &&
        normalized !== "other" &&
        shouldHighlightByDensity(settings)
      ) {
        html += `<span class="adhd-${normalized}">${token}</span>`;
      } else {
        html += token;
      }
    } else {
      html += token;
    }
  }

  return html;
}

export async function segmentSpaceBasedText(text, dictIds, settings) {
  const dictMap = await loadDictionaries(dictIds);
  if (dictMap.size === 0) return text;

  const words = text.split(/(\s+)/);
  let html = "";

  for (const word of words) {
    if (/^\s+$/.test(word)) {
      html += word;
      continue;
    }

    const cleanWord = word.replace(/[^\w\-\']/g, "");
    if (!cleanWord) {
      html += word;
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

    if (result) {
      const normalized = normalizePos(result.pos);

      // 检查是否应该高亮这个词性 + 密度控制
      if (
        shouldHighlightPos(result.dictId, normalized, settings) &&
        normalized !== "other" &&
        shouldHighlightByDensity(settings)
      ) {
        html += `<span class="adhd-${normalized}">${word}</span>`;
      } else {
        html += word;
      }
    } else {
      html += word;
    }
  }

  return html;
}
