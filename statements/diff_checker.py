from statements.all_imports_for_diff_checker import *
from company_mapper import *
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
from flask import send_file


def missing_doc_and_wrong_amount(bc_balance, vendor_balance, obj):
    missing_documents = {}
    wrong_amounts = {}

    print(vendor_balance)
    # print(bc_balance)

    for inv, value in vendor_balance.items():
        if str(inv) not in bc_balance:
            missing_documents[inv] = value
        else:
            diff = float(value) + float(bc_balance[str(inv)])
            if abs(diff) > 3:
                wrong_amounts[inv] = diff

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    y = 800
    p.setFont("Helvetica", 12)
    p.drawString(100, y, f"Company name: {obj.__class__.__name__.replace('Model', '')}")
    y -= 20
    p.drawString(100, y, f"Account No. in BC: {', '.join(find_account_number())}")

    y -= 40
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, y, "Missing Documents:")
    y -= 20

    p.setFont("Helvetica", 12)
    if not missing_documents:
        p.drawString(120, y, "There are no missing invoices")
        y -= 20
    else:
        for inv, amount in missing_documents.items():
            p.drawString(120, y, f"Invoice {inv}, amount: {amount}")
            y -= 20

    y -= 20
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, y, "Wrong Invoices:")
    y -= 20

    p.setFont("Helvetica", 12)
    if not wrong_amounts:
        p.drawString(120, y, "There are no wrong invoices")
    else:
        for inv, amount in wrong_amounts.items():
            p.drawString(120, y, f"Invoice {inv}, amount: {amount}")
            y -= 20
            if y < 50:
                p.showPage()
                y = 800
                p.setFont("Helvetica", 12)

    p.showPage()
    p.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="analysis_report.pdf", mimetype='application/pdf')

