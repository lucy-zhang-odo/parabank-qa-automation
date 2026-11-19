"""Print a Markdown summary of JUnit XML files (used for the GitHub Actions job summary)."""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

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
            if case.find("failure") is not None or case.find("error") is not None:
                failed.append(f"- `{case.get('classname')}::{case.get('name')}`")

print("## Test results\n")
print("| Suite | Total | Passed | Failed | Skipped / known defects | Time |")
print("|---|---|---|---|---|---|")
print("\n".join(rows))
if failed:
    print("\n### Failed\n")
    print("\n".join(failed))
print("\nReports and Playwright traces of failed tests are in the `test-reports` artifact.")
