#!/usr/bin/env python3
"""Offline unit tests for the .actualize tooling (stdlib unittest, no network).

Run: python -m unittest discover -s .actualize/tests -p 'test_*.py'
"""
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _tabs            # noqa: E402
import record           # noqa: E402
import remaining        # noqa: E402
import validate         # noqa: E402

VALID = """# Page

{% list tabs %}

- TS

```ts
// This snippet is an ES module: top-level await requires type="module" or a bundler.
// $b24 is an already-initialized SDK instance (see the SDK "Get started" guide).
import { Text } from '@bitrix24/b24jssdk'
import type { B24Frame } from '@bitrix24/b24jssdk'
declare const $b24: B24Frame
const r = await $b24.actions.v2.call.make({ method: 'crm.lead.add', params: {}, requestId: Text.getUuidRfc4122() })
```

- UMD

```html
<script src="https://unpkg.com/@bitrix24/b24jssdk@1/dist/umd/index.min.js"></script>
<script>
// Initialize the SDK inside a Bitrix24 frame
const $b24 = await B24Js.initializeB24Frame()
const r = await $b24.actions.v2.call.make({ method: 'crm.lead.add', params: {}, requestId: B24Js.Text.getUuidRfc4122() })
</script>
```

{% endlist %}
"""

# Template-compliant fixture for the style/comment checks: all four mandatory comments,
# the success-guard, the catch comment, the Shape comment before the main result type, and
# no trailing comma after requestId. Each style test breaks exactly one rule.
STYLED = '''# Page

{% list tabs %}

- TS

```ts
import { Text } from '@bitrix24/b24jssdk'
import type { B24Frame } from '@bitrix24/b24jssdk'
declare const $b24: B24Frame

// Shape of the payload returned in result (match the "response handling" section of the page)
type DemoResult = {
  id: number
}

try {
  const response = await $b24.actions.v2.call.make<DemoResult>({
    method: 'crm.lead.add',
    params: {
      title: 'x',
    },
    requestId: Text.getUuidRfc4122()
  })

  // The payload is available only on a successful response
  if (!response.isSuccess) {
    console.error(response.getErrorMessages().join('; '))
  } else {
    const result = response.getData()!.result
    console.info(result.id)
  }
} catch (error) {
  // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
  console.error(error)
}
```

- UMD

```html
<script src="https://unpkg.com/@bitrix24/b24jssdk@1/dist/umd/index.min.js"></script>
<script>
async function demo() {
  try {
    // Initialize the SDK inside a Bitrix24 frame
    const $b24 = await B24Js.initializeB24Frame()

    const response = await $b24.actions.v2.call.make({
      method: 'crm.lead.add',
      params: {
        title: 'x',
      },
      requestId: B24Js.Text.getUuidRfc4122()
    })

    // The payload is available only on a successful response
    if (!response.isSuccess) {
      console.error(response.getErrorMessages().join('; '))
      return
    }

    const result = response.getData().result
    console.info(result.id)
  } catch (error) {
    // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)
    console.error(error)
  }
}
</script>
```

{% endlist %}
'''

# A page with TWO {% list tabs %} blocks: a parameter-description block (no code)
# then the code-examples block. validate/record must target the code one.
PARAM_TABS = (
    "{% list tabs %}\n\n- crm\n\nPlain prose describing a parameter, no code fence.\n\n"
    "- iblock\n\nMore prose.\n\n{% endlist %}\n"
)
MULTIREGION = ("# Page\n\n## Parameter SETTINGS\n\n" + PARAM_TABS
               + "\n## Code examples\n\n" + VALID.split("# Page\n\n", 1)[1])


def replace_nth(s, old, new, n):
    if n < 1:
        return s
    i = -1
    for _ in range(n):
        i = s.find(old, i + 1)
        if i < 0:
            return s
    return s[:i] + new + s[i + len(old):]


def write_md(content):
    fd, path = tempfile.mkstemp(suffix=".md")
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path


