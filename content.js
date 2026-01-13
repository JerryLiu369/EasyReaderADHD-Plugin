// EasyReaderADHD Content Script

const DICT_FILES = {
  en: "dictionaries/EN_word.json",
  zh: "dictionaries/ZH_word.json",
  ja: "dictionaries/JA_word.json",
  fr: "dictionaries/FR_word.json",
  es: "dictionaries/ES_word.json",
  ru: "dictionaries/RU_word.json",
  zh_chengyu: "dictionaries/ZH/ZH_word_chengyu.json",
  zh_poem: "dictionaries/ZH/ZH_word_poem.json",
  zh_it: "dictionaries/ZH/ZH_word_it.json",
  zh_caijing: "dictionaries/ZH/ZH_word_caijing.json",
  zh_law: "dictionaries/ZH/ZH_word_law.json",
  zh_medical: "dictionaries/ZH/ZH_word_medical.json",
  zh_car: "dictionaries/ZH/ZH_word_car.json",
  zh_food: "dictionaries/ZH/ZH_word_food.json",
  zh_animal: "dictionaries/ZH/ZH_word_animal.json",
  zh_diming: "dictionaries/ZH/ZH_word_diming.json",
  zh_lishimingren: "dictionaries/ZH/ZH_word_lishimingren.json",
};

const dictCache = {};
let settings = null;
let styleElement = null;

