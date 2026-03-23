import csv
import logging
import os
from io import StringIO, BytesIO
from typing import Optional

from flask import Blueprint, request, jsonify
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

reporting = Blueprint('reporting', __name__)

# Report column definitions
EVENT_REPORT_HEADERS = [
    "Event Name", "Location", "Required Skills", "Urgency", "Event Date", "Created At"
]

VOLUNTEER_HISTORY_HEADERS = [
    "ID", "Username", "Event ID", "Date Volunteered", "Created At",
    "Hours Contributed", "Required Skills", "Urgency", "Feedback",
    "Description", "Event Name", "Location", "Participation Status"
]


def generate_csv(data: list[list], headers: list[str]) -> str:
    """Generate CSV content from tabular data."""
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(data)
    output.seek(0)
    return output.getvalue()


def generate_pdf(data: list[list], headers: list[str], title: str) -> bytes:
    """Generate a PDF document from tabular data."""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle(title)

    pdf.drawString(100, 750, title)

    y_position = 720
    pdf.drawString(50, y_position, " | ".join(headers))
    y_position -= 20

    for row in data:
        pdf.drawString(50, y_position, " | ".join(map(str, row)))
        y_position -= 20
        if y_position < 50:
            pdf.showPage()
            y_position = 750

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


def build_report_response(data: list[list], headers: list[str],
                          title: str, report_format: str, filename_prefix: str):
    """Build a report response in either CSV or PDF format."""
    if report_format == 'csv':
        csv_data = generate_csv(data, headers)
        return csv_data, 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename={filename_prefix}_report.csv'
        }
    elif report_format == 'pdf':
        pdf_data = generate_pdf(data, headers, title)
        return pdf_data, 200, {
            'Content-Type': 'application/pdf',
            'Content-Disposition': f'attachment; filename={filename_prefix}_report.pdf'
        }
    else:
        return jsonify({"error": "Unsupported format. Use 'csv' or 'pdf'."}), 400


def extract_event_row(event: dict) -> list[str]:
    """Extract a single row of event data for reporting."""
    return [
        event.get('eventName', 'N/A'),
        event.get('location', 'N/A'),
        ", ".join(event.get('requiredSkills', [])),
        event.get('urgency', 'N/A'),
        event.get('eventDate', 'N/A'),
        event.get('createdAt', 'N/A'),
    ]


def extract_volunteer_history_row(entry: dict) -> list[str]:
    """Extract a single row of volunteer history data for reporting."""
    return [
        entry.get('id', 'N/A'),
        entry.get('username', 'N/A'),
        entry.get('eventid', 'N/A'),
        entry.get('datevolunteered', 'N/A'),
        entry.get('createdat', 'N/A'),
        entry.get('hourscontributed', 'N/A'),
        ", ".join(entry.get('requiredskills', []) or []),
        entry.get('urgency', 'N/A'),
        entry.get('feedback', 'N/A'),
        entry.get('description', 'N/A'),
        entry.get('eventname', 'N/A'),
        entry.get('location', 'N/A'),
        entry.get('participationstatus', 'N/A'),
    ]


@reporting.route('/reports/events', methods=['GET'])
def events_report():
    """Generate a report for all events."""
    try:
        events_response = supabase.table('events').select("*").execute()
        events = events_response.data

        if not events:
            return jsonify({"error": "No events found"}), 404

        report_data = [extract_event_row(event) for event in events]
        report_format = request.args.get('format', 'csv').lower()

        return build_report_response(
            report_data, EVENT_REPORT_HEADERS, "Events Report",
            report_format, "events"
        )
    except Exception as e:
        logger.exception("Failed to generate events report")
        return jsonify({"error": "Failed to generate report."}), 500


@reporting.route('/reports/volunteerhistory', methods=['GET'])
def volunteer_history_report():
    """Generate a report for all volunteer history."""
    try:
        volunteer_response = supabase.table('volunteerhistory').select("*").execute()
        volunteer_history = volunteer_response.data

        if not volunteer_history:
            return jsonify({"error": "No volunteer history found"}), 404

        report_data = [extract_volunteer_history_row(entry) for entry in volunteer_history]
        report_format = request.args.get('format', 'csv').lower()

        return build_report_response(
            report_data, VOLUNTEER_HISTORY_HEADERS, "Volunteer History Report",
            report_format, "volunteerhistory"
        )
    except Exception as e:
        logger.exception("Failed to generate volunteer history report")
        return jsonify({"error": "Failed to generate report."}), 500
