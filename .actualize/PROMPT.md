# Prompt: actualizing b24jssdk JS examples (TS + UMD)

You are given a **path to a single documentation `.md` file** of the Bitrix24 REST API (usually
under `api-reference/**`). The task is to replace the deprecated example in the **`- JS`** tab
(which uses `$b24.callMethod` / `$b24.callListMethod` / `$b24.fetchListMethod`, removed in
b24jssdk 2.0) with **two tabs** — **`- JS (TS)`** and **`- JS (UMD)`** — on the current SDK API. Do not
change the page content, only the example.

Input: `<PATH>` — the path to the file.

## Hard rules

1. **Change only the example** inside the `{% list tabs %}` block. Do NOT touch the rest of the
   text: headings, parameter descriptions, the "response handling" section, error codes,
   "continue learning".
2. **Remove the `- JS` tab** (old jsSDK) and put in its place, in order: **`- JS (TS)`**, then
   **`- JS (UMD)`** (the doc-team tab-naming convention — keep the `JS (…)` wrapper exactly). A page
   may have **several** `{% list tabs %}` code-example blocks (each with its own `- JS` tab) —
   convert **every** one of them.
3. **Do NOT touch** the `cURL (Webhook)`, `cURL (OAuth)`, `PHP`, `BX24.js`, `PHP CRest`, or
   `Python` (b24pysdk) tabs — neither the code nor the order. Only the `- JS (TS)` / `- JS (UMD)`
   tabs are in scope; leave every other-language tab byte-for-byte unchanged.
4. Carry the request parameters over from the old JS example **1:1** (`taskId`, `fields`,
   `select`, `filter`, `order`, `params`, `start`, `id`, `entityTypeId`, etc.).
5. **Comments and example string values are in English.**
6. **In the TS/UMD example, remove calls to non-existent functions** (`processResult(...)`,
   `processData(...)`, etc.) — replace them with a meaningful `console.info(...)` over the real
   response fields. Do NOT touch such calls in the PHP/BX24.js/cURL tabs — they are out of scope.

## API version (v2 / v3)

- Default — **`actions.v2`**.
- It is **`actions.v3`** ONLY if one of these two explicit signals holds:
  - the file lives under `api-reference/rest-v3/**`, OR
  - the old JS example being converted already calls `actions.v3.*`.
- Do **NOT** infer the version from the response shape. `result.item` describes the *payload*,
  not the API version — e.g. `crm.item.*` are rest-v2 yet return `result.item`. Type the `item`
  shape from the page, but keep `actions.v2`.
- Any other case (neither signal applies, or the version is unclear) — do **NOT** guess v3: keep
  the `actions.v2` default and flag it for maintainer confirmation (manual run: ask; batch run:
  leave a `// TODO: confirm API version` comment and report it).
- Take the result type `<T>` from the response shape on the page: `{ task: {...} }`,
  `{ item: {...} }`, `{ tasks: [...] }`, `{ fields: {...} }`, `{ order: {...} }`, `boolean` fields,
  etc.
- Apply the chosen version (`v2`/`v3`) to **both** tabs — TS and UMD. In the templates below
  `actions.v2` is shown as the default example.

## List methods (`*.list`, the old `callListMethod` / `fetchListMethod`)

Use **`actions.v2.call.make` with the `start` parameter** (a single-page call). Reason: the list
helpers `callList.make` / `fetchList.make` paginate by an id cursor and **do not accept `order`**
(it is excluded from their parameter type — passing it is a `tsc` error), and sorting in examples
usually matters.
- read the array from `result.<key>` (e.g. `result.tasks`, `result.items`);
- ABOVE `const response` leave a hint comment that for a full fetch there are **two** helpers:
  `$b24.actions.v2.callList.make()` (returns the whole array at once) and
  `$b24.actions.v2.fetchList.make()` (an async generator over chunks) — with a `NOTE:` that both
  do not accept `order` (excluded from the parameter type);