class ExtractTests(unittest.TestCase):
    def setUp(self):
        self._tmp = []
        self.addCleanup(self._cleanup)

    def _cleanup(self):
        for p in self._tmp:
            try:
                os.remove(p)
            except OSError:
                pass

    def _write(self, content):
        path = write_md(content)
        self._tmp.append(path)
        return path

    def test_valid_returns_one_example(self):
        examples = validate.extract(self._write(VALID))
        self.assertEqual(len(examples), 1)
        ts, umd = examples[0]
        self.assertIn("actions.v2.", ts)
        self.assertIn("actions.v2.", umd)
        self.assertNotIn("<script", umd)  # inner JS only

    def test_region_isolation_ignores_outside_blocks(self):
        # a ```ts block OUTSIDE the tabs region must not be counted
        md = "```ts\nconst ignored = true\n```\n\n" + VALID
        examples = validate.extract(self._write(md))
        self.assertEqual(len(examples), 1)
        self.assertIn("crm.lead.add", examples[0][0])

    def test_multiregion_skips_param_block(self):
        # first tabs block is a parameter description (no ```ts); only the code-example
        # block is validated — extract returns exactly one example, the code one.
        examples = validate.extract(self._write(MULTIREGION))
        self.assertEqual(len(examples), 1)
        ts, umd = examples[0]
        self.assertIn("crm.lead.add", ts)
        self.assertIn("actions.v2.", umd)

    def test_two_code_regions_both_validated(self):
        # a page with two separate code-example blocks -> BOTH are validated and returned
        body = VALID.split("# Page\n\n", 1)[1]
        examples = validate.extract(
            self._write("# Page\n\n## One\n\n" + body + "\n## Two\n\n" + body))
        self.assertEqual(len(examples), 2)
        for ts, umd in examples:
            self.assertIn("actions.v2.", ts)
            self.assertIn("actions.v2.", umd)

    def _assert_fail(self, content):
        with self.assertRaises(SystemExit):
            validate.extract(self._write(content))

    def _assert_fail_msg(self, content, substr):
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with self.assertRaises(SystemExit), redirect_stdout(buf):
            validate.extract(self._write(content))
        self.assertIn(substr, buf.getvalue())

    def test_tabs_wrapper_without_ts_fence_fails_clearly(self):
        # {% list tabs %} with - TS/- UMD labels but only prose (no ```ts) -> no code
        # region -> clear, specific failure message
        md = ("# Page\n\n{% list tabs %}\n\n- TS\n\nprose, not code\n\n"
              "- UMD\n\nstill prose\n\n{% endlist %}\n")
        self._assert_fail_msg(md, "no {% list tabs %} region with a")

    def test_per_region_error_names_the_failing_region(self):
        # valid first code region + a second one with a stray extra ```ts ->
        # the failure is attributed to "code region 2/2"
        body = VALID.split("# Page\n\n", 1)[1]
        bad = body.replace("{% endlist %}", "```ts\nconst x = 1\n```\n\n{% endlist %}", 1)
        self._assert_fail_msg("# Page\n\n## One\n\n" + body + "\n## Two\n\n" + bad,
                              "code region 2/2")

    def test_legacy_js_tab(self):
        self._assert_fail(VALID.replace("- TS\n", "- JS\n\n```js\nx\n```\n\n- TS\n", 1))

    def test_missing_ts_tab(self):
        self._assert_fail(VALID.replace("- TS\n", "", 1))

    def test_missing_umd_tab(self):
        self._assert_fail(VALID.replace("- UMD\n", "", 1))

    def test_new_tab_labels_pass(self):
        # canonical doc-team labels "JS (TS)" / "JS (UMD)" are accepted (VALID uses the legacy
        # "TS" / "UMD"); code is extracted by fence language, not by the tab label
        md = VALID.replace("- TS\n", "- JS (TS)\n", 1).replace("- UMD\n", "- JS (UMD)\n", 1)
        examples = validate.extract(self._write(md))
        self.assertEqual(len(examples), 1)
        self.assertIn("actions.v2.", examples[0][0])

    def test_new_label_missing_umd_fails(self):
        # JS (TS) present but neither "JS (UMD)" nor legacy "UMD" -> fail
        md = VALID.replace("- TS\n", "- JS (TS)\n", 1).replace("- UMD\n", "", 1)
        self._assert_fail(md)

    def test_two_ts_blocks(self):
        self._assert_fail(VALID.replace("{% endlist %}", "```ts\nconst x = 1\n```\n\n{% endlist %}"))

    def test_two_html_blocks(self):
        self._assert_fail(VALID.replace(
            "{% endlist %}", "```html\n<script>const x = 1</script>\n```\n\n{% endlist %}"))

    def test_no_tabs_region(self):
        # tab names present but no {% list tabs %} … {% endlist %} wrapper
        self._assert_fail("# Page\n\n- TS\n- UMD\n\n```ts\nconst r = 1\n```\n")

    def test_umd_script_without_logic(self):
        # an html block whose only <script> is the external src (no inline body) must fail
        self._assert_fail(
            "# Page\n\n{% list tabs %}\n\n- TS\n\n"
            "```ts\nconst r = await $b24.actions.v2.call.make({ method: 'x', params: {} })\n```\n\n"
            "- UMD\n\n```html\n"
            '<script src="https://unpkg.com/@bitrix24/b24jssdk@1/dist/umd/index.min.js"></script>\n'
            "```\n\n{% endlist %}\n")

    def test_forbidden_token(self):
        self._assert_fail(VALID.replace("actions.v2.call.make", "callMethod", 1))

    def test_all_forbidden_tokens(self):
        # every banned token must trip extract(), not just callMethod
        for banned in validate.FORBIDDEN:
            with self.subTest(token=banned):
                # inject the token as a comment line inside the TS block
                bad = VALID.replace("declare const $b24: B24Frame",
                                    f"declare const $b24: B24Frame\n// {banned}()", 1)
                self._assert_fail(bad)

    def test_v3_accepted(self):
        # actions.v3 must be accepted just like v2
        ts, umd = validate.extract(self._write(VALID.replace("actions.v2.", "actions.v3.")))[0]
        self.assertIn("actions.v3.", ts)
        self.assertIn("actions.v3.", umd)

    def test_ts_without_actions(self):
        self._assert_fail(replace_nth(VALID, "$b24.actions.v2.call.make", "$b24.callApi", 1))

    def test_umd_without_actions(self):
        self._assert_fail(replace_nth(VALID, "$b24.actions.v2.call.make", "$b24.callApi", 2))

    # --- template-uniformity (comment + code-style) checks -------------------
    def test_styled_fixture_passes_style(self):
        examples = validate.extract(self._write(STYLED))
        self.assertEqual(len(examples), 1)

    def test_missing_guard_comment_fails(self):
        # remove the UMD success-guard comment (4-space indent, unique to UMD)
        bad = STYLED.replace(
            "    // The payload is available only on a successful response\n", "", 1)
        self._assert_fail_msg(bad, "before `if (!response.isSuccess)`")

    def test_missing_init_comment_fails(self):
        bad = STYLED.replace(
            "    // Initialize the SDK inside a Bitrix24 frame\n", "", 1)
        self._assert_fail_msg(bad, "initializeB24Frame")

    def test_missing_catch_comment_fails(self):
        bad = STYLED.replace(
            "    // Thrown on transport or SDK failures (AjaxError, SdkError, etc.)\n", "", 1)
        self._assert_fail_msg(bad, "first line of the catch block")

    def test_trailing_comma_after_requestid_fails(self):
        bad = STYLED.replace(
            "requestId: Text.getUuidRfc4122()", "requestId: Text.getUuidRfc4122(),", 1)
        self._assert_fail_msg(bad, "trailing comma after `requestId`")

    def test_style_errors_flags_main_type_without_shape(self):
        code = ("type DemoResult = {\n  id: number\n}\n"
                "const r = await $b24.actions.v2.call.make<DemoResult>("
                "{ method: 'm', params: {}, requestId: Text.getUuidRfc4122() })\n")
        self.assertTrue(any("main result type" in e for e in validate.style_errors(code)))

    def test_style_errors_exempts_helper_types(self):
        # a second type that is NOT used as a .make<X> generic needs no Shape comment
        code = ('// Shape of the payload returned in result (x)\n'
                "type DemoResult = {\n  id: number\n}\n"
                "type Helper = {\n  x: number\n}\n"
                "const r = await $b24.actions.v2.call.make<DemoResult>("
                "{ method: 'm', params: {}, requestId: Text.getUuidRfc4122() })\n")
        self.assertEqual(validate.style_errors(code), [])

    def test_style_errors_flags_list_main_type_without_shape(self):
        # regression: the old `\.make<(\w+)>` regex missed the list-generic `make<X[]>`,
        # silently skipping the Shape check on every list method. It must be flagged now.
        code = ("type UserItem = {\n  id: number\n}\n"
                "const r = await $b24.actions.v2.callList.make<UserItem[]>("
                "{ method: 'm', params: {}, requestId: Text.getUuidRfc4122() })\n")
        self.assertTrue(any("main result type" in e for e in validate.style_errors(code)))

    def test_style_errors_accepts_list_element_shape_wording(self):
        # for a list method the element-form Shape comment is accepted, not only the object form
        code = ("// Shape of each user returned in result[]\n"
                "type UserItem = {\n  id: number\n}\n"
                "const r = await $b24.actions.v2.callList.make<UserItem[]>("
                "{ method: 'm', params: {}, requestId: Text.getUuidRfc4122() })\n")
        self.assertEqual(validate.style_errors(code), [])

    def test_style_errors_rejects_typo_shape_wording(self):
        # SHAPE_RE anchors on `result\b`: a pluralised/typo tail ("results[]") must NOT satisfy it
        code = ("// Shape of each user returned in results[]\n"
                "type UserItem = {\n  id: number\n}\n"
                "const r = await $b24.actions.v2.callList.make<UserItem[]>("
                "{ method: 'm', params: {}, requestId: Text.getUuidRfc4122() })\n")
        self.assertTrue(any("main result type" in e for e in validate.style_errors(code)))

    def test_style_errors_object_form_still_accepted(self):
        # the object form (make<X>, "… the payload …" with a trailing parenthetical) still passes
        code = ("// Shape of the payload returned in result (match the page)\n"
                "type DemoResult = {\n  id: number\n}\n"
                "const r = await $b24.actions.v2.call.make<DemoResult>("
                "{ method: 'm', params: {}, requestId: Text.getUuidRfc4122() })\n")
        self.assertEqual(validate.style_errors(code), [])

    def test_has_legacy_js_tab_only_inside_tabs(self):
        # a prose "- JS" bullet must NOT count; only a "- JS" tab inside {% list tabs %} does
        self.assertFalse(validate._has_legacy_js_tab("intro\n- JS\n- PHP\n\nmore prose\n"))
        self.assertTrue(validate._has_legacy_js_tab(
            "{% list tabs %}\n- JS\n\n```ts\nx\n```\n{% endlist %}"))

    def test_extract_ignores_prose_js_bullet(self):
        # a prose "- JS" line elsewhere on the page must not trip the legacy-tab check
        md = VALID.replace("# Page\n", "# Page\n\nLanguages:\n- JS\n- PHP\n")
        self.assertEqual(len(validate.extract(self._write(md))), 1)

    def test_extract_accepts_python_tab(self):
        # a b24pysdk "- Python" tab (```python) alongside the JS tabs must not affect validation
        py_tab = "\n- Python\n\n```python\nresult = b24.call('crm.lead.add')\n```\n"
        md = VALID.replace("\n{% endlist %}", py_tab + "\n{% endlist %}")
        self.assertEqual(len(validate.extract(self._write(md))), 1)

    def test_main_result_types_keeps_named_generics_only(self):
        # named (incl. primitives) kept; inline-literal, multi-type excluded; spaces tolerated
        code = ("type Foo = {}\n .make<Foo>(1) .make<Foo[]>(1) .make<number[]>(1) "
                ".make<{ a: 1 }>(1) .make<Foo, Bar>(1) .make< Spaced[] >(1)")
        self.assertEqual(validate.main_result_types(code), {"Foo", "number", "Spaced"})

    def test_shape_coverage_splits_checked_and_uncovered(self):
        code = ("type Foo = {\n  id: number\n}\n"
                "const a = x.make<Foo[]>(1)\n"
                "const b = x.make<number[]>(1)\n"
                "const c = x.make<{ a: 1 }>(1)\n"
                "const d = x.make<Foo, Bar>(1)\n")
        checked, uncovered = validate.shape_coverage(code)
        self.assertEqual(checked, {"Foo"})
        self.assertIn("number[]", uncovered)
        self.assertIn("Foo, Bar", uncovered)            # multi-type generic surfaced, not skipped
        self.assertTrue(any("{" in u for u in uncovered))


