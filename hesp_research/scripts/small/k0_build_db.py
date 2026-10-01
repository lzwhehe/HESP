"""Build one SQLite database per ExCyTIn incident from the public CSV release (docs/PROTOCOL_SMALL.md).

The CSVs were written by pandas with sep='❖' and quotechar='"'; every column becomes TEXT COLLATE NOCASE, matching
the official MySQL setup (all columns TEXT, case-insensitive default collation). Empty fields stay ''. NUL bytes are
dropped; column names that collide case-insensitively (AzureDiagnostics) get a '_2' suffix.

    python k0_build_db.py --data ~/k0/data/data_anonymized/incidents --out ~/k0/db
"""
import argparse
import csv
import os
import sqlite3

csv.field_size_limit(2**31 - 1)
SEP = "❖"
NUL = chr(0)


def load_table(con, name, path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        rd = csv.reader((line.replace(NUL, "") for line in f), delimiter=SEP, quotechar='"')
        header, seen = [], set()
        for c in next(rd):
            k = c
            while k.lower() in seen:
                k += "_2"
            seen.add(k.lower())
            header.append(k)
        cols = ", ".join(f'"{c}" TEXT COLLATE NOCASE' for c in header)
        con.execute(f'CREATE TABLE "{name}" ({cols})')
        q = f'INSERT INTO "{name}" VALUES ({", ".join("?" * len(header))})'
        batch, n, bad = [], 0, 0
        for row in rd:
            if len(row) != len(header):
                bad += 1
                continue
            batch.append(row)
            if len(batch) >= 5000:
                con.executemany(q, batch)
                n += len(batch)
                batch = []
        con.executemany(q, batch)
        n += len(batch)
    return n, bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    for inc in sorted(os.listdir(args.data)):
        d = os.path.join(args.data, inc)
        dest = os.path.join(args.out, inc + ".sqlite")
        if os.path.exists(dest) or not os.path.isdir(d):
            continue
        if os.path.exists(dest + ".part"):
            os.remove(dest + ".part")
        con = sqlite3.connect(dest + ".part")
        total = 0
        for fn in sorted(os.listdir(d)):
            p = os.path.join(d, fn)
            if fn.startswith("._"):
                continue
            if fn.endswith(".csv"):
                n, bad = load_table(con, fn[:-4], p)
            elif os.path.isdir(p):  # folder of CSV parts for one table
                parts = sorted(x for x in os.listdir(p) if x.endswith(".csv"))
                n = bad = 0
                for i, x in enumerate(parts):
                    if i == 0:
                        a, b = load_table(con, fn, os.path.join(p, x))
                    else:
                        tmp = fn + "_tmp"
                        a, b = load_table(con, tmp, os.path.join(p, x))
                        con.execute(f'INSERT INTO "{fn}" SELECT * FROM "{tmp}"')
                        con.execute(f'DROP TABLE "{tmp}"')
                    n, bad = n + a, bad + b
            else:
                continue
            total += n
            if bad:
                print(f"  {inc}.{fn}: {bad} malformed rows skipped", flush=True)
        con.commit()
        con.close()
        os.replace(dest + ".part", dest)
        print(inc, "rows", total, flush=True)


if __name__ == "__main__":
    main()
