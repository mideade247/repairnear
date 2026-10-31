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
    for command in ("publish", "archive", "restore", "status"):
        action = commands.add_parser(command)
        action.add_argument("service_id")
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
                store.transition("demo-1", "published")
                store.transition("demo-2", "published")
                results = store.search()
            elif args.command == "search":
                results = store.search(
                    area=args.area,
                    category=args.category,
                    limit=args.limit,
                    offset=args.offset,
                )
            else:
                targets = {
                    "publish": "published",
                    "archive": "archived",
                    "restore": "draft",
                }
                if args.command != "status":
                    store.transition(args.service_id, targets[args.command])
                print(
                    json.dumps(
                        {
                            "service_id": args.service_id,
                            "state": store.state(args.service_id),
                        }
                    )
                )
                return 0
            print(json.dumps([asdict(item) for item in results], indent=2))
    except (ValueError, sqlite3.Error) as error:
        parser.exit(2, f"repairnear: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