class HelperTests(unittest.TestCase):
    def test_replace_nth_targets_only_the_nth(self):
        self.assertEqual(replace_nth("a-a-a", "a", "X", 2), "a-X-a")

    def test_replace_nth_out_of_range_is_noop(self):
        # fewer than n occurrences -> original string returned unchanged
        self.assertEqual(replace_nth("a-a", "a", "X", 5), "a-a")

    def test_replace_nth_zero_is_noop(self):
        self.assertEqual(replace_nth("a-a-a", "a", "X", 0), "a-a-a")


class CleanTests(unittest.TestCase):
    def test_tabs_and_newlines_collapsed(self):
        self.assertEqual(record.clean("a\tb\nc\r\nd"), "a b c d")

    def test_default_limit_200(self):
        self.assertEqual(len(record.clean("x" * 500)), 200)

    def test_custom_limit(self):
        self.assertEqual(record.clean("x" * 50, 20), "x" * 20)

    def test_none_does_not_crash(self):
        self.assertEqual(record.clean(None), "None")


class TabsTests(unittest.TestCase):
    def test_tabs_region_first_only(self):
        text = "{% list tabs %}A{% endlist %}\n{% list tabs %}B{% endlist %}"
        self.assertEqual(_tabs.tabs_region(text), "A")

    def test_tabs_region_none(self):
        self.assertIsNone(_tabs.tabs_region("no tabs here"))

    def test_first_method_single_quote(self):
        self.assertEqual(_tabs.first_method("method: 'crm.lead.add'"), "crm.lead.add")

    def test_first_method_double_quote(self):
        self.assertEqual(_tabs.first_method('method: "tasks.task.get"'), "tasks.task.get")

    def test_code_regions_picks_only_ts_bearing(self):
        text = ("{% list tabs %}\n- a\n\nprose only\n{% endlist %}\n"
                "{% list tabs %}\n- TS\n\n```ts\nmethod: 'crm.lead.add'\n```\n{% endlist %}")
        regions = _tabs.code_regions(text)
        self.assertEqual(len(regions), 1)
        self.assertIn("crm.lead.add", regions[0])

    def test_code_regions_empty_when_no_ts(self):
        self.assertEqual(_tabs.code_regions("{% list tabs %}\n- a\n\nprose\n{% endlist %}"), [])

    def test_code_regions_returns_every_code_block(self):
        block = "{% list tabs %}\n- TS\n\n```ts\nx\n```\n{% endlist %}"
        self.assertEqual(len(_tabs.code_regions(block + "\n" + block)), 2)


