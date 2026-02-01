/**
 * 样式管理模块
 */

import { DEFAULT_COLORS, DEFAULT_APPEARANCE } from "../shared/constants.js";
import { darkenColor } from "../shared/colors.js";
import { logger } from "../shared/logger.js";

// Hex to RGBA 转换
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

let styleElement = null;

export function applyStyles(settings) {
  if (!settings) {
    logger.warn("applyStyles: settings 未初始化");
    return;
  }

  const app = settings.appearance || DEFAULT_APPEARANCE;
  const colors = app.colors || DEFAULT_COLORS;

  // 字重转换为 text-stroke (原版实现)
  const strokeWidth =
    (app.weight || 400) > 400 ? (((app.weight || 400) - 400) / 500) * 0.5 : 0;
  const weightStyle =
    strokeWidth > 0
      ? `-webkit-text-stroke: ${strokeWidth}px currentColor;`
      : "";
  const scaleStyle =
    (app.scale || 100) > 100 ? `font-size: ${(app.scale || 100) / 100}em;` : "";

  const css = `
.adhd-processed span {
  display: inline;
  border-radius: 3px;
  transition: background-color 0.2s;
  color: inherit !important;
  ${scaleStyle}
  ${weightStyle}
  ${(app.spacing || 0) > 0 ? `padding: 0 ${app.spacing}px; margin: 0 ${app.spacing / 2}px;` : ""}
  ${app.underline ? "border-bottom: 2px solid currentColor;" : ""}
}

.adhd-n { background-color: ${hexToRgba(colors.noun, 0.25)}; }
.adhd-v { background-color: ${hexToRgba(colors.verb, 0.25)}; }
.adhd-a, .adhd-adj { background-color: ${hexToRgba(colors.adj, 0.25)}; }
.adhd-adv { background-color: ${hexToRgba(colors.adj, 0.25)}; }
.adhd-other { background-color: ${hexToRgba(colors.other, 0.25)}; }
`;

  if (!styleElement) {
    styleElement = document.createElement("style");
    styleElement.id = "adhd-styles";
    document.head.appendChild(styleElement);
  }
  styleElement.textContent = css;
  logger.debug("样式已应用");
}

export function removeStyles() {
  if (styleElement) {
    styleElement.remove();
    styleElement = null;
  }
}
