# TalkCloud H5 Courseware Standard

Use this reference when adapting or reviewing H5 courseware for TalkCloud/TK classroom upload.

## Runtime Model

- Classroom loads the courseware inside an iframe.
- Courseware is an independent single-page web app.
- Classroom and courseware communicate with `window.postMessage`.
- Message payloads should be JSON strings.
- Every message must include `method` as a string.

## Packaging Rules

- Upload format: `.zip`.
- Entry file: `index.html`.
- `index.html` must be at the first level of the zip.
- Use one HTML entry file for one courseware package.
- Build as a single-page app; internal pages are app states, not separate HTML files.
- File and folder names should use ASCII-safe English letters, digits, hyphens, underscores, dots, and common English symbols. Avoid Chinese characters in package paths.
- On macOS, zip the files inside the courseware folder, not the folder itself.

## URL Parameters From Classroom

Read these from `window.location.search` when needed:

- `role`: `-1` playback viewer, `0` teacher, `1` assistant, `2` student, `4` inspector.
- `name`: user name.
- `userid`: user id.
- `roomtype`: classroom type.
- `isH5MediaOutput`: whether external audio output is enabled.
- `isclassbegin`: when `true`, class has already started.

## Required Startup Messages

After the entire courseware is ready, send once:

```js
window.parent.postMessage(JSON.stringify({
  method: "onLoadComplete",
  coursewareRatio: 16 / 9
}), "*");
```

Then send total internal pages:

```js
window.parent.postMessage(JSON.stringify({
  method: "onPagenum",
  totalPages: 18
}), "*");
```

Rules:

- Send `onLoadComplete` only once for the whole courseware.
- Do not send `onLoadComplete` for every internal page.
- `coursewareRatio` is width divided by height. Use `16 / 9` for common slide decks unless the source uses another ratio.
- Send `onPagenum` after the page count is known.

## Page Navigation

The classroom sends:

```js
{
  method: "onJumpPage",
  toPage: 2
}
```

Required behavior:

- Listen to `window` `message`.
- Parse string JSON safely.
- Treat `toPage` as 1-based.
- Jump the internal SPA state to that page.
- Mark classroom-triggered jumps so they do not cause a feedback loop.

For local navigation:

- Update the local page first.
- Sync current page state through `onFileMessage`.
- If the local navigation represents a real page turn, optionally send `onJumpPage` to notify classroom.

## Custom State Sync

Send custom state with:

```js
window.parent.postMessage(JSON.stringify({
  method: "onFileMessage",
  handleData: {
    cmd: "courseware_state",
    info: {
      currentPage: 2,
      totalPages: 18
    }
  }
}), "*");
```

Rules:

- Custom events must carry restorable state, not just an action.
- A late-joining user or replay should be able to restore the relevant page state from the latest custom event.
- Do not sync drag movement continuously; sync final or meaningful state.
- Avoid high-frequency custom messages.
- Handle custom events both when sending and receiving if they affect visible state.

## Voice Assessment Events

Start assessment:

```js
window.parent.postMessage(JSON.stringify({
  method: "startAssessment",
  handleData: {
    lanType: 0,
    contentText: "Thank you",
    strictLevel: 2,
    duration: 10
  }
}), "*");
```

Fields:

- `lanType`: `0` English, `1` Chinese.
- `contentText`: assessment text, max 30 English words or Chinese characters.
- `strictLevel`: float from `1.0` to `4.0`; higher is stricter.
- `duration`: `10`, `20`, `30`, or `60` seconds; default is `60`.

Finish assessment:

```js
window.parent.postMessage(JSON.stringify({
  method: "finishAssessment"
}), "*");
```

Listen for:

- `startAssessmentRes`: `data.code`, where `0` failed and `1` succeeded.
- `assessmentEnd`: `data.code` and `data.score`; score range `0` to `100`.

## Class Start State

Class start can arrive from:

- URL parameter `isclassbegin=true`.
- Message `onClassStateChange`, where `message.isClassBegin === true`.

If the URL already has `isclassbegin=true`, do not wait for `onClassStateChange`.

## Upload-Readiness Checklist

- Root `index.html` exists.
- Zip root contains `index.html` directly.
- Project is a single-page app.
- Required assets are present.
- Package paths are ASCII-safe.
- `onLoadComplete` exists and is sent once.
- `onPagenum` exists and uses the correct page count.
- `onJumpPage` is received and applied.
- `onFileMessage` syncs restorable state.
- Local page turns avoid classroom feedback loops.
- Layout adapts to iframe size.
- Loading/status state is visible when large resources are used.