def _page(method_ts, method_umd, type_body, curl="crm.deal.get",
          result_json='{ "result": { "ID": "1", "TITLE": "x" } }'):
    """A minimal but realistic method page for the cross-check tests: one code region with
    cURL + JS (TS) + JS (UMD) tabs (the UMD block carries the real two-<script> shape: CDN loader
    + logic), and a JSON response block. `curl=None` omits the cURL tab; `result_json=None` omits
    the response section (=> empty field universe); `method_ts=None` omits the TS `method:` (so the
    SDK method falls back to the UMD tab)."""
    ts_arg = "{ }" if method_ts is None else f"{{ method: '{method_ts}' }}"
    curl_tab = "" if curl is None else (
        "- cURL (Webhook)\n\n"
        "    ```bash\n"
        f"    curl -X POST -d '{{}}' https://**x**/rest/**u**/**w**/{curl}\n"
        "    ```\n\n")
    resp = "" if result_json is None else f"\n## Обработка ответа\n\n```json\n{result_json}\n```\n"
    return (
        "# Page\n\n{% list tabs %}\n\n"
        f"{curl_tab}"
        "- JS (TS)\n\n"
        "    ```ts\n"
        f"    type DealResult = {{\n{type_body}\n    }}\n"
        f"    const r = await $b24.actions.v2.call.make<DealResult>({ts_arg})\n"
        "    ```\n\n"
        "- JS (UMD)\n\n"
        "    ```html\n"
        '    <script src="https://unpkg.com/@bitrix24/b24jssdk@1/dist/umd/index.min.js"></script>\n'
        "    <script>\n"
        f"    const r = await $b24.actions.v2.call.make({{ method: '{method_umd}' }})\n"
        "    </script>\n"
        "    ```\n\n"
        "{% endlist %}\n"
        f"{resp}")


