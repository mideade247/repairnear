import argparse
import json
import sqlite3
from dataclasses import asdict

from repairnear.directory import Directory, Listing


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Search a local repair directory")
    parser.add_argument("--database", default="repairnear.sqlite3")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("demo", help="Search fictional services without writing files")
    search = commands.add_parser("search")
    search.add_argument("--area")
    search.add_argument("--category")
    search.add_argument("--limit", type=int, default=20)
    search.add_argument("--offset", type=int, default=0)
    args = parser.parse_args(argv)
    try:
        with Directory(
            ":memory:" if args.command == "demo" else args.database
        ) as store:
            if args.command == "demo":
                store.add(
                    Listing(
                        "demo-1", "Fictional Cycle Workshop", "Example Town", "bicycle"
                    )
                )
                store.add(
                    Listing(
                        "demo-2",
                        "Fictional Furniture Repair",
                        "Example Town",
                        "furniture",
                    )
                )
                results = store.search()
            else:
                results = store.search(
                    area=args.area,
                    category=args.category,
                    limit=args.limit,
                    offset=args.offset,
                )
            print(json.dumps([asdict(item) for item in results], indent=2))
    except (ValueError, sqlite3.Error) as error:
        parser.exit(2, f"repairnear: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
