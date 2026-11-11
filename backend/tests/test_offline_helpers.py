"""Offline unit tests for the pure helper functions in app.py and reporting.py.

These tests need no Supabase project. app.py and reporting.py build a Supabase
client at import time, so placeholder credentials are supplied (only when real
ones are absent) just for the import. Creating the client makes no network
call, and none of the functions tested here touch the database.
"""
import csv
import io
import os
import unittest
from unittest import mock

_PLACEHOLDER_ENV = {
    "SUPABASE_URL": os.getenv("SUPABASE_URL") or "http://localhost:54321",
    "SUPABASE_KEY": os.getenv("SUPABASE_KEY") or "placeholder.offline.key",
}

with mock.patch.dict(os.environ, _PLACEHOLDER_ENV):
    from app import EVENT_SCHEMA, USER_SCHEMA, calculate_match_score, validate_data
    from reporting import generate_csv, generate_pdf


class CalculateMatchScoreTests(unittest.TestCase):
    def test_full_match_is_case_insensitive(self):
        self.assertEqual(calculate_match_score(["First Aid", "CPR"], ["first aid", "cpr"]), 100)

    def test_partial_match(self):
        self.assertEqual(calculate_match_score(["First Aid"], ["First Aid", "Cooking"]), 50)

    def test_no_overlap(self):
        self.assertEqual(calculate_match_score(["Driving"], ["Cooking"]), 0)

    def test_empty_inputs_score_zero(self):
        self.assertEqual(calculate_match_score([], ["Cooking"]), 0)
        self.assertEqual(calculate_match_score(["Cooking"], []), 0)


class ValidateDataTests(unittest.TestCase):
    def valid_event(self):
        return {
            "eventName": "Food Drive",
            "location": "Houston, TX",
            "requiredSkills": ["Cooking"],
            "urgency": "high",
            "eventDate": "2024-12-01",
        }

    def test_valid_event_has_no_errors(self):
        self.assertEqual(validate_data(self.valid_event(), EVENT_SCHEMA), [])

    def test_missing_required_field(self):
        event = self.valid_event()
        del event["location"]
        self.assertIn("location is required.", validate_data(event, EVENT_SCHEMA))

    def test_invalid_urgency(self):
        event = self.valid_event()
        event["urgency"] = "urgent"
        errors = validate_data(event, EVENT_SCHEMA)
        self.assertTrue(any(e.startswith("urgency must be one of") for e in errors))

    def test_short_username_and_password(self):
        user = {"username": "ab", "password": "123", "email": "a@example.com"}
        errors = validate_data(user, USER_SCHEMA)
        self.assertIn("username must be at least 3 characters.", errors)
        self.assertIn("password must be at least 6 characters.", errors)


class ReportGenerationTests(unittest.TestCase):
    def test_generate_csv_writes_header_and_rows(self):
        output = generate_csv([["alice", 5], ["bob", 3]], ["username", "hours"])
        rows = list(csv.reader(io.StringIO(output)))
        self.assertEqual(rows, [["username", "hours"], ["alice", "5"], ["bob", "3"]])

    def test_generate_pdf_returns_pdf_bytes(self):
        pdf = generate_pdf([["alice", 5]], ["username", "hours"], "Volunteer Report")
        self.assertTrue(pdf.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