class CrossCheckParseTests(unittest.TestCase):
    def test_curl_methods_webhook_and_oauth(self):
        region = ("https://x/rest/**u**/**w**/calendar.section.get\n"
                  "https://x/rest/calendar.section.get")
        self.assertEqual(validate.curl_methods(region), {"calendar.section.get"})

    def test_curl_methods_strips_json_suffix(self):
        self.assertEqual(validate.curl_methods("https://x/rest/a/b/ai.engine.register.json"),
                         {"ai.engine.register"})

    def test_curl_methods_dotted_and_multiple(self):
        region = "/rest/x/y/calendar.event.get.nearest\n/rest/crm.deal.add"
        self.assertEqual(validate.curl_methods(region),
                         {"calendar.event.get.nearest", "crm.deal.add"})

    def test_curl_methods_none(self):
        self.assertEqual(validate.curl_methods("no rest url here"), set())

    def test_type_body_keys_nested_and_scoped(self):
        ts = ("type X = {\n"
              "  ID: string\n"
              "  PERM: {\n"
              "    view: boolean\n"
              "  }\n"
              "}\n"
              "const r = await call.make<X>({ method: 'm', params: { ownerId: 1, start: 0 } })")
        # nested key kept; request-side params (ownerId/start/method) excluded
        self.assertEqual(validate.type_body_keys(ts), {"ID", "PERM", "view"})

    def test_type_body_keys_scalar_alias_has_none(self):
        self.assertEqual(validate.type_body_keys("type Ok = boolean"), set())

    def test_documented_field_names_json_and_table(self):
        page = ('```json\n{ "result": { "ID": "1" }, "time": { "start": 1 } }\n```\n'
                "|| **TITLE**\n`string` | desc ||\n"
                "|| **Название** | header (cyrillic, excluded) ||")
        names = validate.documented_field_names(page)
        self.assertIn("ID", names)
        self.assertIn("TITLE", names)
        self.assertNotIn("Название", names)

    def test_curl_methods_strips_json_suffix_oauth(self):
        # OAuth form (no webhook segments) with a trailing .json is also stripped
        self.assertEqual(validate.curl_methods("https://x/rest/ai.engine.register.json"),
                         {"ai.engine.register"})

    def test_curl_methods_real_webhook_placeholder_format(self):
        # the exact shape the corpus uses: **put_your_..._here** placeholder segments
        url = ("https://**put_your_bitrix24**/rest/**put_your_user_id_here**/"
               "**put_your_webhook_here**/calendar.section.get")
        self.assertEqual(validate.curl_methods(url), {"calendar.section.get"})

    def test_curl_methods_ignores_query_and_fragment(self):
        # a trailing ?query or #fragment must not be glued onto the method name
        self.assertEqual(validate.curl_methods("/rest/x/y/crm.deal.add?foo=1"), {"crm.deal.add"})
        self.assertEqual(validate.curl_methods("/rest/x/y/crm.deal.add#anchor"), {"crm.deal.add"})

    def test_umd_inner_js_skips_cdn_loader_script(self):
        # the real two-<script> shape: empty CDN loader first, logic second -> logic returned
        html = ('<script src="https://unpkg.com/@bitrix24/b24jssdk@1/dist/umd/index.min.js">'
                "</script>\n<script>\nconst r = 1\n</script>")
        self.assertEqual(validate.umd_inner_js(html).strip(), "const r = 1")
        self.assertEqual(validate.umd_inner_js("<script></script>"), "")  # no body -> ''

    def test_type_body_keys_inline_nested_yields_outer_key_only(self):
        # an inline `{ … }` on a property line contributes the OUTER key only (documented gap)
        ts = "type X = {\n  id: string\n  addr: { city: string }\n}"
        self.assertEqual(validate.type_body_keys(ts), {"id", "addr"})

    def test_type_body_keys_key_on_opening_brace_line(self):
        # a key sharing the opening-brace line is captured, not skipped
        ts = "type X = { ID: string\n  NAME: string\n}"
        self.assertEqual(validate.type_body_keys(ts), {"ID", "NAME"})

    def test_type_body_keys_scoped_to_named_types(self):
        # only=… restricts collection to the named result type(s); helper types are ignored
        ts = ("type Helper = {\n  reqOnly: number\n}\n"
              "type DealResult = {\n  ID: string\n}\n")
        self.assertEqual(validate.type_body_keys(ts, only={"DealResult"}), {"ID"})
        self.assertEqual(validate.type_body_keys(ts), {"reqOnly", "ID"})  # None => every block

    def test_documented_field_names_includes_envelope_keys(self):
        # documents the generous-superset gap: response-envelope keys are always "documented"
        page = '```json\n{ "result": { "ID": "1" }, "time": { "start": 1 } }\n```'
        names = validate.documented_field_names(page)
        self.assertTrue({"result", "time", "start", "ID"} <= names)


