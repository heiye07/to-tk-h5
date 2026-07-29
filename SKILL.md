---
name: to-tk-h5
description: Convert, adapt, validate, and package HTML5 courseware so it can be uploaded and used in TalkCloud/TK classroom as H5 courseware. Use when the user asks to make an H5 courseware project compatible with 拓课云/拓课云教室/TalkCloud/TK classroom upload, including iframe postMessage communication, page navigation sync, resource checks, and zip packaging.
---

# To TK H5

Use this skill to turn an existing H5 lesson/courseware folder or single `index.html` into a TalkCloud-compatible H5 courseware package.

## Required Reference

Read `references/talkcloud-h5-standard.md` before modifying or reviewing a courseware project. It contains the exact protocol, packaging rules, and adapter pattern.

## Workflow

1. Locate the source project.
   - If the user provides only one `index.html`, copy it into a project output folder before editing.
   - Put both modified sources and final output under the user workspace/project folder, not under chat/download/cache folders.
   - Keep an original backup as `source-original/index.original.html`.

2. Inspect the H5 structure.
   - Count internal pages/slides.
   - Identify the existing navigation function or state variable.
   - Identify local assets referenced by `src`, `href`, `poster`, CSS `url(...)`, audio, video, and image tags.
   - Check whether assets exist next to the project; missing assets must be reported and should block final packaging unless the user explicitly accepts an incomplete package.

3. Add or adapt the TalkCloud bridge.
   - Send `onLoadComplete` once after the whole courseware is ready.
   - Send `onPagenum` once with the internal page count.
   - Listen for classroom `onJumpPage` and jump to the requested internal page.
   - When local navigation changes the page, send page state through `onFileMessage`; send `onJumpPage` only for deliberate local page-turn events.
   - Avoid feedback loops: classroom-triggered jumps must not re-broadcast as new local page turns.
   - Expose a stable debug/control object such as `window.TalkCloudCourseware`.

4. Add responsive and runtime safeguards.
   - Treat the courseware as an iframe-embedded single page.
   - Use a fixed courseware ratio when appropriate, usually `16 / 9`.
   - Avoid fixed viewport assumptions that make content clip inside the classroom iframe.
   - Avoid wheel-only navigation in classroom environments; keyboard/buttons/touch are safer.
   - Provide visible loading/status UI when the courseware depends on substantial assets.

5. Validate.
   - Run `scripts/tk_h5_package.py validate <project-dir>`.
   - Fix missing required protocol hooks, missing root `index.html`, non-ASCII package paths, and missing assets.
   - If browser validation is available, start a local static server and verify initialization, page count, local navigation, and a simulated `onJumpPage`.

6. Package.
   - Run `scripts/tk_h5_package.py package <project-dir> --out <workspace>/<name>.zip`.
   - Ensure the zip root contains `index.html` directly.
   - Ensure the zip contains no Chinese filenames or paths unless the user explicitly accepts the risk.
   - Do not include scratch folders such as `source-original`, `tools`, `ppt-unpacked`, or inspection outputs in the upload zip.

## Standard Adapter Pattern

For an existing deck controller, adapt its page jump method instead of rewriting the UI. The minimum bridge shape is:

```js
class CoursewareBridge {
  constructor(controller) {
    this.controller = controller;
    this.readySent = false;
    window.addEventListener("message", (event) => this.onMessage(event), false);
  }

  sendReadyOnce() {
    if (this.readySent) return;
    this.readySent = true;
    this.post({ method: "onLoadComplete", coursewareRatio: 16 / 9 });
    this.post({ method: "onPagenum", totalPages: this.controller.totalPages });
    this.syncState();
  }

  onMessage(event) {
    const message = this.parse(event.data);
    if (!message || typeof message.method !== "string") return;
    if (message.method === "onJumpPage") {
      this.controller.goToPage(Number(message.toPage) || 1, { fromClassroom: true });
    }
  }

  syncState() {
    this.post({
      method: "onFileMessage",
      handleData: {
        cmd: "courseware_state",
        info: {
          currentPage: this.controller.currentPage,
          totalPages: this.controller.totalPages
        }
      }
    });
  }

  post(payload) {
    window.parent.postMessage(JSON.stringify(payload), "*");
  }

  parse(raw) {
    if (!raw) return null;
    if (typeof raw === "object") return raw;
    try { return JSON.parse(raw); } catch { return null; }
  }
}
```

Adjust naming and indexing to match the existing app. TalkCloud page numbers are 1-based.

## Deliverables

Return:

- Modified project folder path.
- Final zip path.
- Validation summary.
- Any missing assets or fidelity limitations.

Do not claim the package is upload-ready if required local assets are missing or `index.html` is not at the zip root.
