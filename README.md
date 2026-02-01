# EasyReaderADHD - 阅读辅助浏览器扩展

![Icon](static/icon-128.png)

> 为 ADHD 和阅读困难用户设计的智能文本高亮阅读辅助工具

[English](#english) | [中文](#中文)

---

## 中文

### 🎯 功能特性

**EasyReaderADHD** 是一款强大的浏览器扩展，帮助 ADHD 患者、阅读困难者和语言学习者改善阅读体验。

#### 核心功能
- 🎨 **语法着色系统** - 自动为不同词性（名词、动词、形容词）着色，提升理解效率
- 🌍 **多语言支持** - 英语、中文、日语、法语、西班牙语、俄语
- 🎭 **丰富的配色方案** - 5 种预设主题（默认、柔和、森林、粉红、高对比）+ 自定义选项
- ⚙️ **精细化调控**
  - 字体大小调整（50%-200%）
  - 字间距控制
  - 字体粗细调整
  - 可选下划线
- 📚 **多字典支持** - 基础字典 + 专业词库（成语、诗词、IT、财经、法律、医学等）
- ✅ **基于词典的词性高亮**

### 💡 适用于
- ADHD 患者的阅读专注力提升
- 阅读困难者的视觉辅助
- 语言学习者的理解加速
- 任何人的无障碍阅读体验

### 🚀 快速开始

1. 在 Chrome 应用商店安装扩展
2. 点击扩展图标打开设置
3. 选择你的偏好语言和配色方案
4. 开始阅读！扩展会自动高亮文本

### ⚙️ 自定义选项

#### 外观设置
- **主题选择** - 预设主题或完全自定义颜色
- **颜色定制** - 为不同词性选择独特颜色
- **排版控制** - 调整字体大小、间距和粗细

#### 字典设置
- **语言选择** - 启用/禁用任何语言
- **词性过滤** - 选择要高亮的词性
- **专业词库** - 可选的专业领域词汇库

#### 处理模式
- **字典模式** - 快速、轻量、隐私保护


### 🔐 隐私保护

- ✅ 所有设置仅保存在浏览器本地
- ✅ 不收集、跟踪或上传任何数据
- ✅ 无广告、无分析、无第三方跟踪
- ✅ [查看完整隐私政策](PRIVACY.md)

### 📦 项目结构

```
EasyReaderADHD-Plugin/
├── manifest.json           # 扩展配置
├── popup.html              # 设置界面
├── popup.js                # 设置逻辑
├── content.js              # 内容脚本
├── background.js           # 后台服务
├── styles.css              # 样式表
├── dictionaries/           # 词典数据
│   ├── EN_word.json        # 英语词典
│   ├── ZH_word.json        # 中文词典
│   ├── JA_word.json        # 日语词典
│   └── ZH/                 # 中文专业词库
└── static/
    └── icon-128.png        # 扩展图标
```

### 🛠️ 开发

#### 依赖项
- Chrome 浏览器 (Manifest V3)
- 无额外依赖

#### 本地安装

1. 克隆仓库
```bash
git clone https://github.com/JerryLiu369/EasyReaderADHD-Plugin.git
```

2. 在 Chrome 中打开 `chrome://extensions/`

3. 启用"开发者模式"

4. 点击"加载未打包的扩展程序"，选择项目文件夹

#### 修改和测试

编辑 `popup.js`、`content.js` 或 `styles.css` 后，在 Chrome 的扩展管理页面点击刷新按钮。

### 🎓 词典数据

词典数据包含词性标签和特定领域词汇：
- 基础：名词、动词、形容词、其他词性
- 中文专业：成语、诗词、IT、财经、法律、医学、汽车、食物、动物、地名、历史人物

### 📝 许可证

[MIT License](LICENSE)

### 📧 联系方式

有问题或建议？请联系：**953639086@qq.com**

---

## English

### 🎯 Features

**EasyReaderADHD** is a powerful browser extension designed to help users with ADHD, dyslexia, and other reading challenges improve their reading experience.

#### Key Features
- 🎨 **Syntax-based text coloring** - Automatically color-code different parts of speech for better comprehension
- 🌍 **Multi-language support** - English, Chinese, Japanese, French, Spanish, Russian
- 🎭 **Customizable color themes** - 5 pre-designed themes + full customization
- ⚙️ **Fine-tuned controls**
  - Font size adjustment (50%-200%)
  - Letter spacing control
  - Font weight adjustment
  - Optional underline for highlighted words
- 📚 **Multiple dictionaries** - Basic dictionaries + specialized Chinese vocabularies (idioms, poetry, IT, finance, law, medicine, etc.)
- ✅ **Dictionary-based POS highlighting**

### 💡 Perfect for
- ADHD users struggling with reading focus
- Dyslexic readers needing visual aids
- Language learners improving comprehension
- Anyone wanting a more accessible reading experience

### 🚀 Quick Start

1. Install the extension from Chrome Web Store
2. Click the extension icon to open settings
3. Choose your preferred language and color scheme
4. Start reading! Text will be automatically highlighted

### 🔐 Privacy

- ✅ All settings stored locally in your browser
- ✅ No data collection, tracking, or transmission
- ✅ No ads, analytics, or third-party tracking
- ✅ [Full Privacy Policy](PRIVACY.md)

### 📦 Project Structure

```
EasyReaderADHD-Plugin/
├── manifest.json           # Extension configuration
├── popup.html              # Settings UI
├── popup.js                # Settings logic
├── content.js              # Content script
├── background.js           # Background service
├── styles.css              # Styles
├── dictionaries/           # Dictionary data
└── static/
    └── icon-128.png        # Extension icon
```

### 🛠️ Development

#### Requirements
- Chrome browser (Manifest V3)
- No additional dependencies

#### Local Installation

1. Clone the repository
```bash
git clone https://github.com/JerryLiu369/EasyReaderADHD-Plugin.git
```

2. Open `chrome://extensions/` in Chrome

3. Enable "Developer mode"

4. Click "Load unpacked extension" and select the project folder

### 📝 License

[MIT License](LICENSE)

### 📧 Contact

Questions or suggestions? Email: **953639086@qq.com**

---

**Made with ❤️ for accessible reading**