- do NOT use `response.getTotal()` (deprecated, removed in SDK 2.0) — show the page size via
  `result.<key>.length`.

## Reading the response: `getData()!` vs `getData()`

- JS (TS) — in the `else` branch (`isSuccess === true`): `response.getData()!.result` (with `!`).
- JS (UMD) — after `if (!isSuccess) { …; return }`: `response.getData().result` (without `!`).
- Do NOT use `response.getTotal()` — it is `@deprecated` / `@removed 2.0.0` (tied to the v2 `total`
  field, absent in v3). Page size — `result.<key>.length`; the full count — via a list helper
  (`callList.make` → whole array → `.length`) or `aggregate` (count) in v3.

## ES module and SDK version

- The TS example is an ES module (it has `import` and top-level `await`); this is noted in a comment
  at `declare const $b24`. It must not be pasted into a plain `<script>` without `type="module"`.
- The UMD tag uses the major tag `@1` (protection against major breaking changes); the typecheck is
  pinned by the committed lockfile `.actualize/typecheck/package-lock.json` (a specific 1.x).
- Set `requestId` via the SDK generator: `Text.getUuidRfc4122()` (TS, `import { Text }`) and
  `B24Js.Text.getUuidRfc4122()` (UMD) — do not hardcode a string.
- Put the explanatory comments (about the ES module and the ready `$b24`) **first** in the TS
  snippet, before `import`. Import the type as `import type { B24Frame[, ISODate] }`; date fields in
  the result type are `ISODate | null` (not `string | null`).

## If there is nothing to change

No `{% list tabs %}` block or no `- JS` tab → print `SKIP: no JS tab` and do not change the file.
(The two new tabs are labelled `JS (TS)` and `JS (UMD)` — the `- JS` referred to here is the OLD
single jsSDK tab being replaced, not the new ones.)

## JS (TS) tab (assumes an already-initialized `$b24`)

```ts
// This snippet is an ES module: top-level await requires type="module" or a bundler.
// $b24 is an already-initialized SDK instance (see the SDK "Get started" guide).
import { Text } from '@bitrix24/b24jssdk'
import type { B24Frame } from '@bitrix24/b24jssdk' // add ISODate, etc. for typed date fields

declare const $b24: B24Frame

// Shape of the payload returned in result (match the "response handling" section of the page)
type <Name>Result = {
  // ...
}

try {
  const response = await $b24.actions.v2.call.make<<Name>Result>({
    method: '<rest.method>',
    params: {
      // parameters copied 1:1 from the original example, comments in English
    },
    requestId: Text.getUuidRfc4122()
  })

  // The payload is available only on a successful response
  if (!response.isSuccess) {
    console.error(response.getErrorMessages().join('; '))
  } else {
    const result = response.getData()!.result
    console.info(/* read real response fields */)
  }
} catch (error) {
  // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
  console.error(error)
}
```

## JS (UMD) tab (full initialization)

In UMD, `call.make` is called **without** the generic `<T>` parameter (this is plain JS, not TS).

```html
<!-- Load the SDK (UMD build); it is exposed as the global B24Js -->
<script src="https://unpkg.com/@bitrix24/b24jssdk@1/dist/umd/index.min.js"></script>
<script>
  async function <verbNoun>() {
    try {
      // Initialize the SDK inside a Bitrix24 frame
      const $b24 = await B24Js.initializeB24Frame()

      const response = await $b24.actions.v2.call.make({
        method: '<rest.method>',
        params: { /* same params as TS */ },
        requestId: B24Js.Text.getUuidRfc4122()
      })

      // The payload is available only on a successful response
      if (!response.isSuccess) {
        console.error(response.getErrorMessages().join('; '))
        return
      }

      const result = response.getData().result
      console.info(/* read real response fields */)
    } catch (error) {
      // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
      console.error(error)
    }
  }

  document.addEventListener('DOMContentLoaded', <verbNoun>)
</script>
```

## Tab format (YFM)

Each tab: a `- Name` line, a blank line, then a code block indented by **4 spaces**:

