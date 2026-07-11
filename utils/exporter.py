import csv
import os
from datetime import datetime
from PySide6.QtGui import QTextDocument

def export_to_csv(headers, rows, filepath):
    """Exports dataset to standard CSV format."""
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        return True, "CSV exported successfully."
    except Exception as e:
        return False, str(e)

def export_to_excel(headers, rows, filepath):
    """
    Exports dataset to an Excel-compatible XML/HTML format.
    This allows styling and opens natively in MS Excel without external libraries.
    """
    try:
        html = """
        <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">
        <head>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8">
        <style>
            table { border-collapse: collapse; font-family: 'Segoe UI', Arial, sans-serif; }
            th { background-color: #4f46e5; color: #ffffff; font-weight: bold; border: 1px solid #cbd5e1; padding: 8px; }
            td { border: 1px solid #cbd5e1; padding: 6px; }
            tr:nth-child(even) { background-color: #f8fafc; }
        </style>
        </head>
        <body>
        <table>
            <thead>
                <tr>
        """
        for h in headers:
            html += f"            <th>{h}</th>\n"
        html += """        </tr>
            </thead>
            <tbody>
        """
        for row in rows:
            html += "        <tr>\n"
            for cell in row:
                val = str(cell) if cell is not None else ""
                html += f"            <td>{val}</td>\n"
            html += "        </tr>\n"
        html += """    </tbody>
        </table>
        </body>
        </html>
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        return True, "Excel report exported successfully."
    except Exception as e:
        return False, str(e)

def export_to_pdf(title, headers, rows, filepath, company_info=None):
    """
    Exports dataset to a beautifully styled PDF document using PySide6's 
    built-in QTextDocument.printToPdf which converts HTML into a vector PDF.
    """
    try:
        # Resolve company details
        company_name = company_info.get("company_name", "SUN CRM Enterprise") if company_info else "SUN CRM Enterprise"
        company_addr = company_info.get("company_address", "") if company_info else ""
        company_phone = company_info.get("company_phone", "") if company_info else ""
        company_email = company_info.get("company_email", "") if company_info else ""
        
        date_str = datetime.now().strftime("%d-%b-%Y %I:%M %p")
        
        # HTML document structure
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    color: #1e293b;
                    margin: 20px;
                    font-size: 11px;
                }}
                .header-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 25px;
                }}
                .header-table td {{
                    border: none;
                    padding: 0;
                    vertical-align: top;
                }}
                .company-name {{
                    font-size: 18px;
                    font-weight: bold;
                    color: #4f46e5;
                    margin-bottom: 5px;
                }}
                .company-details {{
                    color: #64748b;
                    line-height: 1.4;
                }}
                .report-meta {{
                    text-align: right;
                }}
                .report-title {{
                    font-size: 16px;
                    font-weight: bold;
                    color: #0f172a;
                    margin-bottom: 5px;
                }}
                .report-date {{
                    color: #64748b;
                }}
                .divider {{
                    height: 2px;
                    background-color: #e2e8f0;
                    margin-bottom: 20px;
                }}
                .data-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }}
                .data-table th {{
                    background-color: #4f46e5;
                    color: #ffffff;
                    text-align: left;
                    font-weight: 600;
                    padding: 8px 10px;
                    border: 1px solid #e2e8f0;
                }}
                .data-table td {{
                    padding: 8px 10px;
                    border: 1px solid #e2e8f0;
                }}
                .data-table tr:nth-child(even) td {{
                    background-color: #f8fafc;
                }}
                .footer {{
                    margin-top: 30px;
                    text-align: center;
                    color: #94a3b8;
                    font-size: 9px;
                    border-top: 1px solid #e2e8f0;
                    padding-top: 10px;
                }}
            </style>
        </head>
        <body>
            <table class="header-table">
                <tr>
                    <td>
                        <div class="company-name">{company_name}</div>
                        <div class="company-details">
                            {company_addr}<br>
                            Ph: {company_phone} | Email: {company_email}
                        </div>
                    </td>
                    <td class="report-meta">
                        <div class="report-title">{title}</div>
                        <div class="report-date">Generated: {date_str}</div>
                    </td>
                </tr>
            </table>
            
            <div class="divider"></div>
            
            <table class="data-table">
                <thead>
                    <tr>
        """
        # Add Headers
        for h in headers:
            html += f"                    <th>{h}</th>\n"
        html += """            </tr>
                </thead>
                <tbody>
        """
        # Add Rows
        for row in rows:
            html += "                <tr>\n"
            for cell in row:
                val = str(cell) if cell is not None else ""
                html += f"                    <td>{val}</td>\n"
            html += "                </tr>\n"
        html += f"""        </tbody>
            </table>
            
            <div class="footer">
                SUN CRM Report | Page 1 of 1 | Thank you for using SUN CRM
            </div>
        </body>
        </html>
        """
        
        # Build document and print to PDF
        doc = QTextDocument()
        doc.setHtml(html)
        doc.printToPdf(filepath)
        return True, "PDF exported successfully."
    except Exception as e:
        return False, str(e)
