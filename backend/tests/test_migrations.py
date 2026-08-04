from pathlib import Path

from alembic.config import Config
from sqlalchemy import create_engine, inspect

from alembic import command


def test_migrations_are_idempotent_and_persistent(tmp_path: Path) -> None:
    database_path = tmp_path / "persistent.db"
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    config.set_main_option("script_location", str(Path(__file__).parents[1] / "alembic"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path}")

    command.upgrade(config, "head")
    command.upgrade(config, "head")

    assert database_path.exists()
    assert (
        "alembic_version" in inspect(create_engine(f"sqlite:///{database_path}")).get_table_names()
    )
