# to-tk-h5

`to-tk-h5` 是一个面向 Codex、WorkBuddy 等 Agent 软件的本地 Skill，用于把普通 H5 课件改造成可上传到拓课云 / TK 教室使用的 H5 课件包。

这个 Skill 适合处理以下任务：

- 按拓课云 H5 课件规范修改已有 `index.html` 或 H5 项目。
- 补齐课堂 iframe 通信协议。
- 检查课件资源是否缺失。
- 检查打包结构是否符合上传要求。
- 输出可上传使用的 `.zip` 文件。

## 功能说明

使用该 Skill 后，Agent 会优先读取本仓库中的拓课云 H5 标准说明，并按规范处理课件项目。

主要处理内容包括：

- 检查入口文件 `index.html` 是否在项目根目录。
- 检查图片、音频、视频、CSS、JS 等本地资源是否存在。
- 检查上传包路径是否包含中文或高风险特殊字符。
- 添加或校验拓课云课堂所需通信方法：
  - `onLoadComplete`
  - `onPagenum`
  - 接收并处理 `onJumpPage`
  - 通过 `onFileMessage` 同步课件状态
- 避免课堂跳页和本地跳页之间产生消息循环。
- 生成符合上传结构的 zip 包。

## 目录结构

```text
to-tk-h5/
  SKILL.md
  agents/
    openai.yaml
  references/
    talkcloud-h5-standard.md
  scripts/
    tk_h5_package.py
```

关键文件说明：

- `SKILL.md`：Agent 识别和执行 Skill 的主说明文件。
- `references/talkcloud-h5-standard.md`：拓课云 / TK H5 课件标准整理文档。
- `scripts/tk_h5_package.py`：本地校验和打包脚本。
- `agents/openai.yaml`：Agent 软件可读取的展示信息。

## 在 Codex 中安装

### Windows

把本仓库克隆到 Codex 的本地 skills 目录：

```powershell
mkdir "$env:USERPROFILE\.codex\skills" -Force
git clone https://github.com/heiye07/to-tk-h5.git "$env:USERPROFILE\.codex\skills\to-tk-h5"
```

如果你的电脑无法通过 HTTPS 访问 GitHub，可以使用 SSH：

```powershell
git clone ssh://git@github.com/heiye07/to-tk-h5.git "$env:USERPROFILE\.codex\skills\to-tk-h5"
```

安装完成后，重启 Codex。重启后 Codex 应该能识别到 `to-tk-h5` 这个 Skill。

### macOS / Linux

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/heiye07/to-tk-h5.git ~/.codex/skills/to-tk-h5
```

安装完成后，重启 Codex。

## 在 WorkBuddy 或其他 Agent 软件中安装

如果 Agent 软件支持本地 Skill 目录，安装方式通常是：把整个仓库作为一个完整文件夹放进该软件的 skills 目录。

最终结构应类似：

```text
<agent-skills-folder>/to-tk-h5/SKILL.md
<agent-skills-folder>/to-tk-h5/agents/openai.yaml
<agent-skills-folder>/to-tk-h5/references/talkcloud-h5-standard.md
<agent-skills-folder>/to-tk-h5/scripts/tk_h5_package.py
```

注意事项：

- `SKILL.md` 必须位于 `to-tk-h5` 文件夹根目录。
- 不要只复制 `SKILL.md`，需要保留 `references` 和 `scripts` 目录。
- 复制或克隆完成后，重启 Agent 软件，或在软件中刷新 Skill 列表。

## 更新 Skill

如果你是通过 Git 安装的，可以进入 Skill 目录后拉取更新。

Codex Windows 示例：

```powershell
cd "$env:USERPROFILE\.codex\skills\to-tk-h5"
git pull
```

通用示例：

```bash
cd <agent-skills-folder>/to-tk-h5
git pull
```

如果 Agent 软件不会自动重新加载 Skill，更新后需要重启软件。

## 如何让 Agent 使用这个 Skill

在 Codex、WorkBuddy 或其他 Agent 软件中，可以直接点名 `to-tk-h5`。

示例提示词：

```text
使用 to-tk-h5，把 D:\h5-ppt\my-courseware 转成拓课云教室可上传的 H5 课件，并输出 zip。
```

```text
使用 to-tk-h5，检查这个 H5 课件是否符合拓课云上传标准。
```

```text
按照拓课云 H5 课件标准修改这个 index.html，并把修改后的源码和最终 zip 都放在项目文件夹里。
```

```text
把这个 H5 课件改成支持拓课云教室 iframe 加载、跳页同步和状态同步的版本。
```

Agent 完成后，通常应该输出：

- 修改后的项目文件夹路径。
- 最终 `.zip` 文件路径。
- 校验结果摘要。
- 缺失资源或无法完全还原的效果说明。

## 手动校验和打包

除了让 Agent 自动调用，也可以手动运行脚本。

校验项目：

```bash
python scripts/tk_h5_package.py validate /path/to/courseware-project
```

生成上传 zip：

```bash
python scripts/tk_h5_package.py package /path/to/courseware-project --out /path/to/courseware.zip
```

如果确认缺失资源是有意保留的，可以允许缺失资源继续打包：

```bash
python scripts/tk_h5_package.py package /path/to/courseware-project --out /path/to/courseware.zip --allow-missing-assets
```

不建议默认使用 `--allow-missing-assets`。如果资源真实缺失，课件上传后可能出现图片、音频、视频或样式无法加载的问题。

## 拓课云上传前检查清单

上传前至少确认：

- zip 根目录直接包含 `index.html`。
- 课件是单页 H5 应用，内部页码由 JS 状态控制。
- 图片、音频、视频、CSS、JS 等本地资源都存在。
- zip 内文件路径尽量使用英文、数字、横线、下划线和点号。
- `onLoadComplete` 在课件整体加载完成后只发送一次。
- `onPagenum` 发送正确的内部页数。
- 能接收课堂发来的 `onJumpPage` 并跳到对应页面。
- 能通过 `onFileMessage` 同步可恢复的课件状态。
- 本地翻页不会和课堂跳页产生重复广播或死循环。
- 页面布局能适应拓课云教室 iframe 容器。

## 说明

这个 Skill 的作用是帮助 Agent 按拓课云 H5 课件规范改造和打包课件。最终还原度取决于源课件本身。

如果源文件来自 PPT，且包含复杂动画、音频、视频、触发器、拖拽交互或课堂专用交互，Agent 应先检查源资源和现有 H5 结构，再说明哪些效果可以保留，哪些效果需要人工重建。
