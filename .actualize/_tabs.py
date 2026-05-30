"""Shared parsing of the {% list tabs %} region and code blocks.

Single source of truth for the regexes so validate.py (which fails hard) and
record.py (which falls back gracefully) cannot drift apart. Only the FIRST
{% list tabs %} region is considered — these method pages have exactly one.
"""
import re

TABS_RE = re.compile(r"\{%\s*list tabs\s*%\}(.*?)\{%\s*endlist\s*%\}", re.DOTALL)
TS_RE = re.compile(r"(?m)^[ \t]*```ts\n(.*?)\n[ \t]*```", re.DOTALL)
HTML_RE = re.compile(r"(?m)^[ \t]*```html\n(.*?)\n[ \t]*```", re.DOTALL)
METHOD_RE = re.compile(r"""method:\s*['"]([^'"]+)['"]""")


def tabs_region(text):
    """Return the inside of the first {% list tabs %}…{% endlist %}, or None."""
    m = TABS_RE.search(text)
    return m.group(1) if m else None


def find_ts(region):
    return TS_RE.findall(region)


def find_html(region):
    return HTML_RE.findall(region)


def first_method(scope):
    """First REST method name (single or double quoted) in scope, or None."""
    m = METHOD_RE.search(scope)
    return m.group(1) if m else None
