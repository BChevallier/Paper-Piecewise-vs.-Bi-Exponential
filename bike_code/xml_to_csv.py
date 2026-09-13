import csv
import xml.etree.ElementTree as ET
from pathlib import Path


# =========================
# EDIT THESE SETTINGS
# =========================

INPUT_FOLDER = Path("../bike_data/raw_data/ergo_data")
OUTPUT_FOLDER = Path("../bike_data/raw_data/tt2")

INPUT_FILE_PATTERN = "tt2_cpet_p{participant:02d}.xml"
OUTPUT_FILE_PATTERN = "tt2_p{participant:02d}.csv"

FIRST_PARTICIPANT = 1
LAST_PARTICIPANT = 44

TABLE_TITLE = "Messdaten"
SKIP_UNITS_ROW = True

# If True, values like 0:00:08,000 become 0:00:08
REMOVE_MILLISECONDS_FROM_T = True


# =========================
# DO NOT EDIT BELOW
# =========================

NS = {
    "ss": "urn:schemas-microsoft-com:office:spreadsheet"
}


def get_cell_text(cell):
    data = cell.find("ss:Data", NS)

    if data is None or data.text is None:
        return ""

    return data.text.strip()


def parse_row(row):
    values = []
    current_col = 1

    for cell in row.findall("ss:Cell", NS):
        index_attr = cell.attrib.get(f"{{{NS['ss']}}}Index")

        if index_attr is not None:
            target_col = int(index_attr)

            while current_col < target_col:
                values.append("")
                current_col += 1

        values.append(get_cell_text(cell))
        current_col += 1

    return values


def clean_t_value(value):
    """
    Convert time strings like:
    0:00:08,000 -> 0:00:08
    00:00:08,000 -> 00:00:08
    """
    if not isinstance(value, str):
        return value

    return value.replace(",000", "")


def find_table_rows(rows, table_title=None, min_columns=3):
    parsed_rows = [parse_row(row) for row in rows]

    if table_title:
        for i, values in enumerate(parsed_rows):
            if any(value == table_title for value in values):
                return i + 1, parsed_rows

        raise ValueError(f"Could not find table title: {table_title}")

    for i, values in enumerate(parsed_rows):
        non_empty = [v for v in values if v]

        if len(non_empty) >= min_columns:
            numeric_count = 0

            for value in non_empty:
                try:
                    float(value.replace(",", "."))
                    numeric_count += 1
                except ValueError:
                    pass

            if numeric_count < len(non_empty) / 2:
                return i, parsed_rows

    raise ValueError("Could not automatically detect a table header row.")


def convert_xml_table_to_csv(
    xml_path,
    csv_path,
    table_title="Messdaten",
    skip_units_row=True,
    stop_at_empty_row=True,
    remove_milliseconds_from_t=True
):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    rows = root.findall(".//ss:Row", NS)

    if not rows:
        raise ValueError("No SpreadsheetML rows found in XML file.")

    header_index, parsed_rows = find_table_rows(
        rows,
        table_title=table_title
    )

    headers = parsed_rows[header_index]

    if not headers or not any(headers):
        raise ValueError("Detected header row is empty.")

    data_start_index = header_index + 1

    if skip_units_row:
        data_start_index += 1

    records = []

    if "t" in headers:
        t_index = headers.index("t")
    else:
        t_index = None

    for values in parsed_rows[data_start_index:]:
        if stop_at_empty_row and not any(values):
            break

        if len(values) < len(headers):
            values += [""] * (len(headers) - len(values))

        values = values[:len(headers)]

        if not any(values):
            continue

        if remove_milliseconds_from_t and t_index is not None:
            values[t_index] = clean_t_value(values[t_index])

        records.append(values)

    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(records)

    return len(records)


for participant in range(FIRST_PARTICIPANT, LAST_PARTICIPANT + 1):
    input_xml_path = INPUT_FOLDER / INPUT_FILE_PATTERN.format(
        participant=participant
    )

    output_csv_path = OUTPUT_FOLDER / OUTPUT_FILE_PATTERN.format(
        participant=participant
    )

    if not input_xml_path.exists():
        print(f"Skipping p{participant:02d}: file not found: {input_xml_path}")
        continue

    try:
        row_count = convert_xml_table_to_csv(
            xml_path=input_xml_path,
            csv_path=output_csv_path,
            table_title=TABLE_TITLE,
            skip_units_row=SKIP_UNITS_ROW,
            remove_milliseconds_from_t=REMOVE_MILLISECONDS_FROM_T
        )

        print(f"p{participant:02d}: converted {row_count} rows -> {output_csv_path}")

    except Exception as e:
        print(f"p{participant:02d}: failed: {e}")