import sqlite3

import pytest

from repairnear.cli import main
from repairnear.directory import Directory, Listing


def listing(
    service_id="one", name="Fictional Workshop", area="Example Town", category="bicycle"
):
    return Listing(service_id, name, area, category)


def add_published(store, record):
    store.add(record)
    store.transition(record.service_id, "published")


def test_persistence(tmp_path):
    path = tmp_path / "directory.sqlite3"
    with Directory(path) as store:
        add_published(store, listing())
    with Directory(path) as store:
        assert store.search() == [listing()]


def test_combined_filters_and_order():
    with Directory() as store:
        add_published(store, listing("b", "Beta"))
        add_published(store, listing("a", "Alpha"))
        add_published(store, listing("c", "Other", category="furniture"))
        assert [
            x.service_id for x in store.search(area="example town", category="BICYCLE")
        ] == ["a", "b"]
        assert len(store.search(area="Example Town")) == 3
        assert len(store.search(category="furniture")) == 1
        assert store.search(area="Elsewhere") == []
        assert [x.service_id for x in store.search(limit=1, offset=1)] == ["b"]


def test_duplicate_does_not_replace_and_connection_remains_usable():
    with Directory() as store:
        add_published(store, listing())
        with pytest.raises(ValueError, match="already exists"):
            add_published(store, listing(name="Replacement"))
        add_published(store, listing("two"))
        assert store.search()[0].name == "Fictional Workshop"
        assert len(store.search()) == 2


def test_sql_fragments_are_literal():
    value = "Town'; DROP TABLE listings; --"
    with Directory() as store:
        add_published(store, listing(area=value))
        assert store.search(area=value) == [listing(area=value)]
        assert store.search(area="' OR 1=1 --") == []


@pytest.mark.parametrize("field", ["service_id", "name", "area", "category"])
@pytest.mark.parametrize("value", [None, "", "  ", 123, "x" * 201, "bad\nvalue"])
def test_invalid_listing(field, value):
    values = dict(service_id="one", name="Example", area="Town", category="bicycle")
    values[field] = value
    with pytest.raises(ValueError):
        Listing(**values)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"limit": 0},
        {"limit": 101},
        {"limit": True},
        {"offset": -1},
        {"offset": False},
        {"area": " "},
        {"category": 2},
    ],
)
def test_invalid_search(kwargs):
    with Directory() as store:
        with pytest.raises(ValueError):
            store.search(**kwargs)


def test_connection_closed_on_exception():
    store = Directory()
    with pytest.raises(RuntimeError), store:
        raise RuntimeError("failed operation")
    with pytest.raises(sqlite3.ProgrammingError):
        store.search()


def test_demo_uses_no_database_file(tmp_path, capsys):
    path = tmp_path / "unused.sqlite3"
    assert main(["--database", str(path), "demo"]) == 0
    assert "Fictional Cycle Workshop" in capsys.readouterr().out
    assert not path.exists()


def test_cli_invalid_limit(tmp_path, capsys):
    with pytest.raises(SystemExit) as error:
        main(["--database", str(tmp_path / "test.sqlite3"), "search", "--limit", "0"])
    assert error.value.code == 2
    assert "limit" in capsys.readouterr().err


def test_draft_lifecycle_and_filtered_pagination(tmp_path):
    path = tmp_path / "lifecycle.sqlite3"
    with Directory(path) as store:
        store.add(listing("draft", "A Draft"))
        store.add(listing())
        assert store.state("one") == "draft"
        assert store.search() == []
        store.transition("one", "published")
        assert store.search(limit=1) == [listing()]
        store.transition("one", "archived")
        assert store.search() == []
        with pytest.raises(ValueError, match="cannot change"):
            store.transition("one", "published")
        store.transition("one", "draft")
    with Directory(path) as store:
        assert store.state("one") == "draft"
        store.transition("one", "published")
        assert store.search() == [listing()]


@pytest.mark.parametrize("target", ["draft", "unknown", None])
def test_invalid_transition_leaves_state_unchanged(target):
    with Directory() as store:
        store.add(listing())
        with pytest.raises(ValueError):
            store.transition("one", target)
        assert store.state("one") == "draft"
        with pytest.raises(ValueError, match="unknown service_id"):
            store.transition("missing", "published")


def test_legacy_migration_preserves_records_as_drafts(tmp_path):
    path = tmp_path / "legacy.sqlite3"
    with sqlite3.connect(path) as connection:
        connection.execute(
            "CREATE TABLE listings (service_id TEXT PRIMARY KEY NOT NULL, "
            "name TEXT NOT NULL, area TEXT NOT NULL, category TEXT NOT NULL)"
        )
        connection.execute(
            "INSERT INTO listings VALUES (?, ?, ?, ?)",
            ("one", "Fictional Workshop", "Example Town", "bicycle"),
        )
    with Directory(path) as store:
        assert store.state("one") == "draft"
        assert store.search() == []
        store.transition("one", "published")
        assert store.search() == [listing()]
    with Directory(path) as store:
        assert store.state("one") == "published"


def test_unknown_schema_is_not_modified(tmp_path):
    path = tmp_path / "future.sqlite3"
    with sqlite3.connect(path) as connection:
        connection.execute("PRAGMA user_version = 99")
    with pytest.raises(ValueError, match="unsupported"):
        Directory(path)
    with sqlite3.connect(path) as connection:
        assert connection.execute("PRAGMA user_version").fetchone() == (99,)


def test_cli_publication_commands(tmp_path, capsys):
    path = tmp_path / "cli.sqlite3"
    with Directory(path) as store:
        store.add(listing())
    for command, state in (
        ("status", "draft"),
        ("publish", "published"),
        ("archive", "archived"),
        ("restore", "draft"),
    ):
        assert main(["--database", str(path), command, "one"]) == 0
        assert state in capsys.readouterr().out
    with pytest.raises(SystemExit) as error:
        main(["--database", str(path), "publish", "missing"])
    assert error.value.code == 2


def test_migration_failure_rolls_back(tmp_path):
    path = tmp_path / "broken.sqlite3"
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE listings (state TEXT)")
    with pytest.raises(sqlite3.OperationalError):
        Directory(path)
    with sqlite3.connect(path) as connection:
        assert connection.execute("PRAGMA user_version").fetchone() == (0,)
        assert len(connection.execute("PRAGMA table_info(listings)").fetchall()) == 1
