import pytest
from unittest.mock import patch, MagicMock

from app.main import process_s3_event

class FakeGeoJSON(dict):
    def __init__(self, is_valid):
        super().__init__()
        self.is_valid = is_valid
        self["type"] = "FeatureCollection"
        self["features"] = [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [1, 2]},
                "properties": {}
            }
        ]

@pytest.fixture
def fake_event():
    return {"Body": '{"Records":[{"s3":{"bucket":{"name":"bucket"},"object":{"key":"file.geojson"}}}]}'}

@patch("app.main.fetch_db_credentials")
@patch("app.main.connect_postgres")
@patch("app.main.s3")
@patch("app.main.geojson.loads")
def test_process_s3_event_valid_geojson(mock_geojson_loads, mock_s3, mock_connect_postgres, mock_fetch_db_credentials, fake_event):
    """Should proceed when is_valid is True"""
    mock_geojson_loads.return_value = FakeGeoJSON(is_valid=True)
    mock_s3.get_object.return_value = {
        'Body': MagicMock(read=MagicMock(return_value=b"{}"))
    }
    mock_fetch_db_credentials.return_value = {"username": "user", "password": "pass"}
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect_postgres.return_value.__enter__.return_value = mock_conn

    process_s3_event(fake_event)

    assert mock_connect_postgres.called
    assert mock_cursor.execute.called

@patch("app.main.fetch_db_credentials")
@patch("app.main.connect_postgres")
@patch("app.main.s3")
@patch("app.main.geojson.loads")
def test_process_s3_event_invalid_geojson(mock_geojson_loads, mock_s3, mock_connect_postgres, mock_fetch_db_credentials, fake_event, caplog):
    """Should NOT proceed when is_valid is False"""
    mock_geojson_loads.return_value = FakeGeoJSON(is_valid=False)
    mock_s3.get_object.return_value = {
        'Body': MagicMock(read=MagicMock(return_value=b"{}"))
    }

    process_s3_event(fake_event)

    assert "Invalid GeoJSON" in caplog.text
    assert not mock_connect_postgres.called