class CrossCheckTests(unittest.TestCase):
    def test_clean_page_has_no_errors_or_notes(self):
        errs, notes = validate.cross_check(_page("crm.deal.get", "crm.deal.get",
                                                 "  ID: string\n  TITLE: string"))
        self.assertEqual((errs, notes), ([], []))

    def test_method_ts_umd_mismatch(self):
        errs, _ = validate.cross_check(_page("crm.deal.get", "crm.deal.update", "  ID: string"))
        self.assertTrue(any("method mismatch" in e for e in errs))

    def test_method_sdk_vs_curl_mismatch(self):
        errs, _ = validate.cross_check(_page("crm.deal.list", "crm.deal.list", "  ID: string",
                                             curl="crm.deal.get"))
        self.assertTrue(any("is not the cURL endpoint" in e for e in errs))

    def test_invented_field_with_universe_is_an_error(self):
        errs, notes = validate.cross_check(_page("crm.deal.get", "crm.deal.get",
                                                 "  ID: string\n  BOGUS: string"))
        self.assertEqual(notes, [])
        self.assertTrue(any("BOGUS" in e and "invented" in e for e in errs))

    def test_ungrounded_field_without_universe_is_a_note(self):
        # no response section => empty universe => report, do NOT gate
        errs, notes = validate.cross_check(_page("placement.getEvents", "placement.getEvents",
                                                 "  id: string", curl=None, result_json=None))
        self.assertEqual(errs, [])
        self.assertTrue(any("ungrounded" in n and "id" in n for n in notes))

    def test_no_curl_tab_skips_method_cross_check(self):
        # internal TS==UMD still holds; absent cURL endpoint must not fail
        errs, _ = validate.cross_check(_page("crm.deal.get", "crm.deal.get", "  ID: string",
                                             curl=None))
        self.assertEqual(errs, [])

    def test_region_isolation_each_method_matches_its_own_curl(self):
        page = (_page("crm.deal.get", "crm.deal.get", "  ID: string", curl="crm.deal.get")
                + _page("crm.deal.add", "crm.deal.add", "  ID: string", curl="crm.deal.add"))
        errs, _ = validate.cross_check(page)
        self.assertEqual(errs, [])

    def test_method_umd_only_vs_curl_mismatch(self):
        # TS tab carries no method: (sdk_m falls back to UMD) — the UMD method must still match cURL
        errs, _ = validate.cross_check(
            _page(None, "crm.deal.update", "  ID: string", curl="crm.deal.get"))
        self.assertTrue(any("is not the cURL endpoint" in e for e in errs))

    def test_region2_mismatch_attributed_to_region2(self):
        # region 1 clean, region 2 has a TS/UMD method mismatch -> the error names region 2
        page = (_page("crm.deal.get", "crm.deal.get", "  ID: string")
                + _page("crm.deal.get", "crm.deal.update", "  ID: string"))
        errs, _ = validate.cross_check(page)
        self.assertTrue(any("region 2" in e and "method mismatch" in e for e in errs))

    def test_method_mismatch_and_ungrounded_note_coexist(self):
        # an error (method mismatch) and a note (empty universe) can be produced together
        errs, notes = validate.cross_check(
            _page("crm.deal.get", "crm.deal.update", "  id: string", curl=None, result_json=None))
        self.assertTrue(errs and notes)
        self.assertTrue(any("method mismatch" in e for e in errs))
        self.assertTrue(any("ungrounded" in n for n in notes))

    def test_helper_type_not_used_as_generic_is_not_cross_checked(self):
        # a helper type's request-side key must NOT be grounded against the page (scoping fix):
        # categoryId is documented nowhere, yet the page is clean because Helper is not .make<>'d
        page = _page("crm.deal.get", "crm.deal.get", "  ID: string").replace(
            "    type DealResult = {",
            "    type Helper = {\n      categoryId: number\n    }\n    type DealResult = {", 1)
        self.assertEqual(validate.cross_check(page), ([], []))

    def test_record_result_type_does_not_false_fail(self):
        # PROMPT "Result type patterns": a result type `Record<string, Item>` has no {}-body, so its
        # keys are not scanned, and the helper `Item` is skipped (scoped to the make<X> name) — an
        # undocumented Item field is NOT flagged as invented. Mirrors *.fields / localization maps.
        page = _page("crm.deal.get", "crm.deal.get", "  ID: string").replace(
            "    type DealResult = {\n  ID: string\n    }\n"
            "    const r = await $b24.actions.v2.call.make<DealResult>(",
            "    type FieldItem = {\n      undocumentedKey: string\n    }\n"
            "    type CurrencyResult = Record<string, FieldItem>\n"
            "    const r = await $b24.actions.v2.call.make<CurrencyResult>(", 1)
        self.assertEqual(validate.cross_check(page), ([], []))

    def test_field_grounded_by_table_only(self):
        # universe populated from a `|| **field** ||` table alone (no JSON block) still grounds
        page = _page("crm.deal.get", "crm.deal.get", "  TITLE: string", result_json=None)
        page += "\n#|\n|| **Поле** | Описание ||\n|| **TITLE***\n`string` | name ||\n|#\n"
        self.assertEqual(validate.cross_check(page), ([], []))


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__("shutil").rmtree(self.tmp, ignore_errors=True))
        for attr, val in (("REPO", self.tmp), ("LEDGER", os.path.join(self.tmp, "ledger.tsv"))):
            p = mock.patch.object(record, attr, val)
            p.start()
            self.addCleanup(p.stop)

    def _md(self, name, method="crm.lead.add"):
        path = os.path.join(self.tmp, name)
        body = ("{% list tabs %}\n- TS\n\n```ts\nmethod: 'METHOD'\n```\n"
                "{% endlist %}\n").replace("METHOD", method)
        with open(path, "w") as f:
            f.write(body)
        return path

    def test_upsert_idempotent(self):
        p = self._md("a.md")
        record.upsert(p, "done")
        record.upsert(p, "done")
        self.assertEqual(len(record.load()), 1)

    def test_upsert_updates_status_and_method(self):
        p = self._md("a.md", method="tasks.task.get")
        record.upsert(p, "done")
        record.upsert(p, "reviewed")
        rows = record.load()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][3], "reviewed")
        self.assertEqual(rows[0][4], "tasks.task.get")

    def test_upsert_sorted_by_file(self):
        record.upsert(self._md("b.md"), "done")
        record.upsert(self._md("a.md"), "done")
        files = [r[1] for r in record.load()]
        self.assertEqual(files, sorted(files))

    def test_upsert_rejects_path_outside_repo(self):
        with self.assertRaises(SystemExit):
            record.upsert("/etc/hostname", "done")

    def test_load_dedup_last_wins(self):
        with open(record.LEDGER, "w") as f:
            f.write("date\tfile\tsha256\tstatus\tmethod\n")
            f.write("d1\ta.md\taaa\tdone\tm\n")
            f.write("d2\ta.md\tbbb\treviewed\tm\n")
        rows = record.load()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][2], "bbb")

    def test_verify_empty_ledger_exit_0(self):
        with self.assertRaises(SystemExit) as e:
            record.verify()
        self.assertEqual(e.exception.code, 0)

    def test_verify_ok(self):
        record.upsert(self._md("a.md"), "done")
        with self.assertRaises(SystemExit) as e:
            record.verify()
        self.assertEqual(e.exception.code, 0)

    def test_verify_missing(self):
        p = self._md("a.md")
        record.upsert(p, "done")
        os.remove(p)
        with self.assertRaises(SystemExit) as e:
            record.verify()
        self.assertEqual(e.exception.code, 1)

    def test_verify_drift(self):
        p = self._md("a.md")
        record.upsert(p, "done")
        with open(p, "a") as f:
            f.write("\nmutated\n")
        with self.assertRaises(SystemExit) as e:
            record.verify()
        self.assertEqual(e.exception.code, 1)

    def test_detect_method_fallback_basename(self):
        path = os.path.join(self.tmp, "no-method.md")
        with open(path, "w") as f:
            f.write("plain text, no tabs, no method")
        self.assertEqual(record.detect_method(path), "no-method.md")

    def test_detect_method_from_tabs(self):
        self.assertEqual(
            record.detect_method(self._md("m.md", method="tasks.task.list")),
            "tasks.task.list")

    def test_detect_method_multiregion_uses_code_region(self):
        # decoy method in the first (parameter) block; real method in the code block
        path = os.path.join(self.tmp, "multi.md")
        with open(path, "w") as f:
            f.write("{% list tabs %}\n- a\n\nsee method: 'WRONG.decoy'\n{% endlist %}\n"
                    "{% list tabs %}\n- TS\n\n```ts\nmethod: 'tasks.task.list'\n```\n{% endlist %}\n")
        self.assertEqual(record.detect_method(path), "tasks.task.list")

    def test_detect_method_from_bare_text_fallback(self):
        # no {% list tabs %} at all, but a bare method: '…' in the prose -> fallback finds it
        path = os.path.join(self.tmp, "bare.md")
        with open(path, "w") as f:
            f.write("Some prose. method: 'foo.bar' somewhere in the body.\n")
        self.assertEqual(record.detect_method(path), "foo.bar")


