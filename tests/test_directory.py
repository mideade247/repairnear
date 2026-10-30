import sqlite3

import pytest

from repairnear.cli import main
from repairnear.directory import Directory, Listing


def listing(
    service_id="one", name="Fictional Workshop", area="Example Town", category="bicycle"
):
    return Listing(service_id, name, area, category)


def test_persistence(tmp_path):
    path = tmp_path / "directory.sqlite3"
    with Directory(path) as store:
        store.add(listing())
    with Directory(path) as store:
        assert store.search() == [listing()]


def test_combined_filters_and_order():
    with Directory() as store:
        store.add(listing("b", "Beta"))
        store.add(listing("a", "Alpha"))
        store.add(listing("c", "Other", category="furniture"))
        assert [
            x.service_id for x in store.search(area="example town", category="BICYCLE")
        ] == ["a", "b"]
        assert len(store.search(area="Example Town")) == 3
        assert len(store.search(category="furniture")) == 1
        assert store.search(area="Elsewhere") == []
        assert [x.service_id for x in store.search(limit=1, offset=1)] == ["b"]


def test_duplicate_does_not_replace_and_connection_remains_usable():
    with Directory() as store:
        store.add(listing())
        with pytest.raises(ValueError, match="already exists"):
            store.add(listing(name="Replacement"))
        store.add(listing("two"))
        assert store.search()[0].name == "Fictional Workshop"
        assert len(store.search()) == 2


def test_sql_fragments_are_literal():
    value = "Town'; DROP TABLE listings; --"
    with Directory() as store:
        store.add(listing(area=value))
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
