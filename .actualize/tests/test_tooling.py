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
import { type B24Frame } from '@bitrix24/b24jssdk'
declare const $b24: B24Frame
const r = await $b24.actions.v2.call.make({ method: 'crm.lead.add', params: {} })
```

- UMD

```html
<script src="https://unpkg.com/@bitrix24/b24jssdk@1/dist/umd/index.min.js"></script>
<script>
const $b24 = await B24Js.initializeB24Frame()
const r = await $b24.actions.v2.call.make({ method: 'crm.lead.add', params: {} })
</script>
```

{% endlist %}
"""


def replace_nth(s, old, new, n):
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
    def test_valid_returns_ts_and_umd(self):
        ts, umd = validate.extract(write_md(VALID))
        self.assertIn("actions.v2.", ts)
        self.assertIn("actions.v2.", umd)
        self.assertNotIn("<script", umd)  # inner JS only

    def test_region_isolation_ignores_outside_blocks(self):
        # a ```ts block OUTSIDE the tabs region must not be counted
        md = "```ts\nconst ignored = true\n```\n\n" + VALID
        ts, _ = validate.extract(write_md(md))
        self.assertIn("crm.lead.add", ts)

    def _assert_fail(self, content):
        with self.assertRaises(SystemExit):
            validate.extract(write_md(content))

    def test_legacy_js_tab(self):
        self._assert_fail(VALID.replace("- TS\n", "- JS\n\n```js\nx\n```\n\n- TS\n", 1))

    def test_missing_ts_tab(self):
        self._assert_fail(VALID.replace("- TS\n", "", 1))

    def test_two_ts_blocks(self):
        self._assert_fail(VALID.replace("{% endlist %}", "```ts\nconst x = 1\n```\n\n{% endlist %}"))

    def test_forbidden_token(self):
        self._assert_fail(VALID.replace("actions.v2.call.make", "callMethod", 1))

    def test_ts_without_actions(self):
        self._assert_fail(replace_nth(VALID, "$b24.actions.v2.call.make", "$b24.callApi", 1))

    def test_umd_without_actions(self):
        self._assert_fail(replace_nth(VALID, "$b24.actions.v2.call.make", "$b24.callApi", 2))


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
        with mock.patch.object(remaining, "LEDGER", ledger):
            done = remaining.done_set()
        self.assertIn("x/a.md", done)
        self.assertNotIn("x/b.md", done)


if __name__ == "__main__":
    unittest.main()
