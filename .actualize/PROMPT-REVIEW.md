# Prompt: review of an actualized file

You are given a **path to a `.md` file** that has already been actualized per
`.actualize/PROMPT.md`. Review it and fix it if needed. Change only the example (the `- JS (TS)` /
`- JS (UMD)` tabs).

Input: `<PATH>`.

## What to check

1. **Tab structure**: `- JS (TS)` and `- JS (UMD)` are present, the `- JS` tab (old jsSDK) is gone. The
   `cURL`, `PHP`, `BX24.js`, `PHP CRest` tabs are in place and unchanged — **except** a `cURL`
   (Webhook/OAuth) endpoint/payload deliberately corrected for a copy-paste method mismatch (see
   PROMPT.md, "When the cURL endpoint disagrees with the page"). A page may have several
   `{% list tabs %}` code-example blocks — check that **every** one was converted.
2. **No deprecated calls**: the example has no `callMethod`, `callListMethod`, `fetchListMethod`.
   The call goes through `actions.v2.call.make` (or `actions.v3.call.make` ONLY for a
   `rest-v3/**` file or an example that already calls `actions.v3.*` — not inferred from a
   `result.item` response) — the same version in **both** tabs (TS and UMD).
3. **Response handling**: `try/catch` + an `if (!response.isSuccess)` check with
   `getErrorMessages()`, then reading `getData()!.result` (TS) / `getData().result` (UMD).
4. **Parameters 1:1** with the old example and with the cURL/PHP tabs (method, fields, filters
   match).
5. **English**: comments and string values are translated; no `processResult` / `processData`
   calls.
6. **List methods**: a single variant — `call.make` with `start` (preserves `order`). Above
   `const response` — a comment about **both** helpers `callList.make` / `fetchList.make` with a
   `NOTE` that they do NOT accept `order` (excluded from their type — a `tsc` error if passed).
   `response.getTotal()` is NOT used (deprecated/removed 2.0.0) — page size via `.length`.
7. **The `<T>` type** in TS matches the page's "response handling" section; date fields are
   `ISODate | null`. A primitive result is a bare `make<boolean>` / `<string>` / `<number>` (no
   local `type`, no Shape comment); a dynamic-key map is `type X = Record<string, Item>` + a helper
   (see PROMPT.md, "Result type patterns").
8. **The page text outside the tabs is unchanged** (if the changes are already committed:
   `git show HEAD -- <PATH>` should touch only the `{% list tabs %}` blocks — the code examples,
   plus, where it applies, the corrected `cURL` Webhook/OAuth endpoint/payload). Do not otherwise
   touch the PHP/BX24.js/cURL tabs — their Russian comments and pre-existing `processData()` stay as
   they are.
9. **`requestId`** is generated via `Text.getUuidRfc4122()` (TS) / `B24Js.Text.getUuidRfc4122()`
   (UMD), not a hardcoded string. In TS there is `import { Text }` and `import type { B24Frame }`
   (+`ISODate` if the type has date fields).
10. **TS header order**: the explanatory comments (ES module, `$b24`) come first, before `import`.

## Validation

- `python3 .actualize/validate.py <PATH>` → `PASS`.
- If you fixed something — re-run validation and update the mark:
  `python3 .actualize/record.py <PATH> reviewed`.
  `reviewed` overwrites `done` (one row per file — this is intentional).

---
_Last reviewed: 2026-06-05_
