"""Set up testing as in this example.
http://docs.pylonsproject.org/projects/pyramid/en/latest/tutorials/wiki2/tests.html
"""

import re

from sqlalchemy import func
from sqlalchemy.orm.session import Session
from datetime import datetime

class TestDatabase:
    def test_version(self, session_tm: Session) -> None:
        v = session_tm.query(func.version()).one()[0]
        assert re.match(r"PostgreSQL 1(3|4|5|6)\.", v)


class TestApp:
    def test_timeseries_api_no_filters(self, testapp, session_tm, populate_timeseries_data):
        """Test timeseries API endpoint with no filters."""
        # Call the API without any filters
        res = testapp.get("/api/v1/timeseries", status=200)
        # Assertions
        assert res.content_type == "application/json"
        assert len(res.json) > 0  # Ensure the response contains data
        assert {"id", "datetime", "value"}.issubset(res.json[0].keys())  # Check keys

    def test_timeseries_api_filters_double(self, testapp, session_tm, populate_timeseries_data):
        """Test timeseries API endpoint with filters."""
        # Filter by a specific datetime range (valid filter)
        start_date = "2022-01-01"
        end_date = "2024-01-01"
        # Call the API with the filters
        res = testapp.get(f"/api/v1/timeseries?from={start_date}&to={end_date}", status=200)
        # Assertions for valid datetime filters
        assert res.content_type == "application/json"
        assert len(res.json) > 0  # Ensure the response contains data

        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
        for item in res.json:
            item_datetime = datetime.strptime(item["datetime"], "%Y-%m-%dT%H:%M:%S")
            assert start_datetime <= item_datetime <= end_datetime
       
    def test_timeseries_api_filters_single(self, testapp, session_tm, populate_timeseries_data):
        """Test timeseries API endpoint with filters."""
        # Filter by a start date
        start_date = "2022-01-01"
        # Call the API with the filters
        res = testapp.get(f"/api/v1/timeseries?from={start_date}", status=200)
        # Assertions for valid datetime filters
        assert res.content_type == "application/json"
        assert len(res.json) > 0  # Ensure the response contains data

        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        for item in res.json:
            item_datetime = datetime.strptime(item["datetime"], "%Y-%m-%dT%H:%M:%S")
            assert start_datetime <= item_datetime

        # Filter by a end date
        end_date = "2024-01-01"
        # Call the API with the filters
        res = testapp.get(f"/api/v1/timeseries?to={end_date}", status=200)
        # Assertions for valid datetime filters
        assert res.content_type == "application/json"
        assert len(res.json) > 0  # Ensure the response contains data

        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
        for item in res.json:
            item_datetime = datetime.strptime(item["datetime"], "%Y-%m-%dT%H:%M:%S")
            assert item_datetime <= end_datetime

    def test_timeseries_api_filters_invalid(self, testapp, session_tm, populate_timeseries_data):
        """Test timeseries API endpoint with filters."""
        # Filter by a start date
        start_date = "now"
        # Call the API with the filters
        res = testapp.get(f"/api/v1/timeseries?from={start_date}", status=200)
        # Assertions for valid datetime filters
        assert res.content_type == "application/json"
        assert len(res.json) > 0  # Ensure the response contains data
        assert {"Error" : "Invalid date format. use YYYY-MM-DD."} == res.json
