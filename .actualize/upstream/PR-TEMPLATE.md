# Upstream PR — title & body (one per section)

Use this for each upstream PR opened from a branch that
`.actualize/upstream/contribute-to-upstream.sh` pushed. The script auto-selects which sections
ship and prints a compare URL per section; the live shipped/in-review list lives in
`.actualize/UPSTREAM.md`. Replace `<label>` below with the section (e.g. `crm/contacts`,
`telephony`, `catalog`).

## Title

```
docs(<label>): actualize JS examples to TS + UMD```

e.g. `docs(crm/contacts): …`, `docs(telephony): …`, `docs(catalog): …`.

## Body

```markdown
## What

Actualizes the JavaScript examples in **<label>**: the legacy `- JS` tab
(`$b24.callMethod` / `callListMethod` / `fetchListMethod`) is replaced by two tabs —
`- JS (TS)` and `- JS (UMD)` — on the current actions API (`$b24.actions.v2.call.make`).

## Why

`callMethod` / `callListMethod` / `fetchListMethod` are **removed in `@bitrix24/b24jssdk` 2.0**.
The examples now use the supported actions API: a typed TypeScript variant and a
copy-paste UMD variant that runs inside a Bitrix24 frame.

## Scope & guarantees

- **Only the `- JS` tab changes.** The cURL (Webhook/OAuth), PHP, BX24.js, PHP CRest and
  Python tabs, and all page prose / parameter tables / response sections, are unchanged.
- List methods use `call.make` with `start`; `getTotal()` (removed in SDK 2.0) is replaced by
  `.length` + the list helpers.
- Each example was validated in the fork (`tsc` against `@bitrix24/b24jssdk`, plus a structural
  `- JS (TS)` / `- JS (UMD)` check). The branch carries only this section's `api-reference/`
  content — no tooling, no CI files.
- One section per PR to keep review small.

No breaking changes — documentation examples only.
```

---

### Notes

- The branch is built off **fresh `upstream/main`**, so its diff is exactly this section's
  example changes — nothing to "un-revert" from newer upstream edits.
- `user/` and `tasks/` are **not** shipped from here: upstream actualized those pages itself, so
  the auto-detect rule skips them (no legacy left upstream → not selected).