```
- JS (TS)

    ```ts
    ...code...
    ```

- JS (UMD)

    ```html
    ...code...
    ```
```

## Code style (mandatory)

Keep examples uniform — across 400+ files small drifts compound and make reviews noisy:

- **Body indentation:** inside the 4-space YFM tab indent, use **2-space** steps for the example
  body (not 4). `tsc` / `node --check` accept either, but the corpus standard is 2-space.
- **Trailing commas:** include them in multi-line object / array literals (the last property of
  nested literals like `params`, `fields`, …); **none** after the last property of the outer
  `call.make({ … })` argument object — i.e. no trailing comma after `requestId`, the final call
  argument (see the TS/UMD template above). `validate.py` enforces this.
- **Mandatory template comments (enforced by `validate.py`):** the success-guard comment before
  `if (!response.isSuccess)`, the UMD init comment before `initializeB24Frame()`, the catch comment
  as the first line of `catch (error)`, and `// Shape of the payload returned in result (…)` before
  the main result type. Use the exact wording from the template above. (Exception: a **primitive**
  result — a bare `call.make<boolean>` / `<string>` / `<number>` with no local `type` alias —
  carries no Shape comment; see **Result type patterns**.) **List methods** (the
  `.make<X[]>` generic) use the element form instead — `// Shape of each <item> returned in result[]`
  — describing one element of the `result[]` array; `validate.py` accepts either form.
- **List NOTE — one canonical wording.** Above `const response` for `*.list` methods:

    ```ts
    // <rest.method> returns a single page (max 50 records). For the whole result set
    // use a list helper: $b24.actions.v2.callList.make() returns every record as one
    // array, $b24.actions.v2.fetchList.make() yields them in chunks (async generator).
    // NOTE: the list helpers do not accept `order` (it is excluded from their params, so
    // passing it is a TS error) — keep this call.make + `start` variant when sort matters.
    ```

## Result type patterns

The `<T>` in `call.make<T>` follows the response shape; three shapes recur (all seen in `crm/currency`):

- **Primitive** (`result: true`, an id string, a count) → `call.make<boolean>` (or
  `call.make<string>` / `call.make<number>`) with **no local `type` and no Shape comment** (the
  Shape comment is enforced only on a local `type X = { … }` alias — see Code style). `validate.py`
  then prints an advisory `make<…> generic(s) with no local type alias (Shape check N/A)` — that is
  expected, not a failure.
- **Object keyed by dynamic keys** (`*.fields` → `{ FIELD: {…} }`; localization maps →
  `{ lang: {…} }`) → `type X = Record<string, Item>` plus a helper `type Item = { … }`; the Shape
  comment goes before the alias. Document `Item`'s fields from the page's JSON response example (the
  same block you would use for a normal result type). The field cross-check confronts **neither**
  with the page: the `Record<…>` alias has no `{ }` body (nothing to scan), and the helper `Item` is
  skipped because the check is scoped to the `.make<X>` generic *by name* — `Item` is not the
  generic, so it cannot false-fail. Read the map with `Object.keys(result)` / `result[key]`.
- **List returning the array directly** (`result: [ … ]`, not `result.<key>`) → `call.make<Item[]>`;
  `response.getData()!.result` IS the array (`result.length`, iterate it). This is still a `*.list`
  method, so keep the `call.make` + `start` variant and add the list NOTE above `const response`
  (see the **List NOTE** bullet in Code style) — the only difference is that `result` itself is the
  array.

`getData()!` (the TS non-null `!`) is safe **only inside the `else` branch**, after the
`isSuccess` guard has passed — do not hoist it above the guard.

## When the cURL endpoint disagrees with the page (cross-check failure)

`validate.py` cross-checks the SDK `method:` against the cURL `/rest/.../<method>` endpoint. A
mismatch is almost always a **copy-paste bug** in a cURL/PHP tab (an endpoint — and often its
params — pasted in from another method). The real method is what the page **title**, the JS /
PHP-core tabs and the "response handling" section agree on.

