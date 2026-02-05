# EasyReaderADHD 插件扩展到 PDF 阅读的可行性分析

## 执行摘要

**结论：可行，但需要中等程度的架构改造**

EasyReaderADHD 可以扩展到支持 PDF 阅读，核心的词典处理和分词算法可以直接复用。主要挑战在于 PDF 渲染层面的技术限制和文本提取机制的差异。

---

## 1. 项目现状分析

### 1.1 核心功能
EasyReaderADHD 是一个为 ADHD 和阅读障碍用户设计的 Chrome 扩展，通过以下方式辅助阅读：

- **智能词性高亮**：基于本地词典识别名词、动词、形容词并用不同颜色标记
- **可调节高亮密度**：0-100% 随机密度，避免视觉过载
- **视觉定制化**：字体大小、粗细、字间距、主题切换
- **多语言支持**：中文、英文、日文、法文、西班牙文、俄文 + 专业领域词典
- **完全离线**：所有处理在本地完成，零数据收集

### 1.2 技术架构

#### 技术栈
- **Chrome Extension Manifest V3**
- **JavaScript (ES6 Modules)**
- **esbuild** 用于模块打包

#### 核心组件

| 组件 | 文件位置 | 作用 |
|------|---------|------|
| **Content Script** | `src/content/` | 注入到网页，执行 DOM 操作和文本高亮 |
| **Service Worker** | `src/background/` | 后台服务，处理扩展生命周期和消息 |
| **Popup UI** | `src/popup/` | 用户设置面板 |
| **词典系统** | `src/dictionaries/` | JSON 格式的词性标注词典 |
| **共享模块** | `src/shared/` | 语言检测、常量定义、日志工具 |

#### 处理流程
```
网页加载 → 语言检测 → 词典加载 → 文本分词 → 词性分类 → DOM 替换 → 动态内容监听
```

### 1.3 关键技术实现

#### a) DOM 文本采集
使用 `TreeWalker` 遍历 DOM 树收集文本节点：
- 跳过 `<script>`, `<style>`, `<code>`, `<textarea>` 等标签
- 跳过已处理的节点 (`.adhd-processed`)
- 批量处理（每批 200 个节点）+ `requestIdleCallback` 优化性能

#### b) 语言检测 (`src/shared/language.js`)
基于字符分布的快速检测：
- CJK 字符占比 > 30% → 识别为中文/日文
- 拉丁字符占比 > 30% → 识别为英文
- 支持混合语言文本

#### c) 分词算法

**CJK 文本** (`segmentCJKText`):
- **前向最大匹配算法 (Forward-Max-Match)**
- 从每个位置尝试匹配最长词（8 字符 → 1 字符递减）
- 使用 Set 数据结构实现 O(1) 查找
- 示例：
  ```
  文本: "中华人民共和国"
  匹配: ["中华人民", "共和国"] 而非 ["中", "华", "人", "民"...]
  ```

**空格分隔文本** (`segmentSpaceBasedText`):
- 按空格和标点符号分割
- 词形还原（去除复数 -s、过去式 -ed、进行时 -ing）
- 回退查找策略提高命中率

#### d) 高亮渲染
将匹配的词用 `<span>` 包裹：
```html
原文: The quick brown fox
处理后: The <span class="adhd-a">quick</span> <span class="adhd-a">brown</span> <span class="adhd-n">fox</span>
```

#### e) 动态内容监听
使用 `MutationObserver` 监听 DOM 变化：
- 500ms 防抖避免频繁触发
- 800ms 稳定延迟确保内容加载完成
- 自动处理新增的文本节点

---

## 2. PDF 阅读扩展的可行性分析

### 2.1 为什么需要特殊处理？

#### 当前限制
1. **Content Script 无法访问 PDF 内容**
   - Chrome 内置 PDF 阅读器使用 `<embed>` 标签渲染
   - PDF 内容不是真正的 DOM 文本节点
   - 跨域隔离（`chrome-extension://` vs `file://` 协议）

