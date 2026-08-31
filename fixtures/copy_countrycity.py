"""Copy the countrycity table from one SQLite database to another."""

import argparse
import sqlite3
from pathlib import Path


CREATE_COUNTRYCITY = """
CREATE TABLE IF NOT EXISTS countrycity (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
)
"""


def copy_countrycity(source_path: Path, destination_path: Path, batch_size: int) -> int:
    with sqlite3.connect(source_path) as source, sqlite3.connect(destination_path) as destination:
        source_columns = [column[1] for column in source.execute("PRAGMA table_info(countrycity)")]
        if source_columns != ["id", "name"]:
            raise ValueError("Source database does not contain the expected countrycity table")

        destination.execute(CREATE_COUNTRYCITY)
        rows_copied = 0
        while True:
            rows = source.execute(
                "SELECT id, name FROM countrycity ORDER BY id LIMIT ? OFFSET ?",
                (batch_size, rows_copied),
            ).fetchall()
            if not rows:
                break

            destination.executemany(
                "INSERT OR IGNORE INTO countrycity (id, name) VALUES (?, ?)",
                rows,
            )
            rows_copied += len(rows)

        destination_count = destination.execute(
            "SELECT COUNT(*) FROM countrycity"
        ).fetchone()[0]
        if destination_count < rows_copied:
            raise RuntimeError(
                f"Destination contains {destination_count} rows; expected at least {rows_copied}"
            )

    return rows_copied


def discover_databases() -> tuple[Path, Path]:
    candidates = []
    for path in Path.cwd().rglob("*"):
        if path.suffix not in {".db", ".sqlite", ".sqlite3"} or ".vs" in path.parts:
            continue
        try:
            with sqlite3.connect(path) as connection:
                countrycity_count = connection.execute(
                    "SELECT COUNT(*) FROM countrycity"
                ).fetchone()[0] if connection.execute(
                    "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'countrycity'"
                ).fetchone() else None
            candidates.append((path, countrycity_count))
        except sqlite3.Error:
            continue

    sources = [path for path, row_count in candidates if row_count and row_count > 0]
    destinations = [path for path, row_count in candidates if row_count == 0]
    if len(sources) != 1 or len(destinations) != 1:
        details = ", ".join(f"{path} ({count if count is not None else 'no countrycity table'} rows)" for path, count in candidates)
        raise RuntimeError(
            "Could not identify one source and one destination database. "
            f"Found: {details or 'none'}; pass both paths explicitly."
        )
    return sources[0], destinations[0]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, nargs="?", help="Path to the olddb SQLite file")
    parser.add_argument("destination", type=Path, nargs="?", help="Path to the dbb SQLite file")
    parser.add_argument("--batch-size", type=int, default=1000)
    args = parser.parse_args()

    if args.batch_size < 1:
        parser.error("--batch-size must be greater than zero")
    if args.source is None or args.destination is None:
        try:
            args.source, args.destination = discover_databases()
        except RuntimeError as error:
            parser.error(str(error))
    if not args.source.is_file():
        parser.error(f"Source database does not exist: {args.source}")

    rows_copied = copy_countrycity(args.source, args.destination, args.batch_size)
    print(f"Copied {rows_copied} countrycity rows to {args.destination}")


if __name__ == "__main__":
    main()