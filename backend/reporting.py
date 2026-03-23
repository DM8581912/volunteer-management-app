import logging
import csv
import os
from io import StringIO, BytesIO
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


def generate_csv(data, headers):
    """Generate a CSV string from row data and headers."""
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(data)
    output.seek(0)
    return output.getvalue()


def generate_pdf(data, headers, title):
    """Generate a PDF document from row data with headers and title."""
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


def build_report_response(data, headers, title, default_filename):
    """Build a CSV or PDF response based on the format query parameter."""
    report_format = request.args.get('format', 'csv').lower()

    if report_format == 'csv':
        csv_data = generate_csv(data, headers)
        return csv_data, 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename={default_filename}.csv'
        }
    elif report_format == 'pdf':
        pdf_data = generate_pdf(data, headers, title)
        return pdf_data, 200, {
            'Content-Type': 'application/pdf',
            'Content-Disposition': f'attachment; filename={default_filename}.pdf'
        }
    else:
        return jsonify({"error": "Unsupported format. Use 'csv' or 'pdf'."}), 400


@reporting.route('/reports/events', methods=['GET'])
def events_report():
    """Generate a report for all events."""
    try:
        events_response = supabase.table('events').select("*").execute()
        events = events_response.data

        if not events:
            return jsonify({"error": "No events found"}), 404

        headers = ["Event Name", "Location", "Required Skills", "Urgency", "Event Date", "Created At"]
        report_data = [
            [
                event.get('eventName', 'N/A'),
                event.get('location', 'N/A'),
                ", ".join(event.get('requiredSkills', [])),
                event.get('urgency', 'N/A'),
                event.get('eventDate', 'N/A'),
                event.get('createdAt', 'N/A'),
            ]
            for event in events
        ]

        return build_report_response(report_data, headers, "Events Report", "events_report")

    except Exception as e:
        logger.error("Failed to generate events report: %s", e)
        return jsonify({"error": str(e)}), 500


@reporting.route('/reports/volunteerhistory', methods=['GET'])
def volunteer_history_report():
    """Generate a report for all volunteer history."""
    try:
        volunteer_response = supabase.table('volunteerhistory').select("*").execute()
        volunteer_history = volunteer_response.data

        if not volunteer_history:
            return jsonify({"error": "No volunteer history found"}), 404

        headers = [
            "ID", "Username", "Event ID", "Date Volunteered", "Created At", "Hours Contributed",
            "Required Skills", "Urgency", "Feedback", "Description", "Event Name", "Location",
            "Participation Status"
        ]
        report_data = [
            [
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
            for entry in volunteer_history
        ]

        return build_report_response(
            report_data, headers, "Volunteer History Report", "volunteerhistory_report"
        )

    except Exception as e:
        logger.error("Failed to generate volunteer history report: %s", e)
        return jsonify({"error": str(e)}), 500