2. **PDF 没有可操作的 DOM 树**
   - PDF 是二进制格式，不是 HTML
   - 文本是绘制的图形，不是文本节点
   - 无法直接使用 `TreeWalker` 和 `MutationObserver`

3. **布局复杂性**
   - PDF 有精确的坐标定位
   - 多栏排版、表格、图文混排
   - 需要保持原始布局

### 2.2 技术可行性评估

#### ✅ **可复用的核心逻辑**（约 80% 代码可保留）

| 模块 | 可复用性 | 说明 |
|------|---------|------|
| 词典系统 | 100% | 词典加载、查询、缓存完全可用 |
| 分词算法 | 100% | `segmentCJKText`, `segmentSpaceBasedText` 无需修改 |
| 语言检测 | 100% | 字符分析逻辑通用 |
| 词性过滤 | 100% | 名词/动词/形容词筛选逻辑不变 |
| 密度控制 | 100% | 随机密度算法不变 |
| 设置系统 | 100% | Popup UI 和 storage 逻辑不变 |
| 样式系统 | 80% | 需要调整为 Canvas/SVG 渲染 |

#### 🔄 **需要改造的部分**（约 20% 新增代码）

| 改造项 | 复杂度 | 工作量估算 |
|--------|--------|-----------|
| PDF 解析和文本提取 | 中 | 3-5 天 |
| 高亮层渲染（Canvas/SVG） | 中 | 4-6 天 |
| 坐标映射和布局计算 | 高 | 5-7 天 |
| 多页面状态管理 | 低 | 2-3 天 |
| 性能优化（大型 PDF） | 中 | 3-4 天 |
| **总计** | **中等** | **17-25 天** |

---

## 3. 技术实现方案

### 3.1 架构设计

#### 方案 A：PDF.js 集成（推荐）

**PDF.js** 是 Mozilla 开发的开源 PDF 渲染库，Chrome 内置 PDF 阅读器基于它。

**优势**：
- ✅ 成熟稳定，广泛使用
- ✅ 提供完整的文本提取 API
- ✅ 支持坐标信息（文本块位置）
- ✅ MIT 许可证，可商用

**实现步骤**：
```
1. 集成 PDF.js 库
2. 创建自定义 PDF 渲染页面（替代 Chrome 默认阅读器）
3. 提取文本 + 坐标信息
4. 应用分词和高亮算法
5. 在 Canvas/SVG 层叠加高亮
```

#### 方案 B：Chrome PDF Viewer API（未来）

Chrome 正在开发 PDF Viewer API，但目前仍处于实验阶段，不推荐使用。

---

### 3.2 详细技术方案

#### 步骤 1：检测 PDF 文件
```javascript
// 在 background.js 监听 PDF 打开
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.url && changeInfo.url.endsWith('.pdf')) {
    // 重定向到自定义 PDF 阅读器
    chrome.tabs.update(tabId, {
      url: chrome.runtime.getURL(`pdf-viewer.html?file=${encodeURIComponent(changeInfo.url)}`)
    });
  }
});
```

#### 步骤 2：使用 PDF.js 提取文本
```javascript
// pdf-viewer.html 中
import * as pdfjsLib from 'pdfjs-dist';

async function extractTextWithCoordinates(pdfDocument, pageNumber) {
  const page = await pdfDocument.getPage(pageNumber);
  const textContent = await page.getTextContent();
  
  const textItems = textContent.items.map(item => ({
    text: item.str,
    x: item.transform[4],
    y: item.transform[5],
    width: item.width,
    height: item.height
  }));
  
  return textItems;
}
```

#### 步骤 3：应用现有分词和高亮逻辑
```javascript
// 复用现有代码
import { segmentCJKText, segmentSpaceBasedText } from '../content/segmentation.js';
import { detectLanguage } from '../shared/language.js';

async function highlightPDFText(textItems, settings) {
  for (const item of textItems) {
    const language = detectLanguage(item.text);
    const segments = language === 'zh' || language === 'ja'
      ? await segmentCJKText(item.text, dictIds, settings)
      : await segmentSpaceBasedText(item.text, dictIds, settings);
    
    // 为每个 segment 计算坐标并渲染高亮
    renderHighlightOverlay(segments, item.x, item.y);
  }
}
```