// Helper: Hex to RGBA
function hexToRgba(hex, alpha) {
  let r = 0,
    g = 0,
    b = 0;
  if (hex.length === 4) {
    r = parseInt(hex[1] + hex[1], 16);
    g = parseInt(hex[2] + hex[2], 16);
    b = parseInt(hex[3] + hex[3], 16);
  } else if (hex.length === 7) {
    r = parseInt(hex.substring(1, 3), 16);
    g = parseInt(hex.substring(3, 5), 16);
    b = parseInt(hex.substring(5, 7), 16);
  }
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

// Helper: Darken color for text
function darkenColor(hex, percent) {
  let r = parseInt(hex.substring(1, 3), 16);
  let g = parseInt(hex.substring(3, 5), 16);
  let b = parseInt(hex.substring(5, 7), 16);

  r = Math.floor((r * (100 - percent)) / 100);
  g = Math.floor((g * (100 - percent)) / 100);
  b = Math.floor((b * (100 - percent)) / 100);

  return `rgb(${r}, ${g}, ${b})`;
}

// Apply Styles dynamically
function applyStyles() {
  if (!settings || !settings.appearance) return;
  const app = settings.appearance;
  const colors = app.colors;

  if (!styleElement) {
    styleElement = document.createElement("style");
    styleElement.id = "adhd-custom-styles";
    document.head.appendChild(styleElement);
  }

  // 只有当用户主动调整了才应用，否则继承
  const scaleStyle = app.scale > 100 ? `font-size: ${app.scale / 100}em;` : "";
  // 使用 text-stroke 实现相对加粗（在原有粗细基础上加粗）
  // weight 范围 400-900，转换为 0-0.5px 的描边
  const strokeWidth = app.weight > 400 ? ((app.weight - 400) / 500) * 0.5 : 0;
  const weightStyle =
    strokeWidth > 0
      ? `-webkit-text-stroke: ${strokeWidth}px currentColor;`
      : "";

  const css = `
    .adhd-processed span {
      display: inline;
      border-radius: 3px;
      transition: background-color 0.2s;
      color: inherit !important;
      ${scaleStyle}
      ${weightStyle}
      ${
        app.spacing > 0
          ? `padding: 0 ${app.spacing}px; margin: 0 ${app.spacing / 2}px;`
          : ""
      }
      ${app.underline ? "border-bottom: 2px solid currentColor;" : ""}
    }
    
    .adhd-n { background-color: ${hexToRgba(colors.noun, 0.25)}; }
    .adhd-v { background-color: ${hexToRgba(colors.verb, 0.25)}; }
    .adhd-a, .adhd-adj { background-color: ${hexToRgba(colors.adj, 0.25)}; }
    .adhd-adv { background-color: ${hexToRgba(colors.adj, 0.25)}; }
    .adhd-comp { background-color: ${hexToRgba(colors.other, 0.25)}; }
    .adhd-other { background-color: ${hexToRgba(colors.other, 0.25)}; }
  `;

  styleElement.textContent = css;
}

// --- Logic from previous version ---

async function loadDictionary(dictId) {
  if (dictCache[dictId]) return dictCache[dictId];

  const filePath = DICT_FILES[dictId];
  if (!filePath) return null;

  try {
    const response = await fetch(chrome.runtime.getURL(filePath));
    const data = await response.json();

    const converted = {};
    if (data.words) {
      for (const [word, info] of Object.entries(data.words)) {
        if (info.pos && info.pos.length > 0) {
          converted[word] = info.pos[0];
        }
      }
    }
    dictCache[dictId] = converted;
    return converted;
  } catch (error) {
    console.error(`Load failed: ${dictId}`, error);
    return null;
  }
}

function getEnabledDictsForLanguage(lang) {
  if (!settings) return [];
  const result = [];
  if (settings.dictionaries[lang]?.enabled) result.push(lang);

  if (lang === "zh") {
    Object.keys(DICT_FILES).forEach((key) => {
      if (key.startsWith("zh_") && settings.dictionaries[key]?.enabled) {
        result.push(key);
      }
    });
  }
  return result;
}

async function lookupWord(word, dictIds) {
  for (const dictId of dictIds) {
    const dict = await loadDictionary(dictId);
    if (dict && dict[word]) {
      return { pos: dict[word], dictId };
    }
  }
  return null;
}

function shouldHighlightPos(dictId, normalizedPos) {
  const dictConfig = settings.dictionaries[dictId];
  if (!dictConfig) return false;

  const posMap = {
    n: "noun",
    noun: "noun",
    v: "verb",
    verb: "verb",
    a: "adj",
    adj: "adj",
    adv: "adj",
    other: "other",
  };

  const posKey = posMap[normalizedPos] || "other";
  return dictConfig.pos[posKey] === true;
}

function normalizePos(pos) {
  if (!pos) return "other";

  // 处理复合词性，取第一个字符判断大类
  const firstChar = pos[0].toLowerCase();

  // n开头的都是名词类（n, nr, ns, nt, nz, nrfg等）
  if (firstChar === "n") return "n";

  // v开头的都是动词类（v, vn, vd, vi等）
  if (firstChar === "v") return "v";

  // a开头的都是形容词类（a, ad, an等）
  if (firstChar === "a") return "a";

  // d是副词
  if (firstChar === "d") return "adv";

  // i是成语，通常作为形容词或副词使用
  if (firstChar === "i") return "a";

  const posMap = {
    noun: "n",
    verb: "v",
    adj: "a",
    adv: "adv",
    adverb: "adv",
  };
  return posMap[pos] || "other";
}

function detectLanguage(text) {
  const sample = text.slice(0, 200);
  if ((sample.match(/[\u4e00-\u9fa5]/g) || []).length / sample.length > 0.3)
    return "zh";
  if (
    (sample.match(/[\u3040-\u309f\u30a0-\u30ff]/g) || []).length /
      sample.length >
    0.1
  )
    return "ja";
  if ((sample.match(/[\u0400-\u04ff]/g) || []).length / sample.length > 0.3)
    return "ru";
  if (/[àâäéèêëïîôöùûüÿç]/i.test(sample)) return "fr";
  if (/[ñáéíóúü¿¡]/i.test(sample)) return "es";
  return "en";
}

function getEnglishStems(word) {
  const stems = [word];
  // Basic stemming logic omitted for brevity, assumes standard
  if (word.endsWith("s")) stems.push(word.slice(0, -1));
  if (word.endsWith("ed")) stems.push(word.slice(0, -2));
  if (word.endsWith("ing")) stems.push(word.slice(0, -3));
  return stems;
}

// 预处理：移除CJK字符之间的空格，并记录原始空格位置
// 返回 { cleanText, spaceMap } 其中 spaceMap[i] 表示 cleanText[i] 后面原本有的空格
function preprocessCJKText(text) {
  const cjkPattern = /[\u4e00-\u9fa5\u3040-\u309f\u30a0-\u30ff]/;
  let cleanText = "";
  const spaceMap = new Map(); // key: cleanText中的位置, value: 原始空格字符串

  let i = 0;
  while (i < text.length) {
    const char = text[i];

    if (cjkPattern.test(char)) {
      cleanText += char;
      const currentPos = cleanText.length - 1;

      // 检查后面是否有空格
      let spaces = "";
      let j = i + 1;
      while (j < text.length && /\s/.test(text[j])) {
        spaces += text[j];
        j++;
      }

      // 如果后面有空格，且空格后面是CJK字符，记录这些空格但不加入cleanText
      if (spaces.length > 0 && j < text.length && cjkPattern.test(text[j])) {
        spaceMap.set(currentPos, spaces);
        i = j; // 跳过空格
      } else {
        i++;
      }
    } else {
      cleanText += char;
      i++;
    }
  }

  return { cleanText, spaceMap };
}

// 检测是否支持 Intl.Segmenter
const hasIntlSegmenter =
  typeof Intl !== "undefined" && typeof Intl.Segmenter === "function";

// 只打印一次分词方式日志
let segmenterLogPrinted = false;
function logSegmenterType() {
  if (!segmenterLogPrinted) {
    console.log("EasyReaderADHD: 使用双向最大匹配进行中文分词（基于词典）");
    segmenterLogPrinted = true;
  }
}

// 使用 Intl.Segmenter 进行分词（方案4），支持恢复原始空格
async function segmentWithIntl(text, dictIds, locale, spaceMap) {
  const segmenter = new Intl.Segmenter(locale, { granularity: "word" });
  const segments = segmenter.segment(text);
  let html = "";
  let charIndex = 0; // 追踪在cleanText中的位置

  for (const { segment, isWordLike } of segments) {
    if (!isWordLike) {
      // 非词部分（标点等），检查每个字符后是否有被移除的空格
      for (let i = 0; i < segment.length; i++) {
        html += segment[i];
        const pos = charIndex + i;
        if (spaceMap.has(pos)) {
          html += spaceMap.get(pos);
        }
      }
      charIndex += segment.length;
      continue;
    }

    // 查词典获取词性
    const result = await lookupWord(segment, dictIds);

    // 构建带空格恢复的词内容
    let wordContent = "";
    for (let i = 0; i < segment.length; i++) {
      wordContent += segment[i];
      const pos = charIndex + i;
      if (spaceMap.has(pos)) {
        wordContent += spaceMap.get(pos);
      }
    }

    if (result) {
      const normalizedPos = normalizePos(result.pos);
      if (
        shouldHighlightPos(result.dictId, normalizedPos) &&
        normalizedPos !== "other"
      ) {
        html += `<span class="adhd-${normalizedPos}">${wordContent}</span>`;
      } else {
        html += wordContent;
      }
    } else {
      html += wordContent;
    }

    charIndex += segment.length;
  }
  return html;
}

// 双向最大匹配算法（方案2 - 回退方案）
async function forwardMaxMatch(text, dictIds) {
  const result = [];
  let i = 0;
  while (i < text.length) {
    const char = text[i];
    if (/[\s\p{P}]/u.test(char)) {
      result.push({ word: char, pos: null });
      i++;
      continue;
    }

    let matched = false;
    for (let len = Math.min(8, text.length - i); len >= 1; len--) {
      const word = text.substr(i, len);
      const lookup = await lookupWord(word, dictIds);
      if (lookup) {
        result.push({ word, pos: lookup.pos, dictId: lookup.dictId });
        i += len;
        matched = true;
        break;
      }
    }
    if (!matched) {
      result.push({ word: char, pos: null });
      i++;
    }
  }
  return result;
}

async function backwardMaxMatch(text, dictIds) {
  const result = [];
  let i = text.length;
  while (i > 0) {
    const char = text[i - 1];
    if (/[\s\p{P}]/u.test(char)) {
      result.unshift({ word: char, pos: null });
      i--;
      continue;
    }

    let matched = false;
    for (let len = Math.min(8, i); len >= 1; len--) {
      const word = text.substr(i - len, len);
      const lookup = await lookupWord(word, dictIds);
      if (lookup) {
        result.unshift({ word, pos: lookup.pos, dictId: lookup.dictId });
        i -= len;
        matched = true;
        break;
      }
    }
    if (!matched) {
      result.unshift({ word: char, pos: null });
      i--;
    }
  }
  return result;
}

// 比较两个分词结果，选择更优的
function compareSeg(forward, backward) {
  // 规则1：词数少的优先
  const fWords = forward.filter((s) => !/[\s\p{P}]/u.test(s.word)).length;
  const bWords = backward.filter((s) => !/[\s\p{P}]/u.test(s.word)).length;
  if (fWords !== bWords) return fWords < bWords ? forward : backward;

  // 规则2：单字少的优先
  const fSingle = forward.filter(
    (s) => s.word.length === 1 && !/[\s\p{P}]/u.test(s.word)
  ).length;
  const bSingle = backward.filter(
    (s) => s.word.length === 1 && !/[\s\p{P}]/u.test(s.word)
  ).length;
  if (fSingle !== bSingle) return fSingle < bSingle ? forward : backward;

  // 规则3：有词性标注的词多的优先
  const fPos = forward.filter((s) => s.pos !== null).length;
  const bPos = backward.filter((s) => s.pos !== null).length;
  return fPos >= bPos ? forward : backward;
}

// 双向最大匹配分词（方案2）
async function bidirectionalMaxMatch(text, dictIds) {
  const forward = await forwardMaxMatch(text, dictIds);
  const backward = await backwardMaxMatch(text, dictIds);
  return compareSeg(forward, backward);
}

// 将分词结果转换为HTML，支持恢复原始空格
// sparseRatio: 稀疏化比例，0.5表示随机保留50%的高亮
function segResultToHtml(segments, spaceMap, sparseRatio = 0.5) {
  let html = "";
  let charIndex = 0;

  for (const seg of segments) {
    // 构建带空格恢复的词内容
    let wordContent = "";
    for (let i = 0; i < seg.word.length; i++) {
      wordContent += seg.word[i];
      const pos = charIndex + i;
      if (spaceMap && spaceMap.has(pos)) {
        wordContent += spaceMap.get(pos);
      }
    }

    if (seg.pos) {
      const normalizedPos = normalizePos(seg.pos);
      // 随机稀疏化：只有一定比例的词会被高亮
      const shouldHighlight = Math.random() < sparseRatio;
      if (
        shouldHighlight &&
        shouldHighlightPos(seg.dictId, normalizedPos) &&
        normalizedPos !== "other"
      ) {
        html += `<span class="adhd-${normalizedPos}">${wordContent}</span>`;
      } else {
        html += wordContent;
      }
    } else {
      html += wordContent;
    }

    charIndex += seg.word.length;
  }
  return html;
}

// 主分词函数：使用双向最大匹配（基于词典分词，效果更好）
async function segmentCJKText(text, dictIds) {
  // 打印分词方式日志（只打印一次）
  logSegmenterType();

  // 预处理：移除CJK字符之间的空格，并记录原始空格位置
  const { cleanText, spaceMap } = preprocessCJKText(text);

  // 使用双向最大匹配（基于词典，效果更好）
  const segments = await bidirectionalMaxMatch(cleanText, dictIds);
  return segResultToHtml(segments, spaceMap);
}

async function segmentSpaceBasedText(text, dictIds) {
  const words = text.split(/(\s+|[.,!?;:()"\[\]{}])/);
  let html = "";

  for (const word of words) {
    const cleanWord = word.toLowerCase().replace(/[^\w]/g, "");
    if (!cleanWord) {
      html += word;
      continue;
    }

    let result = await lookupWord(cleanWord, dictIds);
    if (!result && /^[a-zA-Z]+$/.test(cleanWord)) {
      // Simplified check
      if (word.endsWith("s"))
        result = await lookupWord(word.slice(0, -1), dictIds);
    }

    if (result) {
      const normalizedPos = normalizePos(result.pos);
      if (
        shouldHighlightPos(result.dictId, normalizedPos) &&
        normalizedPos !== "other"
      ) {
        html += `<span class="adhd-${normalizedPos}">${word}</span>`;
      } else {
        html += word;
      }
    } else {
      html += word;
    }
  }
  return html;
}

async function processTextNode(textNode) {
  const text = textNode.textContent;
  if (!text.trim()) return;

  // 检查处理模式
  if (settings.processingMode === "llm") {
    await processTextNodeWithLLM(textNode);
    return;
  }

  // 原有的词典模式
  const language = detectLanguage(text);
  const dictIds = getEnabledDictsForLanguage(language);
  if (dictIds.length === 0) return;

  let html;
  if (language === "zh" || language === "ja") {
    html = await segmentCJKText(text, dictIds);
  } else {
    html = await segmentSpaceBasedText(text, dictIds);
  }

  if (!html.includes('class="adhd-')) return;

  const wrapper = document.createElement("span");
  wrapper.innerHTML = html;
  wrapper.className = "adhd-processed";
  textNode.parentNode.replaceChild(wrapper, textNode);
}

// ===================== LLM 处理相关函数 =====================

// LLM API 单次调用（处理单个文本片段）
async function callLLMApiSingle(text, keywordCount) {
  let { endpoint, apiKey, model } = settings.llmSettings;

  // 智能修正 Endpoint (常见错误处理)
  // 如果用户只填了 Base URL (如 .../v1)，自动补全 /chat/completions
  if (endpoint) {
    // 移除末尾的斜杠
    if (endpoint.endsWith("/")) endpoint = endpoint.slice(0, -1);

    if (endpoint.endsWith("/v1")) {
      endpoint += "/chat/completions";
      console.log(
        `EasyReaderADHD [LLM] 检测到BaseURL，自动修正为: ${endpoint}`
      );
    } else if (
      endpoint.includes("dashscope.aliyuncs.com") &&
      !endpoint.includes("/chat/completions")
    ) {
      endpoint += "/chat/completions";
      console.log(
        `EasyReaderADHD [LLM] 检测到阿里云地址，自动修正为: ${endpoint}`
      );
    }
  }

  const prompt = `你是一个专业的ADHD阅读辅助助手。请分析提供的文本，提取能帮助理解句子结构和核心信息的关键词（只限名词n、动词v、形容词a）。

严格遵守以下输出规则（非常重要）：
1. 返回格式必须是合法的标准JSON对象。
2. JSON格式示例：{"苹果": "n", "奔跑": "v", "快速": "a"}
3. 严禁使用Markdown代码块（不要使用 \`\`\`json ），直接返回JSON字符串。
4. 严禁包含任何JSON之外的文字、前缀或后缀。
5. 提取数量【必须严格小于等于】 ${keywordCount} 个。如果超过，只保留最重要的前 ${keywordCount} 个。
6. 禁止提取以下标点符号或纯数字作为关键词：， 。 、 ！ ？ “ ” ‘ ’ （ ） [ ] 【 】 — … 0-9

待分析文本：
${text}`;

  console.log(
    `EasyReaderADHD [LLM] 发送请求: "${text.slice(0, 60)}${
      text.length > 60 ? "..." : ""
    }" (${text.length}字符, 期望${keywordCount}个词)`
  );

  // Send request via Background Script to bypass CORS
  const response = await new Promise((resolve) => {
    chrome.runtime.sendMessage(
      {
        action: "callLLM",
        endpoint,
        apiKey,
        body: {
          model: model || "gpt-3.5-turbo",
          messages: [{ role: "user", content: prompt }],
          temperature: 0.1,
          max_tokens: 800, // 固定较大值，避免截断
          thinking: { type: "disabled" }, // 禁用思考过程，确保直接返回内容
        },
      },
      (res) => {
        if (chrome.runtime.lastError) {
          console.error(
            "EasyReaderADHD [LLM] Runtime Message Error:",
            chrome.runtime.lastError
          );
          resolve({ success: false, error: chrome.runtime.lastError.message });
        } else {
          resolve(res);
        }
      }
    );
  });

  if (!response) {
    console.error(
      "EasyReaderADHD [LLM]Background script returned no response. Please RELOAD the extension."
    );
    return null;
  }

  if (!response.success) {
    console.error(
      `EasyReaderADHD [LLM] API错误: Status=${response.status}, Error="${response.error}"`
    );
    console.log("EasyReaderADHD [LLM] Background Response:", response);
    return null;
  }

  const data = response.data;

  // 打印完整响应结构以供调试
  console.log("EasyReaderADHD [LLM] 完整API响应:", data);

  const content = data.choices?.[0]?.message?.content;

  if (!content) {
    console.warn("EasyReaderADHD [LLM] 响应内容为空");
    return null;
  }

  console.log(`EasyReaderADHD [LLM] 原始响应: "${content}"`);

  // 尝试解析JSON
  try {
    let jsonStr = content;

    // 去除 markdown 代码块标记 ```json ... ```
    jsonStr = jsonStr.replace(/```json\s*/gi, "").replace(/```\s*/g, "");

    // 提取 JSON 对象
    const jsonMatch = jsonStr.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      jsonStr = jsonMatch[0];
    }

    // 尝试修复不完整的JSON（被截断的情况）
    if (!jsonStr.endsWith("}")) {
      console.log("EasyReaderADHD [LLM] JSON不完整，尝试修复:", jsonStr);
      // 删除最后一个不完整的键值对
      jsonStr = jsonStr.replace(/,?\s*"[^"]*"?\s*:?\s*"?[^"]*$/, "") + "}";
    }

    const parsed = JSON.parse(jsonStr);
    console.log(`EasyReaderADHD [LLM] 解析成功:`, parsed);
    return parsed;
  } catch (e) {
    console.warn(
      `EasyReaderADHD [LLM] JSON解析失败: ${e.message}, 原始内容: "${content}"`
    );
    return null;
  }
}

// LLM API 调用（支持长文本分段处理）
async function callLLMApi(text) {
  const { endpoint, apiKey, model } = settings.llmSettings;

  if (!endpoint || !apiKey) {
    console.warn("EasyReaderADHD: LLM endpoint or API key not configured");
    return null;
  }

  const CHUNK_SIZE = 800; // 每段最多800字符
  const chunks = [];

  // 分段：尽量在句号、问号、感叹号处分割
  let remaining = text;
  while (remaining.length > 0) {
    if (remaining.length <= CHUNK_SIZE) {
      chunks.push(remaining);
      break;
    }

    // 在 CHUNK_SIZE 范围内找最后一个句子结束符
    let splitPos = -1;
    for (
      let i = Math.min(CHUNK_SIZE, remaining.length) - 1;
      i >= CHUNK_SIZE * 0.5;
      i--
    ) {
      if (/[。！？.!?]/.test(remaining[i])) {
        splitPos = i + 1;
        break;
      }
    }

    // 如果找不到句子结束符，就在逗号或顿号处分割
    if (splitPos === -1) {
      for (
        let i = Math.min(CHUNK_SIZE, remaining.length) - 1;
        i >= CHUNK_SIZE * 0.5;
        i--
      ) {
        if (/[，、,]/.test(remaining[i])) {
          splitPos = i + 1;
          break;
        }
      }
    }

    // 如果还是找不到，强制在 CHUNK_SIZE 处分割
    if (splitPos === -1) {
      splitPos = CHUNK_SIZE;
    }

    chunks.push(remaining.slice(0, splitPos));
    remaining = remaining.slice(splitPos);
  }

  console.log(
    `EasyReaderADHD [LLM] 请求: 文本长度=${text.length}, 分成${
      chunks.length
    }段, 模型=${model || "gpt-3.5-turbo"}`
  );

  // 处理每个分段，合并结果
  const allKeywords = {};

  for (let i = 0; i < chunks.length; i++) {
    const chunk = chunks[i];
    // 每段提取的关键词上限：每20字1个词，最少8个，最多30个
    const keywordCount = Math.min(
      30,
      Math.max(8, Math.floor(chunk.length / 20))
    );

    console.log(
      `EasyReaderADHD [LLM] 处理第${i + 1}/${chunks.length}段 (${
        chunk.length
      }字符, 提取${keywordCount}个关键词)`
    );

    const result = await callLLMApiSingle(chunk, keywordCount);
    if (result) {
      Object.assign(allKeywords, result);
    }
  }

  const totalCount = Object.keys(allKeywords).length;
  console.log(
    `EasyReaderADHD [LLM] 共提取 ${totalCount} 个关键词`,
    allKeywords
  );

  return totalCount > 0 ? allKeywords : null;
}

// LLM 模式处理单个文本节点
async function processTextNodeWithLLM(textNode) {
  const text = textNode.textContent;
  if (!text.trim() || text.length < 30) {
    // 30字符以下的短文本不调用LLM，节省API调用
    return;
  }

  console.log(`EasyReaderADHD [LLM] 处理文本节点: ${text.length}字符`);
  const keywords = await callLLMApi(text);
  if (!keywords || Object.keys(keywords).length === 0) {
    console.log(`EasyReaderADHD [LLM] 未提取到关键词`);
    return;
  }

  // 根据关键词生成高亮HTML
  let html = text;

  // 按词长度降序排序，避免短词替换长词的一部分
  const sortedWords = Object.entries(keywords).sort(
    (a, b) => b[0].length - a[0].length
  );

  // 使用占位符避免重复替换
  const placeholders = new Map();
  let placeholderIndex = 0;

  for (const [word, pos] of sortedWords) {
    const normalizedPos = normalizePos(pos);
    if (normalizedPos === "other") continue;

    // 创建占位符
    const placeholder = `__ADHD_PH_${placeholderIndex}__`;
    placeholderIndex++;

    // 转义正则特殊字符
    const escapedWord = word.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const regex = new RegExp(escapedWord, "g");

    if (regex.test(html)) {
      // 重置lastIndex
      regex.lastIndex = 0;
      html = html.replace(regex, placeholder);
      placeholders.set(
        placeholder,
        `<span class="adhd-${normalizedPos}">${word}</span>`
      );
    }
  }

  // 替换占位符为实际HTML
  for (const [placeholder, spanHtml] of placeholders) {
    html = html.replace(new RegExp(placeholder, "g"), spanHtml);
  }

  if (!html.includes('class="adhd-')) {
    console.log(`EasyReaderADHD [LLM] 无匹配的高亮词汇`);
    return;
  }

  console.log(`EasyReaderADHD [LLM] 高亮完成: ${placeholders.size}个词汇`);

  const wrapper = document.createElement("span");
  wrapper.innerHTML = html;
  wrapper.className = "adhd-processed";
  textNode.parentNode.replaceChild(wrapper, textNode);
}

// LLM 分批处理页面（按段落分批，边处理边显示）
async function processPageWithLLM() {
  if (!settings || !settings.enabled) return;
  if (settings.processingMode !== "llm") return;

  // Apply dynamic styles first
  applyStyles();

  console.log("EasyReaderADHD: 使用大模型模式处理页面...");

  // 获取所有段落级别的元素
  const paragraphs = document.querySelectorAll(
    "p, h1, h2, h3, h4, h5, h6, li, td, th, article, section > div"
  );

  console.log(`EasyReaderADHD [LLM] 找到 ${paragraphs.length} 个段落元素`);
  let processedCount = 0;

  // 分批处理，每批处理一个段落
  for (const paragraph of paragraphs) {
    if (paragraph.closest(".adhd-processed")) continue;
    if (
      ["SCRIPT", "STYLE", "NOSCRIPT", "TEXTAREA", "INPUT"].includes(
        paragraph.tagName
      )
    )
      continue;

    // 获取段落中的文本节点
    const walker = document.createTreeWalker(paragraph, NodeFilter.SHOW_TEXT, {
      acceptNode: (node) => {
        const parent = node.parentElement;
        if (
          !parent ||
          ["script", "style", "noscript", "textarea", "input"].includes(
            parent.tagName.toLowerCase()
          )
        )
          return NodeFilter.FILTER_REJECT;
        if (parent.closest(".adhd-processed")) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      },
    });

    const textNodes = [];
    let node;
    while ((node = walker.nextNode())) textNodes.push(node);

    // 处理这个段落的文本节点
    for (const textNode of textNodes) {
      await processTextNodeWithLLM(textNode);
    }

    if (textNodes.length > 0) {
      processedCount++;
      console.log(
        `EasyReaderADHD [LLM] 进度: ${processedCount}/${paragraphs.length} 段落`
      );
    }
  }

  console.log(
    `EasyReaderADHD [LLM] ✅ 处理完成！共处理 ${processedCount} 个段落`
  );
  setupObserver();
}

async function processPage() {
  if (!settings || !settings.enabled) return;

  // 检查处理模式
  if (settings.processingMode === "llm") {
    await processPageWithLLM();
    return;
  }

  // 原有的词典模式
  // Apply dynamic styles first
  applyStyles();

  // Preload
  const enabledDicts = [];
  Object.keys(settings.dictionaries).forEach((id) => {
    if (settings.dictionaries[id].enabled) enabledDicts.push(id);
  });
  await Promise.all(enabledDicts.map((id) => loadDictionary(id)));

  // Walk
  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode: (node) => {
        const parent = node.parentElement;
        if (
          !parent ||
          ["script", "style", "noscript", "textarea", "input"].includes(
            parent.tagName.toLowerCase()
          )
        )
          return NodeFilter.FILTER_REJECT;
        if (parent.closest(".adhd-processed")) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      },
    }
  );

  const textNodes = [];
  let node;
  while ((node = walker.nextNode())) textNodes.push(node);

  for (const textNode of textNodes) await processTextNode(textNode);
  console.log("EasyReaderADHD: Page processed");

  // Start observing for dynamically loaded content
  setupObserver();
}

function removeHighlights() {
  document.querySelectorAll(".adhd-processed").forEach((el) => {
    el.outerHTML = el.textContent;
  });
}

// MutationObserver to handle dynamically loaded content
let observer = null;
let pendingNodes = [];
let processingTimeout = null;

function setupObserver() {
  if (observer) return;

  observer = new MutationObserver((mutations) => {
    if (!settings || !settings.enabled) return;

    for (const mutation of mutations) {
      for (const node of mutation.addedNodes) {
        if (
          node.nodeType === Node.ELEMENT_NODE &&
          !node.closest(".adhd-processed")
        ) {
          pendingNodes.push(node);
        }
      }
    }

    // Debounce processing
    if (pendingNodes.length > 0 && !processingTimeout) {
      processingTimeout = setTimeout(() => {
        processNewNodes();
        processingTimeout = null;
      }, 200);
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });
}

async function processNewNodes() {
  if (!settings || !settings.enabled) return;

  const nodesToProcess = [...pendingNodes];
  pendingNodes = [];

  for (const container of nodesToProcess) {
    if (!container.isConnected) continue;
    if (container.closest(".adhd-processed")) continue;

    const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, {
      acceptNode: (node) => {
        const parent = node.parentElement;
        if (
          !parent ||
          ["script", "style", "noscript", "textarea", "input"].includes(
            parent.tagName.toLowerCase()
          )
        )
          return NodeFilter.FILTER_REJECT;
        if (parent.closest(".adhd-processed")) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      },
    });

    const textNodes = [];
    let node;
    while ((node = walker.nextNode())) textNodes.push(node);

    for (const textNode of textNodes) {
      await processTextNode(textNode);
    }
  }
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "settingsUpdated") {
    const oldMode = settings?.processingMode;
    settings = message.settings;

    // 确保 processingMode 和 llmSettings 存在
    if (!settings.processingMode) settings.processingMode = "dictionary";
    if (!settings.llmSettings) {
      settings.llmSettings = {
        endpoint: "",
        apiKey: "",
        model: "gpt-3.5-turbo",
      };
    }

    // Update styles immediately
    applyStyles();

    // If enabled toggled or mode changed, re-process
    if (settings.enabled) {
      // 如果处理模式改变了，需要重新处理
      if (oldMode !== settings.processingMode) {
        removeHighlights();
        processPage();
      } else if (!document.querySelector(".adhd-processed")) {
        processPage();
      }
    } else {
      removeHighlights();
      if (observer) {
        observer.disconnect();
        observer = null;
      }
    }
  }
});

chrome.storage.local.get(["adhdSettings"], (result) => {
  if (result.adhdSettings) {
    settings = result.adhdSettings;
    // 确保 processingMode 和 llmSettings 存在
    if (!settings.processingMode) settings.processingMode = "dictionary";
    if (!settings.llmSettings) {
      settings.llmSettings = {
        endpoint: "",
        apiKey: "",
        model: "gpt-3.5-turbo",
      };
    }
  }
  if (settings && settings.enabled) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => {
        processPage();
        // Re-process after a delay for SPA frameworks
        setTimeout(processPage, 1000);
      });
    } else {
      processPage();
      // Re-process after a delay for SPA frameworks
      setTimeout(processPage, 1000);
    }
  }
});
