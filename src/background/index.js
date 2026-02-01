/**
 * Background Service Worker
 * 轻量级后台脚本，主要用于管理生命周期
 */

chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === "install") {
    chrome.tabs.create({ url: chrome.runtime.getURL("popup.html") });
  }
});

// 保持 service worker 活跃（可选）
// setInterval(() => {}, 25000);
