import json
import io
import base64
from jinja2 import Template
from xhtml2pdf import pisa

def convert_html_to_pdf(source_html):
    """Converts HTML to PDF using xhtml2pdf and returns the PDF data as bytes."""
    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(src=source_html, dest=result)
    if pisa_status.err:
        return None
    pdf_data = result.getvalue()
    result.close()
    return pdf_data

def handler(request):
    # Only allow POST requests
    if request.method != "POST":
        return {
            "statusCode": 405,
            "body": "Method Not Allowed"
        }
    
    # Parse the JSON body
    try:
        if isinstance(request.body, str):
            data = json.loads(request.body)
        else:
            data = request.body
    except Exception as e:
        return {
            "statusCode": 400,
            "body": "Invalid JSON data"
        }
    
    # Define an HTML template using Jinja2
    html_template = """
    <html>
      <head>
        <meta charset="utf-8">
        <style>
          body { font-family: Arial, sans-serif; margin: 40px; }
          h1 { text-align: center; }
          .field { margin-bottom: 10px; }
          .label { font-weight: bold; }
        </style>
      </head>
      <body>
        <h1>{{ form_title }}</h1>
        {% for key, value in submission.items() %}
          <div class="field">
            <span class="label">{{ key }}:</span> {{ value }}
          </div>
        {% endfor %}
      </body>
    </html>
    """

    # Render the HTML with data from the JSON
    template = Template(html_template)
    # Adjust the paths based on your JSON structure
    form_title = data.get("body", {}).get("form_title", "Untitled Form")
    submission = data.get("body", {}).get("submission", {})
    rendered_html = template.render(form_title=form_title, submission=submission)

    # Convert the rendered HTML to PDF
    pdf_data = convert_html_to_pdf(rendered_html)
    if pdf_data is None:
        return {
            "statusCode": 500,
            "body": "Failed to generate PDF"
        }
    
    # Encode the PDF data in base64
    pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
    
    # Set headers to return a PDF file
    headers = {
        "Content-Type": "application/pdf",
        "Content-Disposition": "attachment; filename=generated.pdf"
    }
    
    return {
        "statusCode": 200,
        "isBase64Encoded": True,
        "headers": headers,
        "body": pdf_base64
    }
