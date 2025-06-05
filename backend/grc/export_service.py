import json
import os
import uuid
import datetime
import boto3
import mysql.connector
from mysql.connector import pooling
import pandas as pd
from io import BytesIO
import xmltodict
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4, landscape
from botocore.exceptions import ClientError
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from django.utils import timezone

# Database connection pool
db_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="export_pool",
    pool_size=5,
    host=os.environ.get('DB_HOST', 'localhost'),
    user=os.environ.get('DB_USER', 'root'),
    password=os.environ.get('DB_PASSWORD', 'root'),
    database=os.environ.get('DB_NAME', 'grc')
)

# AWS S3 Configuration
AWS_BUCKET_NAME = "grc-files-vardaan"
AWS_REGION = "us-east-1"
AWS_ACCESS_KEY_ID = "AKIAW76SPJ4WHBIR5DPJ"
AWS_SECRET_ACCESS_KEY = "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"

# Initialize S3 client
try:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
except Exception as e:
    print(f"Error initializing S3 client: {str(e)}")
    s3_client = None

def ensure_bucket_exists():
    """Ensure the S3 bucket exists"""
    try:
        s3_client.head_bucket(Bucket=AWS_BUCKET_NAME)
    except ClientError:
        try:
            s3_client.create_bucket(
                Bucket=AWS_BUCKET_NAME,
                CreateBucketConfiguration={'LocationConstraint': AWS_REGION}
            )
        except Exception as e:
            print(f"Error creating bucket: {str(e)}")
            return False
    return True

# Try to ensure bucket exists on module import
try:
    ensure_bucket_exists()
except Exception as e:
    print(f"Warning: Could not ensure S3 bucket exists: {str(e)}")
    print("File uploads to S3 may fail - will save files locally instead")

# Sample data for testing
SAMPLE_DATA = [
    {"id": 1, "name": "John Doe", "email": "john@example.com", "department": "IT", "salary": 75000},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "department": "HR", "salary": 65000},
    {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "department": "Marketing", "salary": 60000},
    {"id": 4, "name": "Alice Brown", "email": "alice@example.com", "department": "Finance", "salary": 80000},
    {"id": 5, "name": "Charlie Wilson", "email": "charlie@example.com", "department": "IT", "salary": 70000}
]

def get_db_connection():
    """Get a connection from the connection pool"""
    return db_pool.get_connection()

def save_export_record(export_data):
    """Save export record to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO exported_files 
               (export_data, file_type, user_id, status, created_at, updated_at)
               VALUES (%s, %s, %s, 'pending', %s, %s)
               RETURNING id""",
            (json.dumps(export_data), export_data['file_type'], 
             export_data['user_id'], datetime.datetime.now(), 
             datetime.datetime.now())
        )
        export_id = cursor.fetchone()[0]
        conn.commit()
        return export_id
    finally:
        cursor.close()
        conn.close()

def update_export_status(export_id, status, error=None):
    """Update export record status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
        UPDATE exported_files 
        SET status = %s, error = %s, updated_at = %s
        """
        
        params = [status, error, datetime.datetime.now()]
        
        if status == 'completed':
            query += ", completed_at = %s"
            params.append(datetime.datetime.now())
            
        query += " WHERE id = %s"
        params.append(export_id)
        
        cursor.execute(query, params)
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def update_export_metadata(export_id, metadata):
    """Update export metadata"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get existing metadata
        cursor.execute("SELECT metadata FROM exported_files WHERE id = %s", (export_id,))
        result = cursor.fetchone()
        
        if result:
            existing_metadata = json.loads(result[0] or '{}')
            updated_metadata = {**existing_metadata, **metadata}
            
            cursor.execute(
                "UPDATE exported_files SET metadata = %s, updated_at = %s WHERE id = %s",
                (json.dumps(updated_metadata), datetime.datetime.now(), export_id)
            )
            conn.commit()
    finally:
        cursor.close()
        conn.close()

def update_export_url(export_id, s3_url):
    """Update export record with S3 URL"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE exported_files SET s3_url = %s, updated_at = %s WHERE id = %s",
            (s3_url, datetime.datetime.now(), export_id)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def export_to_excel(data):
    """Export data to Excel format"""
    try:
        # Convert data to DataFrame
        df = pd.DataFrame(data)
        
        # Create Excel file in memory
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        
        return excel_buffer.getvalue()
    except Exception as e:
        print(f"Error in export_to_excel: {str(e)}")
        raise

