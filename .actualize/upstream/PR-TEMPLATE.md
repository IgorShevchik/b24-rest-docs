# Upstream PR — title & body (use one per section)

Replace `<section>` with `status` / `deals` / `leads` / `companies`.

---

## Title

```
docs(crm/<section>): actualize JS examples to TS + UMD (b24jssdk actions API)
```

## Body

```markdown
## What

Actualizes the JavaScript examples in **crm/<section>**: the legacy `- JS` tab
(`$b24.callMethod` / `callListMethod` / `fetchListMethod`) is replaced by two tabs —
`- JS (TS)` and `- JS (UMD)` — on the current actions API (`$b24.actions.v2.call.make`).

## Why

`callMethod` / `callListMethod` / `fetchListMethod` are **removed in `@bitrix24/b24jssdk` 2.0**.
The examples now use the supported actions API: a typed TypeScript variant and a
copy-paste UMD variant that runs inside a Bitrix24 frame.

## Scope & guarantees

- **Only the `- JS` tab changes.** The cURL (Webhook/OAuth), PHP, BX24.js, PHP CRest and
  Python tabs, and all page prose / parameter tables / response sections, are unchanged.
- List methods use `call.make` with `start` and link the `callList.make` / `fetchList.make`
  helpers; `getTotal()` (removed in SDK 2.0) is replaced by `.length` + helpers.
- Each example is verified: `tsc --strict` against `@bitrix24/b24jssdk@1`, `node --check`
  on the UMD tab, and a method/field cross-check against the page's cURL endpoint and JSON
  response.
- One section per PR to keep review small.

No breaking changes — documentation examples only.
```

---

### Notes

- `crm/tasks` and `user` were **not** included: upstream has already actualized those pages
  itself (the fork kept its own variants during the sync). Shipping them would duplicate.
- `currency` is actualized in the fork too; add `currency` to `$SECTIONS` in the script if
  you decide to contribute it as a 5th PR.
