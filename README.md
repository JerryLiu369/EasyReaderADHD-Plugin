# EasyReaderADHD

> 为 ADHD 和阅读困难用户设计的 Chrome 阅读辅助扩展

通过智能词性高亮与可调节的高亮密度，帮助在阅读长文时保持专注，减少视觉疲劳。

<!-- TODO: 上线后补充 Chrome Web Store 链接 -->
<!-- [**→ 在 Chrome Web Store 安装**](https://chromewebstore.google.com/detail/xxx) -->

---

## 功能

- **词性高亮**：基于本地词典自动识别名词、动词、形容词，分色高亮
- **高亮密度控制**：0–100% 随机密度，避免满屏色彩造成视觉过载
- **排版定制**：调节字间距、字体大小、字重，多种配色主题可选
- **完全离线**：所有计算在本地完成，无网络请求，不收集任何数据

## 安装

### Chrome Web Store（推荐）

<!-- TODO: 补充链接 -->
在 Chrome Web Store 搜索 **EasyReaderADHD** 并点击安装。

### 开发者模式（本地加载）

```bash
git clone <本仓库地址>
cd EasyReaderADHD-Plugin
npm install
npm run build
```

然后：

1. 打开 `chrome://extensions/`
2. 开启右上角 **开发者模式**
3. 点击 **加载已解压的扩展程序**，选择项目根目录

## 使用

点击浏览器工具栏的插件图标打开设置面板：

| 设置项 | 说明 |
|--------|------|
| 密度滑块 | 控制页面上高亮词汇的比例 |
| 词性开关 | 独立开关名词 / 动词 / 形容词的高亮 |
| 外观主题 | 预设配色方案，或手动调整排版参数 |

## 开发

### 构建命令

| 命令 | 说明 |
|------|------|
| `npm run build` | 单次生产构建，输出至 `dist/` |
| `npm run watch` | 监听模式，源码变更后自动重构建 |

构建完成后，去 `chrome://extensions/` 点击刷新图标重新加载插件。

### 项目结构

```
EasyReaderADHD-Plugin/
├── src/
│   ├── background/     # Service Worker
│   ├── content/        # 页面注入脚本（分词、DOM 操作）
│   ├── popup/          # 设置面板
│   ├── dictionaries/   # 本地词典（JSON）
│   ├── static/         # 图标等静态资源
│   └── styles.css      # 注入页面的样式
├── dist/               # 构建输出
├── esbuild.config.js
└── manifest.json
```

## License

[MIT](LICENSE)
