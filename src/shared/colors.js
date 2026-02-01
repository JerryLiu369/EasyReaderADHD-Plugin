/**
 * 颜色工具
 */

export function hexToRgba(hex, alpha = 1) {
  if (!hex || typeof hex !== "string") return "rgba(0, 0, 0, 0)";

  let r = 0,
    g = 0,
    b = 0;
  const cleanHex = hex.replace("#", "");

  if (cleanHex.length === 3) {
    r = parseInt(cleanHex[0] + cleanHex[0], 16);
    g = parseInt(cleanHex[1] + cleanHex[1], 16);
    b = parseInt(cleanHex[2] + cleanHex[2], 16);
  } else if (cleanHex.length === 6) {
    r = parseInt(cleanHex.substring(0, 2), 16);
    g = parseInt(cleanHex.substring(2, 4), 16);
    b = parseInt(cleanHex.substring(4, 6), 16);
  }

  const a = Math.max(0, Math.min(1, Number(alpha) || 1));
  return `rgba(${r}, ${g}, ${b}, ${a})`;
}

export function darkenColor(hex, percent) {
  if (!hex || typeof hex !== "string") return "rgb(0, 0, 0)";
  if (typeof percent !== "number") percent = 0;

  const cleanHex = hex.replace("#", "");
  if (cleanHex.length !== 6) return "rgb(0, 0, 0)";

  let r = parseInt(cleanHex.substring(0, 2), 16);
  let g = parseInt(cleanHex.substring(2, 4), 16);
  let b = parseInt(cleanHex.substring(4, 6), 16);

  const factor = Math.max(0, Math.min(100, percent)) / 100;
  r = Math.floor(r * (1 - factor));
  g = Math.floor(g * (1 - factor));
  b = Math.floor(b * (1 - factor));

  return `rgb(${r}, ${g}, ${b})`;
}
