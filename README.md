# RepairNear

RepairNear aims to help people find local repair, reuse and tool-lending services.
This initial skeleton provides a tested local SQLite directory and command-line
search. It has no public website or real service listings yet.

## Run locally

Requires Python 3.11 or newer. From this directory:

```sh
python -m venv .venv
```

Activate with `.venv\Scripts\activate` on Windows or
`source .venv/bin/activate` on Linux/macOS, then:

```sh
python -m pip install -e . -r requirements-dev.txt
repairnear demo
repairnear search --area "Example Town" --category bicycle
```

The demo uses fictional records in memory and writes no database file. Search
opens or creates `repairnear.sqlite3`, which starts empty. Select another file
with `repairnear --database directory.sqlite3 search`. Output is JSON.
Filters use exact case-insensitive matching for ASCII text; geographic distance
search and international text matching are not implemented.

## Add a synthetic listing

```python
from repairnear.directory import Directory, Listing

with Directory("repairnear.sqlite3") as directory:
    directory.add(Listing(
        "example-1", "Fictional Cycle Workshop", "Example Town", "bicycle"
    ))
    directory.transition("example-1", "published")
    print(directory.search(area="Example Town", category="bicycle"))
```

Duplicate IDs are rejected without replacing records. Searches return at most
100 results per page in stable name/ID order. Connections close on context exit.

## Checks

```sh
python -m pytest -q
python -m ruff check src tests scripts
python -m ruff format --check src tests scripts
```

CI runs these checks on Python 3.11 and 3.13. Tests use isolated synthetic records
and local temporary databases, with no external services or credentials.

## Next steps

See [ROADMAP.md](ROADMAP.md) for milestones and the next bounded backend task.
The roadmap describes the
planned Django application; this small standalone package establishes the local
directory behaviour first. It does not mark the full backend milestone complete.

Use organisation-level information only after checking accuracy and reuse rights.
The skeleton is suitable for local development; a public service still requires
publication controls, editorial workflows and deployment hardening.

## License

MIT. See [LICENSE](LICENSE).

## Security checks

CI also runs Bandit against application and utility code, plus detect-secrets
against tracked working-tree files. Findings fail CI; scanner failures also fail
the job. Secret values are not printed. This scan does not inspect Git history
or ignored files. Run these checks locally after installing development tools:

```sh
python -m bandit -r src scripts
python -m detect_secrets scan | python scripts/check_secrets.py
```

The secret check requires an initialised Git repository with the intended files
staged or committed. It does not replace a history scan before publication.

## Publication lifecycle

New listings start as drafts. Public search returns only published listings,
with publication filtering applied before pagination. Lifecycle changes are local
editor operations, not a web authentication or authorisation system.

```sh
repairnear --database repairnear.sqlite3 status example-1
repairnear --database repairnear.sqlite3 publish example-1
repairnear --database repairnear.sqlite3 archive example-1
repairnear --database repairnear.sqlite3 restore example-1
```

Allowed transitions are draft to published or archived, published to archived,
and archived to draft. Restore returns a listing to draft; publication then needs
an explicit action. Repeated or invalid transitions and unknown IDs return errors
without changing data. `Directory.state()` inspects an exact service ID.

Existing four-column databases migrate transactionally to schema version 1 on
opening. Existing records are retained as drafts and must be reviewed before
publishing. Back up an existing database before upgrading; older application
versions cannot operate on the new schema. Unsupported schema versions are
rejected. The demo explicitly publishes its fictional listings in memory.
