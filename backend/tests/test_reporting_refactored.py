"""Unit tests for reporting.py - CSV/PDF generation and report routes."""

import json
import pytest
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Patch before import
with patch.dict(os.environ, {
    'SUPABASE_URL': 'https://fake.supabase.co',
    'SUPABASE_KEY': 'fake-key'
}):
    with patch('supabase.create_client', return_value=MagicMock()):
        for mod_name in list(sys.modules.keys()):
            if mod_name in ('app', 'reporting'):
                del sys.modules[mod_name]
        import reporting as reporting_module
        import app as app_module


class TestGenerateCsv:
    """Tests for the generate_csv function."""

    def test_csv_with_data(self):
        headers = ["Name", "Age"]
        data = [["Alice", "30"], ["Bob", "25"]]
        result = reporting_module.generate_csv(data, headers)
        lines = [line.strip() for line in result.strip().split('\n')]
        assert lines[0] == 'Name,Age'
        assert lines[1] == 'Alice,30'
        assert lines[2] == 'Bob,25'

    def test_csv_empty_data(self):
        headers = ["Name", "Age"]
        data = []
        result = reporting_module.generate_csv(data, headers)
        lines = result.strip().split('\n')
        assert len(lines) == 1  # only header
        assert lines[0] == 'Name,Age'

    def test_csv_special_characters(self):
        headers = ["Name"]
        data = [["O'Brien, Jr."]]
        result = reporting_module.generate_csv(data, headers)
        assert "O'Brien" in result


class TestGeneratePdf:
    """Tests for the generate_pdf function."""

    def test_pdf_returns_bytes(self):
        headers = ["Name"]
        data = [["Alice"]]
        result = reporting_module.generate_pdf(data, headers, "Test Report")
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_pdf_starts_with_pdf_header(self):
        headers = ["Name"]
        data = [["Alice"]]
        result = reporting_module.generate_pdf(data, headers, "Test Report")
        assert result[:5] == b'%PDF-'

    def test_pdf_empty_data(self):
        headers = ["Name"]
        data = []
        result = reporting_module.generate_pdf(data, headers, "Test Report")
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_pdf_many_rows_pagination(self):
        headers = ["Name"]
        data = [[f"Person {i}"] for i in range(100)]
        result = reporting_module.generate_pdf(data, headers, "Big Report")
        assert isinstance(result, bytes)
        assert len(result) > 0


class TestExtractFunctions:
    """Tests for extract_event_row and extract_volunteer_history_row."""

    def test_extract_event_row_full_data(self):
        event = {
            'eventName': 'Cleanup',
            'location': 'Park',
            'requiredSkills': ['organizing'],
            'urgency': 'high',
            'eventDate': '2025-01-01',
            'createdAt': '2025-01-01T00:00:00'
        }
        row = reporting_module.extract_event_row(event)
        assert row[0] == 'Cleanup'
        assert row[2] == 'organizing'

    def test_extract_event_row_missing_fields(self):
        event = {}
        row = reporting_module.extract_event_row(event)
        assert all(v == 'N/A' or v == '' for v in row)

    def test_extract_volunteer_history_row(self):
        entry = {
            'id': '123',
            'username': 'alice',
            'eventid': '456',
            'datevolunteered': '2025-01-01',
            'createdat': '2025-01-01T00:00:00',
            'hourscontributed': 5,
            'requiredskills': ['python'],
            'urgency': 'low',
            'feedback': 'Great',
            'description': 'Test event',
            'eventname': 'Cleanup',
            'location': 'Park',
            'participationstatus': 'completed'
        }
        row = reporting_module.extract_volunteer_history_row(entry)
        assert row[0] == '123'
        assert row[1] == 'alice'
        assert len(row) == 13


class TestReportRoutes:
    """Tests for report API routes."""

    @pytest.fixture(autouse=True)
    def setup(self):
        app_module.app.config['TESTING'] = True
        self.client = app_module.app.test_client()

    @patch.object(reporting_module, 'supabase')
    def test_events_report_csv(self, mock_supabase):
        mock_supabase.table.return_value.select.return_value.execute.return_value = MagicMock(
            data=[{'eventName': 'Cleanup', 'location': 'Park', 'requiredSkills': ['organizing'],
                   'urgency': 'high', 'eventDate': '2025-01-01', 'createdAt': '2025-01-01'}]
        )
        response = self.client.get('/admin/reports/events?format=csv')
        assert response.status_code == 200
        assert 'text/csv' in response.content_type

    @patch.object(reporting_module, 'supabase')
    def test_events_report_no_data(self, mock_supabase):
        mock_supabase.table.return_value.select.return_value.execute.return_value = MagicMock(data=[])
        response = self.client.get('/admin/reports/events')
        assert response.status_code == 404

    @patch.object(reporting_module, 'supabase')
    def test_events_report_invalid_format(self, mock_supabase):
        mock_supabase.table.return_value.select.return_value.execute.return_value = MagicMock(
            data=[{'eventName': 'Test', 'location': 'NYC', 'requiredSkills': [],
                   'urgency': 'low', 'eventDate': '2025-01-01', 'createdAt': '2025-01-01'}]
        )
        response = self.client.get('/admin/reports/events?format=xml')
        assert response.status_code == 400

    @patch.object(reporting_module, 'supabase')
    def test_events_report_pdf(self, mock_supabase):
        mock_supabase.table.return_value.select.return_value.execute.return_value = MagicMock(
            data=[{'eventName': 'Cleanup', 'location': 'Park', 'requiredSkills': ['organizing'],
                   'urgency': 'high', 'eventDate': '2025-01-01', 'createdAt': '2025-01-01'}]
        )
        response = self.client.get('/admin/reports/events?format=pdf')
        assert response.status_code == 200
        assert 'application/pdf' in response.content_type

    @patch.object(reporting_module, 'supabase')
    def test_volunteer_history_report_csv(self, mock_supabase):
        mock_supabase.table.return_value.select.return_value.execute.return_value = MagicMock(
            data=[{'id': '1', 'username': 'alice', 'eventid': '2', 'datevolunteered': '2025-01-01',
                   'createdat': '2025-01-01', 'hourscontributed': 5, 'requiredskills': ['python'],
                   'urgency': 'low', 'feedback': 'Good', 'description': 'Test',
                   'eventname': 'Cleanup', 'location': 'Park', 'participationstatus': 'done'}]
        )
        response = self.client.get('/admin/reports/volunteerhistory?format=csv')
        assert response.status_code == 200

    @patch.object(reporting_module, 'supabase')
    def test_volunteer_history_report_no_data(self, mock_supabase):
        mock_supabase.table.return_value.select.return_value.execute.return_value = MagicMock(data=[])
        response = self.client.get('/admin/reports/volunteerhistory')
        assert response.status_code == 404
