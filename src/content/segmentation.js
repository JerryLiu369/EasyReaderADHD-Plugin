/**
 * 文本分词模块
 */

import { lookupWord, normalizePos, loadDictionaries } from "./dictionary.js";

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

export async function segmentCJKText(text, dictIds) {
  const dictMap = await loadDictionaries(dictIds);
  if (dictMap.size === 0) return text;

  const allWords = new Set();
  dictMap.forEach((dictData) => {
    Object.keys(dictData).forEach((word) => allWords.add(word));
  });

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
      html += `<span class="adhd-${normalized}">${token}</span>`;
    } else {
      html += token;
    }
  }

  return html;
}

export async function segmentSpaceBasedText(text, dictIds) {
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
      html += `<span class="adhd-${normalized}">${word}</span>`;
    } else {
      html += word;
    }
  }

  return html;
}
