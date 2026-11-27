"""Smoke test: run Home and every page headlessly with Streamlit's AppTest.

Fails (exit 1) if any page raises an exception on first load or after changing
its first selectbox. Also prints deprecation warnings, and runs an informational
"missing file" check that never fails the build.

Run from the repo root:  python tests/smoke_test.py
"""
import logging
import os
import shutil
import sys
import tempfile
import warnings

from streamlit.testing.v1 import AppTest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ["home.py", "pages/1_Team.py", "pages/2_Statistics.py",
         "pages/3_Champ_Historic.py", "pages/4_Trade_Machine.py"]

# One file each page reads, removed in the informational resilience check.
MISSING_FILE_CASES = {
    "home.py": "flat_table/flat_awards.csv",
    "pages/1_Team.py": "flat_table/flat_east_standing.csv",
    "pages/2_Statistics.py": "flat_table/flat_po_player.csv",
    "pages/3_Champ_Historic.py": "data/df_nba_champion.xlsx",
    "pages/4_Trade_Machine.py": "data/df_nba_players_salaries.xlsx",
}


def annotate(level, msg):
    """Also surface a line as a GitHub Actions annotation (visible on the run page)."""
    if os.environ.get("GITHUB_ACTIONS"):
        clean = msg.replace("%", "%25").replace("\r", "").replace("\n", "%0A")
        print(f"::{level}::{clean[:1000]}")


class Collect(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING)
        self.lines = []

    def emit(self, record):
        self.lines.append(record.getMessage())


def run_page(root, page):
    """Start from home.py (the real entrypoint, as on Streamlit Cloud), then open `page`."""
    os.chdir(root)
    at = AppTest.from_file(os.path.join(root, "home.py"), default_timeout=180)
    at.run()
    if page != "home.py":
        at.switch_page(page).run()
    return at


def main():
    sys.path.insert(0, ROOT)
    handler = Collect()
    logging.getLogger().addHandler(handler)
    logging.getLogger("streamlit").addHandler(handler)
    failures = 0

    print("=== Normal load ===")
    for page in PAGES:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            at = run_page(ROOT, page)
            excs = [str(e.value) for e in at.exception]
            # Interact: pick the last option of the first selectbox, if any.
            if not excs and len(at.selectbox) > 0 and at.selectbox[0].options:
                at.selectbox[0].select(at.selectbox[0].options[-1]).run()
                excs += [f"(after selectbox change) {e.value}" for e in at.exception]
        status = "OK" if not excs else "FAIL"
        failures += bool(excs)
        print(f"[{status}] {page}: exceptions={len(excs)} st.error={len(at.error)} "
              f"selectboxes={len(at.selectbox)}")
        for e in excs:
            print("    EXCEPTION:", e[:500])
            annotate("error", f"{page}: {e}")
        for w in {f"{w.category.__name__}: {w.message}" for w in caught
                  if issubclass(w.category, (DeprecationWarning, FutureWarning))}:
            print("    WARNING:", w[:300])
            annotate("warning", f"{page}: {w}")

    print("\n=== Deprecation / warning log lines (deduplicated) ===")
    for line in sorted({l[:300] for l in handler.lines if "ScriptRunContext" not in l}):
        print("   ", line)
        annotate("warning", f"log: {line}")

    print("\n=== Resilience: one input file missing (informational, never fails) ===")
    for page, rel in MISSING_FILE_CASES.items():
        tmp = tempfile.mkdtemp()
        try:
            copy = os.path.join(tmp, "app")
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(
                ".git", ".venv", "raw_data_bball_ref", "processed_*", "flat_table_bin"))
            os.remove(os.path.join(copy, rel))
            at = run_page(copy, page)
            excs = [str(e.value)[:200] for e in at.exception]
            line = (f"{page} without {rel}: "
                    + ("CRASH -> " + excs[0] if excs else "handled (no exception)"))
            print("  " + line)
            annotate("notice", "resilience: " + line)
        finally:
            os.chdir(ROOT)
            shutil.rmtree(tmp, ignore_errors=True)

    result = f"RESULT: {'FAILED' if failures else 'PASSED'} ({failures} page(s) with exceptions)"
    print("\n" + result)
    annotate("notice", result)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