- Take the SDK `method:` from the page — **never** bend the example to match a wrong cURL endpoint.
- Fix the **cURL (Webhook)** and **cURL (OAuth)** tabs (endpoint **and** payload) to match the page.
  This is a narrow, sanctioned exception to rule 3: a wrong endpoint in a copy-paste example
  actively misleads readers. Do it **only when the correct method is unambiguous** — stated in the
  page title and agreed by the JS / PHP-core tabs and the response section. If it is not: in a
  **manual** run, confirm with whoever assigned the task before editing; in **batch mode**
  (`run-batch.sh` — no interactive channel) do **not** touch the cURL tab, leave it and record the
  mismatch as a finding (let the file `SKIP` if needed). Never guess an endpoint.
- Leave the remaining other-language tabs (PHP CRest, BX24.js, `Python`) untouched and record the
  residual mismatch as a finding for the PR.

## Validation (required)

> **In batch mode (`run-batch.sh`)** the steps below are done by the ORCHESTRATOR, not you: the
> agent has no Bash tool (`--allowed-tools Read Edit Grep`). Just make the edit and stop — the
> runner does validation and the ledger write. The commands below are for a **manual** run.

1. `python3 .actualize/validate.py <PATH>` → must be `PASS`. It checks: tab structure (no `- JS`,
   `- JS (TS)`/`- JS (UMD)` present); extracts blocks ONLY from inside `{% list tabs %}` (every code-example
   block — a page may have several, and each is validated); forbidden tokens
   (`callMethod`/`callListMethod`/`fetchListMethod`/`processResult`/`processData`); the presence of
   `$b24.actions.v{2,3}.*` in **both** tabs; a **field/method cross-check** (the `method:` must match
   the page's cURL `/rest/.../<method>` endpoint, and every result-type field must be documented on the
   page — in a JSON response example or a `|| **field** ||` table row — so the result type is grounded in
   the page, not invented); `tsc --strict` against the PINNED `@bitrix24/b24jssdk` version (= 0 errors);
   `node --check` on the UMD.
2. If `FAIL` — fix the code and repeat until `PASS`.

## Recording completion

> In batch mode the orchestrator does this too — the manual step below is not needed.

After `PASS`: `python3 .actualize/record.py <PATH> done` — an idempotent upsert (one row per file:
date, sha256, status, method) into `.actualize/ledger.tsv`. Drift control:
`python3 .actualize/record.py --verify-all`. List of remaining: `python3 .actualize/remaining.py`.

## Checklist before finishing

> Not filled in on `SKIP` (the file was not changed).

- [ ] the `- JS` tab is removed, `- JS (TS)` and `- JS (UMD)` added (in every code-example block)
- [ ] the other-language tabs (cURL / PHP / BX24.js / PHP CRest / `Python` b24pysdk) and the page text are unchanged
- [ ] no `callMethod` / `callListMethod` / `fetchListMethod` in the jsSDK example
- [ ] no `processResult` / `processData` calls
- [ ] comments and values in English
- [ ] explanatory comments (ES module, `$b24`) first; in TS `import type { B24Frame }` (+`ISODate` for dates), in UMD — `B24Js.*` without import
- [ ] `requestId` via `Text.getUuidRfc4122()` (TS) / `B24Js.Text.getUuidRfc4122()` (UMD)
- [ ] `getData()!` in TS / `getData()` in UMD; for lists — `.length` (NOT `getTotal()`, it is deprecated)
- [ ] for lists — a hint about `callList.make` and `fetchList.make` (with a `NOTE` about ignoring `order`)
- [ ] SDK `method:` equals the cURL endpoint — a mismatch means a copy-paste bug on the page (fix the cURL Webhook/OAuth tabs: endpoint **and** payload; flag the rest; in batch mode leave ambiguous cases untouched)
- [ ] `validate.py` → PASS
- [ ] `record.py ... done` done

---
_Last reviewed: 2026-06-05_
