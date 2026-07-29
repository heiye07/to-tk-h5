# to-tk-h5

`to-tk-h5` is an agent skill for converting, adapting, validating, and packaging HTML5 courseware so it can be uploaded and used in TalkCloud/TK classrooms.

It is designed for Codex, WorkBuddy, and other agent software that supports local skill folders containing a `SKILL.md` file.

## What This Skill Does

- Reads TalkCloud/TK H5 courseware requirements.
- Helps adapt an existing H5 project or single `index.html`.
- Adds or checks required iframe communication:
  - `onLoadComplete`
  - `onPagenum`
  - receiving `onJumpPage`
  - state sync through `onFileMessage`
- Checks root `index.html`, missing assets, and unsafe package paths.
- Packages the project into an upload-ready `.zip`.

## Repository Structure

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

## Install For Codex

### Windows

Clone this repository into the Codex skills directory:

```powershell
mkdir "$env:USERPROFILE\.codex\skills" -Force
git clone https://github.com/heiye07/to-tk-h5.git "$env:USERPROFILE\.codex\skills\to-tk-h5"
```

If GitHub HTTPS is blocked on your machine, use SSH:

```powershell
git clone ssh://git@github.com/heiye07/to-tk-h5.git "$env:USERPROFILE\.codex\skills\to-tk-h5"
```

Restart Codex after installation. The skill should appear as `to-tk-h5`.

### macOS / Linux

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/heiye07/to-tk-h5.git ~/.codex/skills/to-tk-h5
```

Restart Codex after installation.

## Install For WorkBuddy Or Other Agent Software

Use the same rule: place this repository as one complete folder inside the agent's local skills directory.

Example:

```text
<agent-skills-folder>/to-tk-h5/SKILL.md
<agent-skills-folder>/to-tk-h5/references/talkcloud-h5-standard.md
<agent-skills-folder>/to-tk-h5/scripts/tk_h5_package.py
```

The important requirement is that `SKILL.md` stays at the root of the `to-tk-h5` folder.

After copying or cloning the folder, restart the agent software or reload its skills list.

## Update The Skill

If the skill was installed with Git:

```bash
cd <agent-skills-folder>/to-tk-h5
git pull
```

For Codex on Windows:

```powershell
cd "$env:USERPROFILE\.codex\skills\to-tk-h5"
git pull
```

Restart the agent after updating if it does not reload skills automatically.

## How To Use In An Agent

Ask the agent to use this skill when converting H5 courseware for TalkCloud/TK.

Example prompts:

```text
使用 to-tk-h5，把 D:\h5-ppt\my-courseware 转成拓课云教室可上传的 H5 课件，并输出 zip。
```

```text
Use to-tk-h5 to validate this H5 courseware project for TalkCloud upload.
```

```text
按照拓课云 H5 课件标准修改这个 index.html，并保留修改后的源码和最终 zip。
```

Expected output from the agent:

- Modified project folder path.
- Final `.zip` path.
- Validation summary.
- Missing assets or fidelity limitations, if any.

## Manual Validation And Packaging

The helper script can also be run directly.

Validate a project:

```bash
python scripts/tk_h5_package.py validate /path/to/courseware-project
```

Create an upload zip:

```bash
python scripts/tk_h5_package.py package /path/to/courseware-project --out /path/to/courseware.zip
```

Allow packaging even when referenced assets are missing:

```bash
python scripts/tk_h5_package.py package /path/to/courseware-project --out /path/to/courseware.zip --allow-missing-assets
```

Only use `--allow-missing-assets` when you already know the missing files are intentional.

## Upload-Readiness Checklist

Before uploading to TalkCloud/TK classroom, confirm:

- The zip contains `index.html` at the root level.
- The project is a single-page H5 app.
- All required local assets exist.
- Package paths are ASCII-safe.
- `onLoadComplete` is sent once after loading.
- `onPagenum` sends the correct internal page count.
- `onJumpPage` is received and applied.
- `onFileMessage` syncs restorable state.
- The layout works inside an iframe.

## Notes

This skill helps an agent modify and package courseware, but final fidelity still depends on the source material. If the original PPT or H5 uses proprietary animation, audio, video, or classroom-specific interactions, the agent should inspect those assets and report anything that cannot be preserved exactly.