class RemainingTests(unittest.TestCase):
    def test_legacy_regex_matches_deprecated(self):
        self.assertTrue(remaining.LEGACY.search("await $b24.callMethod('x')"))
        self.assertTrue(remaining.LEGACY.search("$b24.callListMethod('x')"))
        self.assertTrue(remaining.LEGACY.search("$b24.fetchListMethod('x')"))

    def test_legacy_regex_ignores_bx24_and_actions(self):
        self.assertFalse(remaining.LEGACY.search("BX24.callMethod('x')"))
        self.assertFalse(remaining.LEGACY.search("$b24.actions.v2.call.make()"))
        self.assertFalse(remaining.LEGACY.search("$b24.callMethodExtra()"))  # word boundary

    def test_done_set(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__("shutil").rmtree(tmp, ignore_errors=True))
        ledger = os.path.join(tmp, "ledger.tsv")
        with open(ledger, "w") as f:
            f.write("date\tfile\tsha256\tstatus\tmethod\n")
            f.write("d\tx/a.md\tsha\tdone\tm\n")
            f.write("d\tx/b.md\tsha\tpending\tm\n")
            f.write("d\tx/c.md\tsha\treviewed\tm\n")
        with mock.patch.object(remaining, "LEDGER", ledger):
            done = remaining.done_set()
        self.assertIn("x/a.md", done)          # done counts
        self.assertIn("x/c.md", done)          # reviewed counts too (DONE set)
        self.assertNotIn("x/b.md", done)       # pending does not


class ValidateCliGuardTests(unittest.TestCase):
    """validate.py main() refuses paths outside the repo (the guard is in main(),
    not extract(), so exercise it via the CLI)."""

    def test_path_outside_repo_rejected(self):
        import subprocess
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script = os.path.join(here, "validate.py")
        r = subprocess.run(
            [sys.executable, script, "/etc/hostname"],
            capture_output=True, text=True, timeout=30,
        )
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("outside the repository", r.stdout + r.stderr)


