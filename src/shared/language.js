/**
 * 语言检测
 */

export function detectLanguage(text) {
  if (!text || typeof text !== "string") return "unknown";

  const trimmed = text.trim();
  if (trimmed.length === 0) return "unknown";

  // 中文字符 (U+4E00-U+9FA5)
  const chineseCount = (trimmed.match(/[\u4e00-\u9fa5]/g) || []).length;
  // 日文假名 (U+3040-U+309F 平假名，U+30A0-U+30FF 片假名)
  const hiraganaCount = (trimmed.match(/[\u3040-\u309f]/g) || []).length;
  const katakanaCount = (trimmed.match(/[\u30a0-\u30ff]/g) || []).length;
  const japaneseCount = hiraganaCount + katakanaCount;
  // 韩文 (U+AC00-U+D7AF)
  const koreanCount = (trimmed.match(/[\uac00-\ud7af]/g) || []).length;
  // 拉丁字符
  const latinCount = (trimmed.match(/[a-zA-Z]/g) || []).length;
  const totalChars = trimmed.length;

  // 中日韩优先
  const cjkTotal = chineseCount + japaneseCount + koreanCount;
  if (cjkTotal / totalChars > 0.3) {
    // 区分日文和中文
    if (japaneseCount > chineseCount && japaneseCount > 0) return "ja";
    if (koreanCount > chineseCount && koreanCount > 0) return "ko";
    return "zh";
  }

  // 拉丁字符
  if (latinCount / totalChars > 0.3) return "en";

  // 默认英文
  return "en";
}
