"""Build a searchable CSV index of a Zotero library's files (title, file path, type, collections, tags) from zotero.sqlite.

    python scripts/zotero_index.py /path/to/zotero.sqlite OUT.csv [--storage /path/to/Zotero/storage] [--also-search DIR [DIR ...]]

Reads a COPY of the database read-only (never the live file, which Zotero locks and which sits in WAL mode). The index lists what is in your
library and where its attachment file is; it contains titles and file names that may be personal, so write it outside any repository.
With --storage, each row also says whether the attachment file exists locally (cloud-only Dropbox placeholders still count as present).
With --also-search, files not found at their Zotero path are matched by file name (exact, or with a hash prefix such as 'ab12cd_name.pdf') against the
directories given, so a reorganised library still resolves; only names are read, never file contents. Stdlib only.
"""
import csv
import os
import shutil
import sqlite3
import sys
import tempfile


def name_map(dirs):
    m: dict[str, str] = {}
    for d in dirs:
        for root, _, files in os.walk(d):
            for f in files:
                m.setdefault(f, os.path.join(root, f))
                if "_" in f:
                    m.setdefault(f.split("_", 1)[1], os.path.join(root, f))
    return m


def build(db, out, storage=None, search_dirs=()):
    found = name_map(search_dirs) if search_dirs else {}
    tmp = tempfile.mkdtemp()
    cp = os.path.join(tmp, "z.sqlite")
    shutil.copy(db, cp)
    c = sqlite3.connect(f"file:{cp}?mode=ro&immutable=1", uri=True)
    q = lambda s, *a: c.execute(s, a).fetchall()          # noqa: E731
    title_f = q("select fieldID from fields where fieldName='title'")[0][0]
    deleted = {r[0] for r in q("select itemID from deletedItems")}
    colname = {r[0]: r[1] for r in q("select collectionID, collectionName from collections")}
    itemcols: dict[int, list[str]] = {}
    for iid, cid in q("select itemID, collectionID from collectionItems"):
        itemcols.setdefault(iid, []).append(colname.get(cid, ""))
    tags: dict[int, list[str]] = {}
    for iid, name in q("select it.itemID, t.name from itemTags it join tags t on t.tagID = it.tagID"):
        tags.setdefault(iid, []).append(name)
    titles = {r[0]: r[1] for r in q("select d.itemID, v.value from itemData d join itemDataValues v on v.valueID = d.valueID where d.fieldID = ?", title_f)}
    rows = 0
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["key", "title", "content_type", "file_name", "dropbox_relative_path", "exists_locally", "located_path", "collections", "tags", "parent_title"])
        for iid, parent, path, ctype, key in q("select a.itemID, a.parentItemID, a.path, a.contentType, i.key from itemAttachments a join items i on i.itemID = a.itemID"):
            if iid in deleted:
                continue
            fname = path[len("storage:"):] if path and path.startswith("storage:") else (path or "")
            rel = f"Zotero/storage/{key}/{fname}" if path and path.startswith("storage:") else ""
            exists, located = "", ""
            if storage and rel:
                exists = os.path.exists(os.path.join(storage, key, fname))
                located = os.path.join(storage, key, fname) if exists else found.get(fname, "")
            cols = itemcols.get(parent or iid, []) + itemcols.get(iid, [])
            w.writerow([key, titles.get(iid) or titles.get(parent) or fname, ctype or "", fname, rel, exists, located, ";".join(sorted(set(cols))),
                        ";".join(sorted(set(tags.get(parent or iid, [])))), titles.get(parent, "")])
            rows += 1
    shutil.rmtree(tmp, ignore_errors=True)
    return rows


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    st = sys.argv[sys.argv.index("--storage") + 1] if "--storage" in sys.argv else None
    dirs = []
    if "--also-search" in sys.argv:
        for a in sys.argv[sys.argv.index("--also-search") + 1:]:
            if a.startswith("--"):
                break
            dirs.append(a)
    print(build(sys.argv[1], sys.argv[2], st, dirs), "attachments indexed")