class ValidateMainTests(unittest.TestCase):
    def _run_main(self, path):
        with mock.patch.object(sys, "argv", ["validate.py", path]):
            with self.assertRaises(SystemExit) as e:
                validate.main()
        return e.exception.code

    def test_main_rejects_path_outside_repo(self):
        # the path-guard runs before any npm/tsc work, so this needs no toolchain
        self.assertEqual(self._run_main("/etc/hostname"), 1)

    def test_main_file_not_found(self):
        missing = os.path.join(validate.REPO, "definitely-missing-xyz-123.md")
        self.assertEqual(self._run_main(missing), 1)

    def test_main_multiregion_compiles_each_example(self):
        # a 2-code-region page must invoke the toolchain for BOTH examples
        # (tsc + node per example = 4 subprocess calls), with tsc/node mocked green.
        import shutil
        body = VALID.split("# Page\n\n", 1)[1]
        two = "# Page\n\n## One\n\n" + body + "\n## Two\n\n" + body
        path = os.path.join(validate.REPO, "._tmp_multiregion_main_test.md")
        with open(path, "w") as f:
            f.write(two)
        self.addCleanup(lambda: os.path.exists(path) and os.remove(path))
        proj = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(proj, ignore_errors=True))
        green = mock.Mock(returncode=0, stdout="", stderr="")
        with mock.patch.object(sys, "argv", ["validate.py", path, "--project", proj]), \
                mock.patch.object(validate, "ensure_project"), \
                mock.patch.object(validate.subprocess, "run", return_value=green) as run:
            with self.assertRaises(SystemExit) as e:
                validate.main()
        self.assertEqual(e.exception.code, 0)
        self.assertEqual(run.call_count, 4)  # 2 examples x (tsc + node)

    def _run_main_capture_stderr(self, md):
        # run main() over `md` with the toolchain mocked green, returning captured stderr
        import io, shutil
        from contextlib import redirect_stderr
        path = os.path.join(validate.REPO, "._tmp_obs_test.md")
        with open(path, "w") as f:
            f.write(md)
        self.addCleanup(lambda: os.path.exists(path) and os.remove(path))
        proj = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(proj, ignore_errors=True))
        green = mock.Mock(returncode=0, stdout="", stderr="")
        buf = io.StringIO()
        with mock.patch.object(sys, "argv", ["validate.py", path, "--project", proj]), \
                mock.patch.object(validate, "ensure_project"), \
                mock.patch.object(validate.subprocess, "run", return_value=green), \
                redirect_stderr(buf):
            with self.assertRaises(SystemExit) as e:
                validate.main()
        self.assertEqual(e.exception.code, 0)
        return buf.getvalue()

    def test_main_observability_reports_checked_count(self):
        # STYLED uses .make<DemoResult> with a local `type DemoResult` -> the Shape check sees it
        err = self._run_main_capture_stderr(STYLED)
        self.assertIn("[validate] Shape: 1 named result type(s) checked (DemoResult)", err)

    def test_main_observability_notes_uncovered_generic(self):
        # a make<number[]> generic has no local alias -> surfaced in the NOTICE, never silently skipped
        md = VALID.replace("call.make(", "call.make<number[]>(", 1)
        err = self._run_main_capture_stderr(md)
        self.assertIn("[validate] note:", err)
        self.assertIn("number[]", err)

    def test_main_primitive_boolean_generic_passes_with_na_note(self):
        # PROMPT "Result type patterns": a primitive make<boolean> (no local type, no Shape comment)
        # must PASS end-to-end — surfaced as the advisory "Shape check N/A" note, not a failure.
        # _run_main_capture_stderr asserts exit code 0 internally, so this also proves cross_check
        # and style_errors do not reject a bare primitive generic.
        md = VALID.replace("call.make(", "call.make<boolean>(", 1)
        err = self._run_main_capture_stderr(md)
        self.assertIn("[validate] note:", err)
        self.assertIn("boolean", err)


class FixtureAnchorTests(unittest.TestCase):
    # guards the substring anchors the replace-based ExtractTests rely on, so a
    # future VALID edit that drops one fails loudly instead of silently no-op'ing
    def test_valid_fixture_has_expected_anchors(self):
        for anchor in ("# Page\n\n", "- TS\n", "- UMD\n", "{% endlist %}", "actions.v2.call.make"):
            self.assertIn(anchor, VALID)
        self.assertEqual(VALID.count("$b24.actions.v2.call.make"), 2)

    def test_multiregion_fixture_shape(self):
        self.assertEqual(MULTIREGION.count("{% list tabs %}"), 2)
        self.assertEqual(len(_tabs.code_regions(MULTIREGION)), 1)  # only the code block has ```ts

    def test_styled_fixture_is_template_compliant(self):
        for c in (validate.GUARD_COMMENT, validate.INIT_COMMENT,
                  validate.CATCH_COMMENT, validate.SHAPE_COMMENT):
            self.assertIn(c, STYLED)
        self.assertIn(".make<DemoResult>", STYLED)
        self.assertNotIn("getUuidRfc4122(),", STYLED)


class DocsConsistencyTests(unittest.TestCase):
    ACTUALIZE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _read(self, name):
        with open(os.path.join(self.ACTUALIZE, name), encoding="utf-8") as f:
            return f.read()

    def test_prompt_encodes_current_conventions(self):
        p = self._read("PROMPT.md")
        for token in ("Text.getUuidRfc4122()", "import type { B24Frame }",
                      "callList.make", "fetchList.make"):
            self.assertIn(token, p)

    def test_readme_in_sync_with_prompt(self):
        readme = self._read("README.md")
        self.assertIn("Text.getUuidRfc4122()", readme)
        # the deprecated getTotal() must not be recommended as the list pattern
        self.assertNotIn("for lists — `getTotal()`", readme)

    def test_validate_comment_constants_are_in_prompt(self):
        # validate.py enforces these exact strings; PROMPT.md must document the same canon,
        # so the enforced rule and the template the agents follow cannot drift apart
        p = self._read("PROMPT.md")
        for const in (validate.GUARD_COMMENT, validate.INIT_COMMENT,
                      validate.CATCH_COMMENT, validate.SHAPE_COMMENT):
            self.assertIn(const, p)
        # the list-method element form must also be documented so authors don't drift (PR #15)
        self.assertIn("Shape of each <item> returned in result[]", p)


if __name__ == "__main__":
    unittest.main()
