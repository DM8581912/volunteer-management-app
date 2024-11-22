from flask import Blueprint, request, jsonify
from io import StringIO, BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import csv
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Create the blueprint
reporting = Blueprint('reporting', __name__)

# Helper Functions
def generate_csv(data, headers):
    """Generate a CSV file from data."""
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(data)
    output.seek(0)
    return output.getvalue()

def generate_pdf(data, headers, title):
    """Generate a PDF file from data."""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle(title)

    # Add title
    pdf.drawString(100, 750, title)

    # Add table headers
    y = 720
    pdf.drawString(50, y, " | ".join(headers))
    y -= 20

    # Add table rows
    for row in data:
        pdf.drawString(50, y, " | ".join(map(str, row)))
        y -= 20
        if y < 50:  # Add a new page if content exceeds the current page
            pdf.showPage()
            y = 750

    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()

# Reporting Route for Events
@reporting.route('/reports/events', methods=['GET'])
def events_report():
    """Generate a report for all events in the Supabase database."""
    try:
        # Fetch events from Supabase
        events_response = supabase.table('events').select("*").execute()
        events = events_response.data

        if not events:
            return jsonify({"error": "No events found"}), 404

        # Prepare report data
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

        # Determine format from query parameters
        report_format = request.args.get('format', 'csv').lower()

        if report_format == 'csv':
            csv_data = generate_csv(report_data, headers)
            return csv_data, 200, {'Content-Type': 'text/csv', 'Content-Disposition': 'attachment; filename=events_report.csv'}
        elif report_format == 'pdf':
            pdf_data = generate_pdf(report_data, headers, "Events Report")
            return pdf_data, 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=events_report.pdf'}
        else:
            return jsonify({"error": "Unsupported format. Use 'csv' or 'pdf'."}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Reporting Route for Volunteer History
@reporting.route('/reports/volunteerhistory', methods=['GET'])
def volunteer_history_report():
    """Generate a report for all volunteer history in the Supabase database."""
    try:
        # Fetch volunteer history from Supabase
        volunteer_response = supabase.table('volunteerhistory').select("*").execute()
        volunteer_history = volunteer_response.data

        if not volunteer_history:
            return jsonify({"error": "No volunteer history found"}), 404

        # Prepare report data
        headers = [
            "ID", "Username", "Event ID", "Date Volunteered", "Created At", "Hours Contributed",
            "Required Skills", "Urgency", "Feedback", "Description", "Event Name", "Location", "Participation Status"
        ]
        report_data = [
            [
                entry.get('id', 'N/A'),
                entry.get('username', 'N/A'),
                entry.get('eventid', 'N/A'),
                entry.get('datevolunteered', 'N/A'),
                entry.get('createdat', 'N/A'),
                entry.get('hourscontributed', 'N/A'),
                ", ".join(entry.get('requiredskills', [])),
                entry.get('urgency', 'N/A'),
                entry.get('feedback', 'N/A'),
                entry.get('description', 'N/A'),
                entry.get('eventname', 'N/A'),
                entry.get('location', 'N/A'),
                entry.get('participationstatus', 'N/A'),
            ]
            for entry in volunteer_history
        ]

        # Determine format from query parameters
        report_format = request.args.get('format', 'csv').lower()

        if report_format == 'csv':
            csv_data = generate_csv(report_data, headers)
            return csv_data, 200, {'Content-Type': 'text/csv', 'Content-Disposition': 'attachment; filename=volunteerhistory_report.csv'}
        elif report_format == 'pdf':
            pdf_data = generate_pdf(report_data, headers, "Volunteer History Report")
            return pdf_data, 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=volunteerhistory_report.pdf'}
        else:
            return jsonify({"error": "Unsupported format. Use 'csv' or 'pdf'."}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
  
