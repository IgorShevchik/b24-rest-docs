# Upstream PR — title & body (one per section)

The script ships 6 sections, each as its own branch/PR:

| Label (commit scope) | Branch | Content |
|---|---|---|
| `crm/status` | `actualize/crm-status` | `api-reference/crm/status` |
| `crm/deals` | `actualize/crm-deals` | `api-reference/crm/deals` |
| `crm/leads` | `actualize/crm-leads` | `api-reference/crm/leads` |
| `crm/companies` | `actualize/crm-companies` | `api-reference/crm/companies` |
| `crm/currency` | `actualize/crm-currency` | `api-reference/crm/currency` |
| `calendar` | `actualize/calendar` | `api-reference/calendar` |

---

## Title

```
docs(<label>): actualize JS examples to TS + UMD (b24jssdk actions API)
```

e.g. `docs(crm/deals): …`, `docs(crm/currency): …`, `docs(calendar): …`.

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

- `crm/tasks` and `user` are **not** shipped: upstream has already actualized those pages
  itself (the fork kept its own variants during the sync). Shipping them would duplicate.
- All six sections above are the fork's own actualization (originally PRs #17/#20–#26 in the
  fork) and are still legacy upstream — i.e. genuinely new there.
