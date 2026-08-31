"""Synchronize the SQLite schema with every entity declared in ``models``."""

import importlib
import pkgutil
import sqlite3

from . import db


def _load_entities() -> None:
    """Import all model modules so their entities are registered with Pony."""
    package = importlib.import_module(__package__)
    for module in pkgutil.iter_modules(package.__path__, f"{package.__name__}."):
        if module.name.rsplit(".", 1)[-1] not in {"database", "migrations"}:
            importlib.import_module(module.name)


def _quote(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _table_name(connection: sqlite3.Connection, entity_name: str) -> str:
    names = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }
    return next((name for name in names if name.lower() == entity_name.lower()), entity_name)


def _sql_type(attribute: object) -> str:
    if attribute.py_type is int:
        return "BIGINT" if getattr(attribute, "size", None) == 64 else "INTEGER"
    return {float: "REAL", str: "TEXT", bytes: "BLOB"}.get(attribute.py_type, "INTEGER")


def _scalar_attributes(entity: object) -> list[object]:
    return [attribute for attribute in entity._attrs_ if not attribute.is_collection]


def _related_entity(attribute: object) -> object | None:
    if not isinstance(attribute.py_type, str):
        return None
    return db.entities.get(attribute.py_type)


def _default_sql(attribute: object) -> str:
    value = getattr(attribute, "default", None)
    if value is None:
        return ""
    if isinstance(value, str):
        return " DEFAULT '" + value.replace("'", "''") + "'"
    if isinstance(value, bool):
        return f" DEFAULT {int(value)}"
    return f" DEFAULT {value}"


def _create_table_sql(entity: object, table_name: str) -> str:
    definitions = []
    foreign_keys = []
    for attribute in _scalar_attributes(entity):
        if attribute.name == "id":
            definitions.append(f'{_quote(attribute.name)} INTEGER PRIMARY KEY AUTOINCREMENT')
            continue
        definition = f"{_quote(attribute.name)} {_sql_type(attribute)}"
        if attribute.is_required:
            definition += " NOT NULL"
        definition += _default_sql(attribute)
        related = _related_entity(attribute)
        if related is not None:
            foreign_keys.append(
                f"FOREIGN KEY ({_quote(attribute.name)}) REFERENCES "
                f"{_quote(related.__name__)} ({_quote('id')}) ON DELETE CASCADE"
            )
        definitions.append(definition)

    for key in entity._keys_:
        names = [attribute.name for attribute in key]
        if names != ["id"]:
            definitions.append("UNIQUE (" + ", ".join(_quote(name) for name in names) + ")")
    definitions.extend(foreign_keys)
    return f"CREATE TABLE {_quote(table_name)} (" + ", ".join(definitions) + ")"


def _unique_columns(connection: sqlite3.Connection, table_name: str) -> set[tuple[str, ...]]:
    result = set()
    for row in connection.execute(f"PRAGMA index_list({_quote(table_name)})"):
        if row[2]:
            index_name = row[1]
            columns = tuple(
                info[2]
                for info in connection.execute(f"PRAGMA index_info({_quote(index_name)})")
            )
            result.add(columns)
    return result


def _schema_matches(connection: sqlite3.Connection, entity: object, table_name: str) -> bool:
    columns = connection.execute(f"PRAGMA table_info({_quote(table_name)})").fetchall()
    if not columns:
        return False
    expected = _scalar_attributes(entity)
    if {row[1] for row in columns} != {attribute.name for attribute in expected}:
        return False
    for row in columns:
        attribute = next(attribute for attribute in expected if attribute.name == row[1])
        if row[2].upper() != _sql_type(attribute) or bool(row[3]) != attribute.is_required:
            return False
        expected_default = _default_sql(attribute).removeprefix(" DEFAULT ") or None
        actual_default = row[4].strip("()") if row[4] else None
        if expected_default != actual_default:
            return False
        if attribute.name == "id" and (row[5] != 1 or row[2].upper() != "INTEGER"):
            return False
    expected_unique = {
        tuple(attribute.name for attribute in key)
        for key in entity._keys_
        if [attribute.name for attribute in key] != ["id"]
    }
    return _unique_columns(connection, table_name) == expected_unique


def _rebuild_table(connection: sqlite3.Connection, entity: object, table_name: str) -> None:
    old_columns = {
        row[1] for row in connection.execute(f"PRAGMA table_info({_quote(table_name)})")
    }
    new_columns = [attribute.name for attribute in _scalar_attributes(entity)]
    common_columns = [name for name in new_columns if name in old_columns]
    temporary_name = f"__migration_{table_name}"
    connection.execute(f"DROP TABLE IF EXISTS {_quote(temporary_name)}")
    connection.execute(_create_table_sql(entity, temporary_name))
    if common_columns:
        columns = ", ".join(_quote(name) for name in common_columns)
        connection.execute(
            f"INSERT INTO {_quote(temporary_name)} ({columns}) "
            f"SELECT {columns} FROM {_quote(table_name)}"
        )
    connection.execute(f"DROP TABLE {_quote(table_name)}")
    connection.execute(f"ALTER TABLE {_quote(temporary_name)} RENAME TO {_quote(table_name)}")


def migrate_database(filename: str) -> None:
    _load_entities()
    connection = sqlite3.connect(filename)
    try:
        connection.execute("PRAGMA foreign_keys = OFF")
        connection.execute("BEGIN")
        for entity in db.entities.values():
            table_name = _table_name(connection, entity.__name__)
            exists = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
                (table_name,),
            ).fetchone()
            if not exists:
                connection.execute(_create_table_sql(entity, table_name))
            elif not _schema_matches(connection, entity, table_name):
                _rebuild_table(connection, entity, table_name)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.close()