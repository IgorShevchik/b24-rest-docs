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
const $b24 = await B24Js.initializeB24Frame()
const r = await $b24.actions.v2.call.make({ method: 'crm.lead.add', params: {}, requestId: B24Js.Text.getUuidRfc4122() })
</script>
```

{% endlist %}
"""

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


if __name__ == "__main__":
    unittest.main()