#### 步骤 4：Canvas 高亮渲染
```javascript
function renderHighlightOverlay(segments, baseX, baseY) {
  const canvas = document.getElementById('highlight-layer');
  const ctx = canvas.getContext('2d');
  
  let offsetX = baseX;
  segments.forEach(segment => {
    if (segment.className) {
      // 根据词性设置颜色
      ctx.fillStyle = getColorForClass(segment.className);
      ctx.fillRect(offsetX, baseY, measureTextWidth(segment.text), lineHeight);
    }
    offsetX += measureTextWidth(segment.text);
  });
}
```

---

### 3.3 文件结构调整

```
src/
├── content/              # 网页模式（现有）
│   ├── index.js
│   ├── dom.js
│   ├── segmentation.js   # 核心分词逻辑（共享）
│   └── dictionary.js     # 词典系统（共享）
├── pdf-viewer/           # PDF 模式（新增）
│   ├── index.js          # PDF 阅读器入口
│   ├── text-extractor.js # 文本提取（基于 PDF.js）
│   ├── renderer.js       # Canvas/SVG 高亮渲染
│   └── pdf-viewer.html   # 自定义 PDF 阅读器页面
├── shared/               # 共享模块（现有 + 扩展）
│   ├── language.js       # 语言检测（共享）
│   ├── constants.js
│   └── logger.js
├── popup/                # 设置面板（现有，微调）
└── dictionaries/         # 词典（完全共享）
```

---

## 4. 主要技术挑战

### 4.1 挑战 1：文本坐标精确映射

**问题**：
- PDF 文本有精确的 x, y 坐标
- 分词后需要计算每个子词的坐标
- 不同字体、字号的字符宽度不同

**解决方案**：
```javascript
// 使用 Canvas measureText API
function calculateSegmentCoordinates(segment, baseX, baseY, font) {
  const ctx = document.createElement('canvas').getContext('2d');
  ctx.font = font;
  const width = ctx.measureText(segment.text).width;
  return { x: baseX, y: baseY, width, height: fontSize };
}
```

### 4.2 挑战 2：性能优化（大型 PDF）

**问题**：
- 上百页 PDF 处理时间长
- 内存占用大

**解决方案**：
- **分页加载**：只处理可见页 + 前后各 2 页
- **虚拟滚动**：动态渲染可见区域
- **Web Worker**：在后台线程处理分词
- **缓存**：已处理页面的高亮结果缓存到内存

```javascript
// 使用 Web Worker 处理分词
const worker = new Worker('segmentation-worker.js');
worker.postMessage({ text, dictIds, settings });
worker.onmessage = (e) => {
  const segments = e.data;
  renderHighlights(segments);
};
```

### 4.3 挑战 3：复杂布局处理

**问题**：
- 多栏排版
- 表格
- 图文混排
- 旋转文本

**解决方案**：
- 使用 PDF.js 的 `textContent.items` 顺序（已按阅读顺序排列）
- 检测文本块边界（x, y 差异阈值）
- 跳过非文本区域（图片、表格边框）

### 4.4 挑战 4：用户体验一致性

**问题**：
- 网页模式和 PDF 模式的交互一致性
- 设置同步
- 样式表现差异

**解决方案**：
- 统一设置面板（同一个 Popup）
- 共享配色方案和密度控制
- Canvas 渲染模拟 HTML 的视觉效果

---

## 5. 实施路线图

### 阶段 1：原型验证（1-2 周）
- [ ] 集成 PDF.js 库
- [ ] 实现基础文本提取
- [ ] 复用分词算法验证可行性
- [ ] Canvas 简单高亮渲染

### 阶段 2：核心功能（2-3 周）
- [ ] 完整的坐标计算系统
- [ ] 多页面状态管理
- [ ] 词性高亮完整实现
- [ ] 密度控制集成

