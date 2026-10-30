import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Listing:
    service_id: str
    name: str
    area: str
    category: str

    def __post_init__(self) -> None:
        for field in ("service_id", "name", "area", "category"):
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field} must be nonempty text")
            if len(value) > 200 or any(ord(char) < 32 for char in value):
                raise ValueError(f"{field} contains invalid or excessive text")
            object.__setattr__(self, field, value.strip())


class Directory:
    def __init__(self, path: str | Path = ":memory:") -> None:
        self._connection = sqlite3.connect(path)
        try:
            self._connection.execute(
                "CREATE TABLE IF NOT EXISTS listings ("
                "service_id TEXT PRIMARY KEY NOT NULL, name TEXT NOT NULL, "
                "area TEXT NOT NULL, category TEXT NOT NULL)"
            )
            self._connection.commit()
        except Exception:
            self._connection.close()
            raise

    def __enter__(self) -> "Directory":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def close(self) -> None:
        self._connection.close()

    def add(self, listing: Listing) -> None:
        if not isinstance(listing, Listing):
            raise TypeError("listing must be a Listing")
        try:
            with self._connection:
                self._connection.execute(
                    "INSERT INTO listings VALUES (?, ?, ?, ?)",
                    (listing.service_id, listing.name, listing.area, listing.category),
                )
        except sqlite3.IntegrityError as error:
            raise ValueError("service_id already exists") from error

    def search(
        self,
        *,
        area: str | None = None,
        category: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Listing]:
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError("limit must be an integer between 1 and 100")
        if type(offset) is not int or offset < 0:
            raise ValueError("offset must be a nonnegative integer")
        for value in (area, category):
            if value is not None and (
                not isinstance(value, str) or not value.strip() or len(value) > 200
            ):
                raise ValueError("filters must be nonempty text up to 200 characters")
        rows = self._connection.execute(
            "SELECT service_id, name, area, category FROM listings "
            "WHERE (? IS NULL OR area = ? COLLATE NOCASE) "
            "AND (? IS NULL OR category = ? COLLATE NOCASE) "
            "ORDER BY name COLLATE NOCASE, service_id LIMIT ? OFFSET ?",
            (
                area,
                area.strip() if area is not None else None,
                category,
                category.strip() if category is not None else None,
                limit,
                offset,
            ),
        ).fetchall()
        return [Listing(*row) for row in rows]
