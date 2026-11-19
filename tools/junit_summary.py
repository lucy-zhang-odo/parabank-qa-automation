"""Report JUnit XML results in GitHub Actions:
- a Markdown table in the job summary ($GITHUB_STEP_SUMMARY, or stdout when run locally)
- an error annotation for each failed test, so the reason is visible on the run page and on PRs
"""
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def one_line(text: str, limit: int = 300) -> str:
    text = " ".join((text or "").split())
    return text[:limit] + ("..." if len(text) > limit else "")


rows, failed = [], []
for path in sys.argv[1:]:
    p = Path(path)
    if not p.exists():
        rows.append(f"| {p.stem} | not run | | | | |")
        continue
    for suite in ET.parse(p).getroot().iter("testsuite"):
        total = int(suite.get("tests", 0))
        fail = int(suite.get("failures", 0)) + int(suite.get("errors", 0))
        skipped = int(suite.get("skipped", 0))   # includes expected failures (known defects)
        rows.append(f"| {p.stem} | {total} | {total - fail - skipped} | {fail} | {skipped} | {float(suite.get('time', 0)):.0f} s |")
        for case in suite.iter("testcase"):
            bad = case.find("failure") if case.find("failure") is not None else case.find("error")
            if bad is not None:
                name = f"{case.get('classname')}::{case.get('name')}"
                reason = one_line(bad.get("message") or bad.text)
                failed.append((name, reason))

lines = ["## Test results", "",
         "| Suite | Total | Passed | Failed | Skipped / known defects | Time |",
         "|---|---|---|---|---|---|", *rows]
if failed:
    lines += ["", "### Failed", ""] + [f"- `{n}`: {r}" for n, r in failed]
lines += ["", "Reports and Playwright traces of failed tests are in the `test-reports` artifact."]

summary = os.environ.get("GITHUB_STEP_SUMMARY")
if summary:
    with open(summary, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    for name, reason in failed:
        print(f"::error title={name}::{reason}")
else:
    print("\n".join(lines))
