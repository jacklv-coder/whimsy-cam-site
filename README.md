# Whimsy Cam / 奇想相机

五种语言的纯静态官网、隐私政策与支持页面。HTML + CSS，无框架、无构建步骤、无外部脚本或字体。内容依据 `nomo/appstore/site/BRIEF.md`（2026-10-07），措辞参考同仓库的五种语言 App Store metadata。

## 本地预览

在本目录运行：

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

打开 `http://127.0.0.1:8765/`。也可直接打开 `index.html` 或任意语言页面。路径全部采用相对链接，适用于 GitHub Pages 的 `/whimsy-cam-site/` 项目路径。

根页面按 `navigator.languages` 的偏好顺序选择支持的语言：`zh-TW`、`zh-HK` 或带 `zh-Hant` 的中文标签进入繁体中文；其余中文标签进入简体中文；日语、韩语和英语进入对应目录；都不匹配则使用英语。JavaScript 关闭时仍显示五个语言入口。

## 文件清单

```text
.gitignore
.nojekyll
index.html                       语言入口；唯一含脚本的页面
style.css                        全站样式与移动端布局
icon.png                         App 图标，256 × 256
assets/
  beach.jpg                      装饰图片，800 × 1067
  street.jpg                     装饰图片，800 × 1067
  dino.jpg                       装饰图片，800 × 1067
zh-hans/
  index.html
  privacy.html
  support.html
zh-hant/
  index.html
  privacy.html
  support.html
en/
  index.html
  privacy.html
  support.html
ja/
  index.html
  privacy.html
  support.html
ko/
  index.html
  privacy.html
  support.html
scripts/
  check_site.py                  静态内容、链接和资源检查
  check_language.mjs             语言分流逻辑检查，无浏览器依赖
README.md
CHECKS.md                        检查结果、限制与人工复核清单
```

`.qa/` 是已忽略的本地工作目录，不属于网站交付文件。

## 维护与检查

`zh-hans/harmony-privacy.html` 是中国大陆鸿蒙版的独立隐私政策，版本为 2026-10-13，内容与鸿蒙 App 内 `rawfile/privacy/policy.json` 同步。原有五种语言的 `privacy.html` 继续适用于 iOS；鸿蒙政策不复用 iOS 字体下载或备份说明。鸿蒙 0.3.0 暂不提供录像，也不申请麦克风权限；政策页面上线不代表 App 已上架。

直接编辑 HTML 和 CSS，无需生成器或安装依赖。导航、页尾和政策修改应同步五种语言。同页语言切换使用明确的 HTML 文件名，离线预览时也可以跳转。

```sh
python3 scripts/check_site.py
node scripts/check_language.mjs
```

Python 检查使用标准库（Python 3.9+）；语言分流检查使用 Node.js 内置模块。它们都是开发检查工具，浏览器不会加载。

移动端需要另外用浏览器逐页实测 `document.documentElement.scrollWidth <= window.innerWidth`，并在支持页展开全部 FAQ 后复测。静态检查不能替代渲染检查。具体结果见 [CHECKS.md](CHECKS.md)。

## 素材来源

所有素材仅从 `/Users/jintao/develop/claude/nomo` 读取，输出文件写入本目录：

- `icon.png` ← `ios/Rewind/Resources/Assets.xcassets/AppIcon.appiconset/AppIcon.png`。
- `assets/beach.jpg` ← `appstore/source/scenes/scene-01-corgi-beach.jpg`。
- `assets/street.jpg` ← `appstore/source/scenes/scene-10-street-dusk.jpg`。
- `assets/dino.jpg` ← `appstore/source/scenes/scene-12-clay-dino.jpg`。

装饰图不是 App 截图，也不作为相机成片效果的展示。图片已缩小、压缩并移除 EXIF。网站使用系统字体，FAQ 使用原生 `details` / `summary`，15 个内容页无需 JavaScript。

## 部署

公开仓库为 `jacklv-coder/whimsy-cam-site`。GitHub Pages 从 `main` 分支根目录发布，预期地址为 `https://jacklv-coder.github.io/whimsy-cam-site/`。Git 远端使用 SSH。`.qa/` 是本地检查材料，不进入公开仓库。
