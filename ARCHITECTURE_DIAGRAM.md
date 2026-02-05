# PDF 扩展架构图 / PDF Extension Architecture Diagram

## 当前架构 / Current Architecture (Web Pages)

```
┌─────────────────────────────────────────────────────────────┐
│                       Web Page                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                HTML DOM Tree                          │  │
│  │  <p>The quick brown fox</p>                          │  │
│  │  <div>跳过懒狗的敏捷棕色狐狸</div>                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              Content Script (src/content/)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. TreeWalker → Collect Text Nodes                   │  │
│  │ 2. Language Detection (CJK/Latin)                    │  │
│  │ 3. Text Segmentation (Forward-Max-Match / Space)     │  │
│  │ 4. Dictionary Lookup (POS tagging)                   │  │
│  │ 5. DOM Replacement (<span class="adhd-n/v/a">)      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   Highlighted Web Page                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  The <span class="adhd-a">quick</span>               │  │
│  │      <span class="adhd-a">brown</span>               │  │
│  │      <span class="adhd-n">fox</span>                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 提议的 PDF 架构 / Proposed PDF Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PDF Document                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        Binary PDF Format (*.pdf)                      │  │
│  │  - Compressed text and graphics                       │  │
│  │  - Precise coordinate positioning                     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              PDF.js Library Integration                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ • Parse PDF binary format                             │  │
│  │ • Extract text content                                │  │
│  │ • Get coordinates (x, y, width, height)              │  │
│  │ • Render PDF pages to Canvas                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│         Text Extraction Result (Per Page)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  [                                                    │  │
│  │    { text: "The quick brown fox",                    │  │
│  │      x: 50, y: 100, width: 120, height: 14 },       │  │
│  │    { text: "jumps over the lazy dog",               │  │
│  │      x: 50, y: 120, width: 140, height: 14 }        │  │
│  │  ]                                                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│      **REUSE** Core Processing Logic (80%)                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Language Detection ✓ (same as web)                │  │
│  │ 2. Text Segmentation ✓ (same algorithms)             │  │
│  │    - segmentCJKText()                                 │  │
│  │    - segmentSpaceBasedText()                         │  │
│  │ 3. Dictionary Lookup ✓ (same dictionaries)          │  │
│  │ 4. POS Filtering ✓ (same logic)                     │  │
│  │ 5. Density Control ✓ (same randomization)           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│       Segmented Text with Coordinates                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  [                                                    │  │
│  │    { text: "The", className: null, x: 50, y: 100 },  │  │
│  │    { text: "quick", className: "adhd-a",             │  │
│  │      x: 70, y: 100 },                                │  │
│  │    { text: "brown", className: "adhd-a",             │  │
│  │      x: 110, y: 100 },                               │  │
│  │    { text: "fox", className: "adhd-n",               │  │
│  │      x: 150, y: 100 }                                │  │
│  │  ]                                                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│         **NEW** Canvas/SVG Highlight Renderer               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ • Calculate precise character widths                  │  │
│  │ • Draw colored rectangles at coordinates             │  │
│  │ • Layer over PDF canvas                              │  │
│  │ • Handle multi-page rendering                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              Final PDF with Highlights                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ PDF Canvas Layer (bottom)                      │  │  │
│  │  │ - Original PDF content                         │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ Highlight Canvas Layer (top)                   │  │  │
│  │  │ The [quick] [brown] [fox]                      │  │  │
│  │  │     adj     adj     noun                       │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 代码复用对比 / Code Reusability Comparison

### ✅ 100% 可复用 / 100% Reusable

```javascript
// src/shared/language.js
export function detectLanguage(text) { ... }  // ✓ Works for both web and PDF

// src/content/segmentation.js
export async function segmentCJKText(text, dictIds, settings) { ... }  // ✓ Platform-agnostic
export async function segmentSpaceBasedText(text, dictIds, settings) { ... }  // ✓ Platform-agnostic

// src/content/dictionary.js
export async function loadDictionaries(dictIds) { ... }  // ✓ Same dictionary system
export function getWordSet(dictIds) { ... }  // ✓ Same lookup logic

// src/content/settings.js
export async function loadSettings() { ... }  // ✓ Same settings management

// src/popup/ (entire folder)
// ✓ Same UI, no changes needed
```

### 🔄 需要适配 / Needs Adaptation

```javascript
// src/content/dom.js → src/pdf-viewer/text-extractor.js
- TreeWalker DOM traversal  →  + PDF.js text extraction
- MutationObserver          →  + Page navigation events

// src/content/dom.js → src/pdf-viewer/renderer.js
- document.createElement('span')  →  + Canvas fillRect() / SVG rect
- textNode.replaceChild()         →  + Coordinate-based overlay
```

### ➕ 新增模块 / New Modules

```javascript
// src/pdf-viewer/index.js (new)
// - Initialize PDF.js
// - Handle PDF loading
// - Coordinate rendering flow

// src/pdf-viewer/text-extractor.js (new)
// - Extract text with PDF.js
// - Get text item coordinates
// - Handle multi-page extraction

// src/pdf-viewer/renderer.js (new)
// - Canvas/SVG highlight rendering
// - Coordinate calculation
// - Multi-page state management

// src/pdf-viewer/pdf-viewer.html (new)
// - Custom PDF viewer page
// - Replaces Chrome default viewer
```

---

## 性能优化策略 / Performance Optimization Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                Large PDF (100+ pages)                       │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              Strategy 1: Paginated Loading                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Only load: [Current Page] + [±2 Pages]              │  │
│  │  - Page 48: Unloaded                                  │  │
│  │  - Page 49: Loaded                                    │  │
│  │  - Page 50: Current ← User viewing                   │  │
│  │  - Page 51: Loaded                                    │  │
│  │  - Page 52: Unloaded                                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              Strategy 2: Web Worker Threading                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Main Thread          Web Worker Thread              │  │
│  │  ┌────────────┐       ┌────────────────────┐        │  │
│  │  │ UI Render  │◄──────┤ Text Segmentation  │        │  │
│  │  │ User Input │       │ Dictionary Lookup  │        │  │
│  │  └────────────┘──────►│ POS Filtering      │        │  │
│  │                        └────────────────────┘        │  │
│  │  No blocking!         CPU-intensive work             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              Strategy 3: Result Caching                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Memory Cache                                         │  │
│  │  {                                                    │  │
│  │    page50: [highlighted segments],  // ✓ Cached     │  │
│  │    page51: [highlighted segments],  // ✓ Cached     │  │
│  │    page52: null                     // Not visited   │  │
│  │  }                                                    │  │
│  │  → Instant redraw when revisiting pages              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 开发时间线 / Development Timeline

```
Week 1-2: Prototype Validation
├── Install PDF.js
├── Extract text from sample PDF
├── Verify segmentation works
└── Basic Canvas highlighting

Week 3-5: Core Implementation
├── Complete coordinate system
├── Multi-page rendering
├── POS highlighting
└── Density control

Week 6-7: Performance Optimization
├── Paginated loading
├── Web Worker
├── Caching
└── Large PDF testing

Week 8: Polish & UX
├── UI refinement
├── Settings integration
├── Error handling
└── Documentation

Week 9: Testing & Release
├── Cross-browser testing
├── Edge case testing
├── Performance benchmarks
└── Chrome Web Store release
```

---

**创建时间 Created**: 2026-02-05  
**版本 Version**: 1.0