### 阶段 3：性能优化（1-2 周）
- [ ] 分页加载
- [ ] Web Worker 多线程
- [ ] 缓存策略
- [ ] 大型 PDF 压力测试

### 阶段 4：用户体验（1 周）
- [ ] UI/UX 适配
- [ ] 设置面板调整
- [ ] 错误处理
- [ ] 用户文档

### 阶段 5：测试与发布（1 周）
- [ ] 跨浏览器测试
- [ ] 边缘案例测试
- [ ] 性能基准测试
- [ ] 发布到 Chrome Web Store

**总工期估算**：6-9 周（1.5-2.5 个月）

---

## 6. 风险评估

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| PDF.js 集成复杂度高于预期 | 高 | 中 | 提前技术验证，参考官方示例 |
| 性能问题（大型 PDF） | 中 | 高 | 分页加载、Web Worker、虚拟滚动 |
| 坐标计算精度问题 | 中 | 中 | Canvas measureText 精确测量 |
| Chrome 扩展权限限制 | 高 | 低 | 使用自定义 PDF 阅读器页面 |
| 用户接受度（替换默认阅读器） | 中 | 中 | 提供开关选项，保留原生阅读器 |

---

## 7. 成本效益分析

### 开发成本
- **人力**：1 名全职开发者 2-3 个月
- **技术栈**：无新增第三方依赖成本（PDF.js 开源）
- **测试**：1 名测试人员 1 周

### 收益
- **用户群扩展**：支持 PDF 可吸引学术、办公用户
- **竞争优势**：市面上少有针对 ADHD 的 PDF 阅读辅助工具
- **品牌价值**：完善的产品功能提升用户满意度

---

## 8. 替代方案对比

### 方案对比表

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **PDF.js 集成** | 完全控制、功能完整、开源 | 开发量较大 | ⭐⭐⭐⭐⭐ |
| **Chrome PDF Viewer API** | 原生集成 | 实验性 API，不稳定 | ⭐⭐ |
| **转换 PDF 为 HTML** | 复用现有代码 | 布局失真、性能差 | ⭐ |
| **OCR + 文本识别** | 支持图片 PDF | 精度低、速度慢 | ⭐ |

---

## 9. 最终建议

### 结论
**强烈建议实施 PDF 扩展功能**，理由如下：

1. ✅ **技术可行**：核心算法 80% 可复用，风险可控
2. ✅ **市场需求**：学术阅读、办公场景大量使用 PDF
3. ✅ **竞争优势**：市场空白，差异化竞争
4. ✅ **成本合理**：2-3 个月开发周期，无外部依赖成本

### 优先级
- **P0（必须）**：基础 PDF 文本提取和高亮
- **P1（重要）**：性能优化（分页加载）
- **P2（可选）**：复杂布局支持（表格、多栏）
- **P3（未来）**：OCR 支持扫描 PDF

### 下一步行动
1. **技术验证（1 周）**：搭建 PDF.js 最小原型，验证文本提取和高亮
2. **需求调研（1 周）**：调查用户对 PDF 功能的具体需求
3. **资源规划（1 周）**：确定开发团队和时间表
4. **正式开发（6-8 周）**：按路线图分阶段实施

---

## 10. 附录：技术参考

### 相关库和工具
- **PDF.js**: https://mozilla.github.io/pdf.js/
- **Chrome Extension API**: https://developer.chrome.com/docs/extensions/
- **Canvas API**: https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API

### 参考项目
- Hypothesis PDF 标注工具
- Liner Web & PDF Highlighter
- Kami PDF 协作工具

### 学习资源
- PDF.js Getting Started: https://github.com/mozilla/pdf.js/wiki/Frequently-Asked-Questions
- Building a PDF Viewer with PDF.js: https://pspdfkit.com/blog/2018/render-pdfs-in-the-browser-with-pdf-js/

---

**文档版本**：1.0  
**创建日期**：2026-02-05  
**作者**：EasyReaderADHD 开发团队  
**状态**：待审批
