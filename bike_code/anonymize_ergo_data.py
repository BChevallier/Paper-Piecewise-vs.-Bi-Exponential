"""
Blank the testing facility's personal contact details in the raw CPET exports.

The MetaSoft exports carry a facility contact block in their Stammdaten header:
the operator's name, the named contact person, a direct phone line and an email
address. This repository is public, so those four cells are blanked here. The
institution name and its postal address are left in place as ordinary provenance.

Participant identity is already pseudonymised by the export itself — surnames and
given names are reduced to initials and the date of birth is a constant
placeholder — so nothing in the participant block needs redacting.

Only those cells are rewritten, in place, into the empty-value form the exports
already use for blank fields (`<Data ss:Type="String"></Data>`). Everything else,
including the whole Messdaten measurement table, is left byte-for-byte untouched:
the file is edited as text rather than reparsed and reserialised, because an XML
round-trip rewrites the declaration and reflows the document.

Fields are located by their label, never by the value being removed, so this
script does not itself restate the data it exists to delete.

Re-run safe: once blanked there is nothing left to match.

Usage:
    python anonymize_ergo_data.py            # blank the fields in place
    python anonymize_ergo_data.py --check    # report only, change nothing
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ERGO_DATA = REPO_ROOT / "bike_data" / "raw_data" / "ergo_data"

# Labelled cells whose value is personal contact information.
LABELS_TO_BLANK = ("Ansprechpartner", "Telefon", "E-Mail")

# The operator's name sits alone in the label position of the row directly after
# the facility's "Name" row, so it has no label of its own to match on.
OPERATOR_ROW_FOLLOWS = "Name"

CELL = r'<Cell[^>]*><Data ss:Type="String">'


def blank_labelled_value(text, label):
    """Blank the value cell of the first row carrying this exact label."""
    pattern = re.compile(
        r'(<Data ss:Type="String">' + re.escape(label) + r"</Data></Cell>\s*"
        + CELL + r")([^<]+)(</Data>)"
    )
    return pattern.subn(r"\1\3", text, count=1)


def blank_operator_name(text):
    """Blank the unlabelled operator-name cell following the facility name row."""
    pattern = re.compile(
        r'(<Data ss:Type="String">'
        + re.escape(OPERATOR_ROW_FOLLOWS)
        + r"</Data></Cell>\s*"
        + CELL
        + r"[^<]*</Data></Cell>\s*</Row>\s*<Row>\s*"
        + CELL
        + r")([^<]+)(</Data>)"
    )
    return pattern.subn(r"\1\3", text, count=1)


def scrub(text):
    """Return the scrubbed text and the labels that actually changed."""
    changed = []

    text, n = blank_operator_name(text)
    if n:
        changed.append("operator name")

    for label in LABELS_TO_BLANK:
        text, n = blank_labelled_value(text, label)
        if n:
            changed.append(label)

    return text, changed


def main(check_only):
    paths = sorted(ERGO_DATA.glob("*.xml"))
    if not paths:
        raise SystemExit(f"No XML files found in {ERGO_DATA}")

    touched = 0
    for path in paths:
        original = path.read_text(encoding="utf-8")
        scrubbed, changed = scrub(original)

        if not changed:
            continue

        touched += 1
        verb = "would blank" if check_only else "blanked"
        print(f"{path.name}: {verb} {', '.join(changed)}")

        if not check_only:
            path.write_text(scrubbed, encoding="utf-8")

    print(
        f"\n{len(paths)} files scanned, {touched} "
        f"{'would be modified' if check_only else 'modified'}, "
        f"{len(paths) - touched} already clean"
    )


if __name__ == "__main__":
    main(check_only="--check" in sys.argv[1:])
