"""Tests for the cast_datetime_to / datetime64_precision settings."""

from types import SimpleNamespace

from clickhouse_sqlalchemy import types as clickhouse_sqlalchemy_types

from target_clickhouse.connectors import ClickhouseConnector


def _to_sql_type(jsonschema_type, is_primary_key=False, config=None):
    """Call to_sql_type as an unbound method — avoids full connector init."""
    return ClickhouseConnector.to_sql_type(
        SimpleNamespace(config=config or {}),
        jsonschema_type,
        is_primary_key=is_primary_key,
    )


class TestDatetimeCast:
    """Tests for the cast_datetime_to / datetime64_precision settings."""

    schema = {"type": ["string", "null"], "format": "date-time"}

    def test_default_is_nullable_datetime(self):
        """Without the setting the column stays a plain DateTime."""
        sql_type = _to_sql_type(self.schema)
        assert isinstance(sql_type, clickhouse_sqlalchemy_types.Nullable)
        assert not isinstance(
            sql_type.nested_type,
            clickhouse_sqlalchemy_types.DateTime64,
        )

    def test_datetime64_with_default_precision(self):
        """DateTime64 uses precision 3 unless told otherwise."""
        sql_type = _to_sql_type(
            self.schema,
            config={"cast_datetime_to": "DateTime64"},
        )
        assert isinstance(sql_type, clickhouse_sqlalchemy_types.Nullable)
        assert isinstance(
            sql_type.nested_type,
            clickhouse_sqlalchemy_types.DateTime64,
        )
        assert sql_type.nested_type.precision == 3

    def test_datetime64_custom_precision(self):
        """datetime64_precision is forwarded to the column type."""
        sql_type = _to_sql_type(
            self.schema,
            config={"cast_datetime_to": "DateTime64", "datetime64_precision": 6},
        )
        assert sql_type.nested_type.precision == 6

    def test_datetime64_primary_key_not_nullable(self):
        """Primary keys are never wrapped in Nullable."""
        sql_type = _to_sql_type(
            {"type": "string", "format": "date-time"},
            is_primary_key=True,
            config={"cast_datetime_to": "DateTime64"},
        )
        assert isinstance(sql_type, clickhouse_sqlalchemy_types.DateTime64)
