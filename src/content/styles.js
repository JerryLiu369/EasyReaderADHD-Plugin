/**
 * 样式管理模块
 */

import { DEFAULT_COLORS, DEFAULT_APPEARANCE } from "../shared/constants.js";
import { darkenColor } from "../shared/colors.js";
import { logger } from "../shared/logger.js";

let styleElement = null;

export function applyStyles(settings) {
  if (!settings) {
    logger.warn("applyStyles: settings 未初始化");
    return;
  }

  const app = settings.appearance || DEFAULT_APPEARANCE;
  const colors = app.colors || DEFAULT_COLORS;

  const css = `
.adhd-noun { color: ${colors.noun}; font-weight: ${(app.weight || 400) + 100}; }
.adhd-verb { color: ${colors.verb}; font-weight: ${(app.weight || 400) + 100}; }
.adhd-adj { color: ${colors.adj}; font-weight: ${(app.weight || 400) + 100}; }
.adhd-other { color: ${colors.other}; font-weight: ${(app.weight || 400) + 100}; }

.adhd-noun, .adhd-verb, .adhd-adj, .adhd-other {
  ${app.underline ? "text-decoration: underline;" : ""}
  transition: all 0.15s ease;
  cursor: default;
}

.adhd-noun:hover, .adhd-verb:hover, .adhd-adj:hover, .adhd-other:hover {
  background-color: rgba(0, 0, 0, 0.05);
  border-radius: 2px;
}

.adhd-processed {
  font-size: ${app.scale || 100}%;
  letter-spacing: ${app.spacing || 0}px;
  line-height: 1.6;
}

@media (prefers-color-scheme: dark) {
  .adhd-noun { text-shadow: 0 0 1px ${darkenColor(colors.noun, 30)}; }
  .adhd-verb { text-shadow: 0 0 1px ${darkenColor(colors.verb, 30)}; }
  .adhd-adj { text-shadow: 0 0 1px ${darkenColor(colors.adj, 30)}; }
  .adhd-other { text-shadow: 0 0 1px ${darkenColor(colors.other, 30)}; }
}
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