def export_to_csv(data):
    """Export data to CSV format"""
    try:
        # Convert data to DataFrame
        df = pd.DataFrame(data)
        
        # Create CSV string
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False)
        
        return csv_buffer.getvalue()
    except Exception as e:
        print(f"Error in export_to_csv: {str(e)}")
        raise

def export_to_json(data):
    """Export data to JSON format"""
    try:
        return json.dumps(data, indent=2).encode('utf-8')
    except Exception as e:
        print(f"Error in export_to_json: {str(e)}")
        raise

def export_to_xml(data):
    """Export data to XML format"""
    try:
        xml = dicttoxml(data, custom_root='compliances', attr_type=False)
        return xml
    except Exception as e:
        print(f"Error in export_to_xml: {str(e)}")
        raise

def export_to_pdf(data):
    buffer = BytesIO()
    
    # Use A4 Landscape with minimal margins
    page_width, page_height = landscape(A4)
    
    # Create the PDF object with minimal margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=15,
        leftMargin=15,
        topMargin=15,
        bottomMargin=15
    )
    
    # Available width for table (page width minus margins)
    available_width = page_width - 30
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Header style
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=7,
        textColor=colors.white,
        alignment=1,
        backColor=colors.navy,
        leading=8
    )
    
    # Cell style with improved word wrap
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=6.5,
        leading=8,
        wordWrap='CJK',
        spaceBefore=2,
        spaceAfter=2
    )
    
    elements = []
    
    if data:
        headers = list(data[0].keys())
        
        # Define column width units based on content type
        width_units = {
            'Compliance ID': 5,
            'Description': 25,  # Increased for better text display
            'Status': 5,
            'Criticality': 5,
            'Maturity Level': 5,
            'Type': 5,
            'Implementation': 5,
            'Created By': 7,
            'Created Date': 8,
            'Version': 4,
            'Identifier': 8,
            'Active/Inactive': 5,
            'Is Risk': 3,
            'SubPolicy': 5,
            'Policy': 5,
            'Framework': 5
        }
        
        # Calculate column widths
        col_widths = []
        for header in headers:
            width = width_units.get(header, 5)
            col_widths.append((width / 100) * available_width)
        
        # Prepare table data with improved text handling
        table_data = [[Paragraph(str(header).replace('_', ' '), header_style) for header in headers]]
        
        for row in data:
            table_row = []
            for header in headers:
                value = str(row[header])
                
                # Special handling for different field types
                if header == 'Description':
                    if len(value) > 300:  # Allow longer descriptions
                        value = value[:297] + '...'
                    cell = Paragraph(value, cell_style)
                elif header == 'Created Date':
                    # Format date consistently
                    try:
                        if isinstance(value, str):
                            value = value.split('.')[0]  # Remove microseconds if present
                    except:
                        pass
                    cell = Paragraph(value, cell_style)
                else:
                    cell = Paragraph(value, cell_style)
                
                table_row.append(cell)
            table_data.append(table_row)
        
        # Create table with improved settings
        table = Table(
            table_data,
            colWidths=col_widths,
            repeatRows=1,
            splitByRow=True
        )
        
        # Enhanced table style
        table.setStyle(TableStyle([
            # Headers
            ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('TOPPADDING', (0, 0), (-1, 0), 4),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
            
            # Cells
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 6.5),
            ('TOPPADDING', (0, 1), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            
            # Alignment
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        
        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=10,
            spaceAfter=10,
            alignment=1
        )
        title = Paragraph("Compliance Report", title_style)
        elements.append(title)
        
        # Add timestamp using Django's timezone
        metadata_style = ParagraphStyle(
            'Metadata',
            parent=styles['Normal'],
            fontSize=7,
            textColor=colors.grey,
            spaceAfter=10
        )
        
        # Use Django's timezone.now() instead of datetime.now()
        current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        timestamp = Paragraph(f"Generated on: {current_time}", metadata_style)
        elements.append(timestamp)
        
        # Add the table
        elements.append(table)
        
        # Build PDF
        doc.build(elements)
        
        pdf = buffer.getvalue()
        buffer.close()
        return pdf
    
    else:
        # Handle empty data case
        title = Paragraph(
            "Compliance Report - No Data",
            styles['Heading1']
        )
        elements.append(title)
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

def export_to_txt(data):
    """Export data to Text format"""
    buffer = BytesIO()
    
    buffer.write(b"Export Report\n")
    buffer.write(b"=" * 50 + b"\n\n")
    buffer.write(f"Generated: {datetime.datetime.now().isoformat()}\n\n".encode('utf-8'))
    
    def format_item(item, level=0):
        indent = "  " * level
        
        if isinstance(item, list):
            for i, element in enumerate(item):
                buffer.write(f"{indent}Item {i+1}:\n".encode('utf-8'))
                format_item(element, level + 1)
        elif isinstance(item, dict):
            for key, value in item.items():
                if isinstance(value, (dict, list)):
                    buffer.write(f"{indent}{key}:\n".encode('utf-8'))
                    format_item(value, level + 1)
                else:
                    buffer.write(f"{indent}{key}: {value}\n".encode('utf-8'))
        else:
            buffer.write(f"{indent}{item}\n".encode('utf-8'))
    
    format_item(data)
    
    buffer.write(b"\n" + b"=" * 50 + b"\n")
    buffer.write(b"End of Report")
    
    buffer.seek(0)
    return buffer.getvalue()

def upload_to_s3(file_buffer, file_name, content_type):
    """Upload file to S3 and return URL"""
    ensure_bucket_exists()
    s3_client = boto3.client('s3')
    file_buffer.seek(0)
    s3_client.upload_fileobj(
        file_buffer,
        AWS_BUCKET_NAME,
        file_name,
        ExtraArgs={'ContentType': content_type}
    )
    return f"https://{AWS_BUCKET_NAME}.s3.amazonaws.com/{file_name}"

def get_content_type(file_type):
    """Get content type based on file extension"""
    content_types = {
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'pdf': 'application/pdf',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'csv': 'text/csv',
        'json': 'application/json',
        'xml': 'application/xml',
        'txt': 'text/plain'
    }
    
    return content_types.get(file_type, 'application/octet-stream')

def export_data(data=None, file_format='xlsx', user_id='user123', options=None):
    """Main export function that handles different formats"""
    try:
        # Create export record
        export_id = save_export_record({
            'file_type': file_format,
            'user_id': user_id
        })
        
        # Update status to processing
        update_export_status(export_id, 'processing')
        
        # Export based on format
        if file_format == 'xlsx':
            file_buffer = export_to_excel(data)
        elif file_format == 'csv':
            file_buffer = export_to_csv(data)
        elif file_format == 'pdf':
            file_buffer = export_to_pdf(data)
        elif file_format == 'json':
            file_buffer = export_to_json(data)
        elif file_format == 'xml':
            file_buffer = export_to_xml(data)
        else:
            raise ValueError(f"Unsupported format: {file_format}")
        
        # Generate filename
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"compliances_export_{timestamp}.{file_format}"
        
        # Upload to S3
        content_type = get_content_type(file_format)
        s3_url = upload_to_s3(file_buffer, file_name, content_type)
        
        # Update export record with S3 URL
        update_export_url(export_id, s3_url)
        
        # Update status to completed
        update_export_status(export_id, 'completed')
        
        return {
            'success': True,
            'file_name': file_name,
            's3_url': s3_url,
            'export_id': export_id
        }
        
    except Exception as e:
        if export_id:
            update_export_status(export_id, 'failed', str(e))
            raise

# Example usage with sample data
if __name__ == "__main__":
    result = export_data(SAMPLE_DATA, 'xlsx', 'test_user')
    print(f"Export successful. File URL: {result['s3_url']}") 