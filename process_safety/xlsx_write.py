"""Minimal .xlsx writer (standard library only): text, numbers, bold header row, frozen panes, status fills.

Text is stored as inline strings, so a value beginning "=" stays text and is never evaluated as a formula.
Workbooks hold values only: no formulas, charts or merged cells.
"""
from __future__ import annotations

import math
import re
import zipfile
from xml.sax.saxutils import escape, quoteattr

_BAD_XML = re.compile("[^\t\n\r\x20-퟿-�\U00010000-\U0010ffff]")
# cell style ids, matching the order of cellXfs below
_PLAIN, _HEAD = 0, 1
_STATUS = {"pass": 2, "fail": 3, "not_checked": 4, "review": 5, "NOT CHECKED": 4, "FAIL": 3, "PASS": 2, "REVIEW": 5}
_FILLS = ("FFE1E0D9", "FFD7F0D7", "FFF6D2D2", "FFFDEBC0", "FFD9E7FA")     # header, pass, fail, not checked, review

_STYLES = ('<?xml version="1.0" encoding="UTF-8"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
           '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
           f'<fills count="{len(_FILLS) + 2}"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill>'
           + "".join(f'<fill><patternFill patternType="solid"><fgColor rgb="{c}"/></patternFill></fill>' for c in _FILLS) +
           '</fills><borders count="1"><border/></borders><cellStyleXfs count="1"><xf/></cellStyleXfs>'
           f'<cellXfs count="{len(_FILLS) + 1}"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
           '<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/>'
           + "".join(f'<xf numFmtId="0" fontId="0" fillId="{i}" borderId="0" xfId="0" applyFill="1"/>' for i in range(3, len(_FILLS) + 2)) +
           '</cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>')


def column_name(i: int) -> str:
    """0 -> A, 25 -> Z, 26 -> AA."""
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def _cell(ref: str, v, style: int) -> str:
    if v is None or v == "":
        return f'<c r="{ref}" s="{style}"/>' if style else ""
    if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v):
        return f'<c r="{ref}" s="{style}"><v>{v!r}</v></c>'
    text = escape(_BAD_XML.sub("", str(v))[:32767])
    return f'<c r="{ref}" s="{style}" t="inlineStr"><is><t xml:space="preserve">{text}</t></is></c>'


def _sheet(rows: list[list]) -> str:
    ncol = max((len(r) for r in rows), default=1)
    widths = [min(60, max([8] + [len(str(r[c])) + 2 for r in rows if c < len(r) and r[c] is not None])) for c in range(ncol)]
    cols = "".join(f'<col min="{c + 1}" max="{c + 1}" width="{w}" customWidth="1"/>' for c, w in enumerate(widths))
    body = []
    for n, row in enumerate(rows):
        cells = "".join(_cell(f"{column_name(c)}{n + 1}", v, _HEAD if n == 0 else _STATUS.get(v, _PLAIN) if isinstance(v, str) else _PLAIN)
                        for c, v in enumerate(row))
        body.append(f'<row r="{n + 1}">{cells}</row>')
    return ('<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetViews><sheetView workbookViewId="0"><pane xSplit="1" ySplit="1" topLeftCell="B2" activePane="bottomRight" state="frozen"/>'
            f'</sheetView></sheetViews><cols>{cols}</cols><sheetData>{"".join(body)}</sheetData></worksheet>')


def write_xlsx(path: str, sheets: list[tuple[str, list[list]]]) -> None:
    """sheets: [(name, rows)], first row of each is the header."""
    if not sheets:
        raise ValueError("a workbook needs at least one sheet")
    names = []
    for name, _ in sheets:
        n = re.sub(r"[\[\]:*?/\\]", " ", _BAD_XML.sub("", name))[:31] or "Sheet"
        if n.lower() in (x.lower() for x in names):
            raise ValueError(f"duplicate sheet name {n!r}")
        names.append(n)
    ns = "http://schemas.openxmlformats.org"
    ids = range(1, len(sheets) + 1)
    types = ('<?xml version="1.0" encoding="UTF-8"?>'
             f'<Types xmlns="{ns}/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
             '<Default Extension="xml" ContentType="application/xml"/>'
             '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
             '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
             + "".join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for i in ids)
             + "</Types>")
    root = (f'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="{ns}/package/2006/relationships">'
            f'<Relationship Id="rId1" Type="{ns}/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
    book = (f'<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="{ns}/spreadsheetml/2006/main" xmlns:r="{ns}/officeDocument/2006/relationships"><sheets>'
            + "".join(f'<sheet name={quoteattr(n)} sheetId="{i}" r:id="rId{i}"/>' for i, n in zip(ids, names)) + "</sheets></workbook>")
    rels = (f'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="{ns}/package/2006/relationships">'
            + "".join(f'<Relationship Id="rId{i}" Type="{ns}/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>' for i in ids)
            + f'<Relationship Id="rId{len(sheets) + 1}" Type="{ns}/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", types)
        z.writestr("_rels/.rels", root)
        z.writestr("xl/workbook.xml", book)
        z.writestr("xl/_rels/workbook.xml.rels", rels)
        z.writestr("xl/styles.xml", _STYLES)
        for i, (_, rows) in zip(ids, sheets):
            z.writestr(f"xl/worksheets/sheet{i}.xml", _sheet(rows))
