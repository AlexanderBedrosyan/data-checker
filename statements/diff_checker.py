from statements.all_imports_for_diff_checker import *
from company_mapper import *
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
from flask import send_file


def missing_doc_and_wrong_amount(bc_balance, vendor_balance, obj):
    missing_documents = {}
    wrong_amounts = {}

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

# def missing_doc_and_wrong_amount(bc_balance=dict, vendor_balance=dict, obj=object):
#     missing_documents = {}
#     wrong_amounts = {}
#     for inv, value in vendor_balance.items():
#         if str(inv) not in bc_balance:
#             missing_documents[inv] = value
#             continue
#
#         diff = float(value) + float(bc_balance[str(inv)])
#
#         if abs(diff) > 3:
#             wrong_amounts[inv] = diff
#
#     all_numbers = find_account_number()
#     print(f"Company name: {obj.__class__.__name__.replace('Model', '')}")
#     print(f"Account No. in BC: {', '.join(find_account_number())}")
#     print('===================================')
#     print(f"All missing documents:")
#     if not missing_documents:
#         print('There are no missing invoices')
#     else:
#         print('\n'.join(f'Invoice {inv}, amount: {amount}' for inv, amount in missing_documents.items()))
#
#     print('===================================')
#     print(f"All wrong invoices:")
#     if not wrong_amounts:
#         print('There are no wrong invoices')
#     else:
#         print('\n'.join(f'Invoice {inv}, amount: {amount}' for inv, amount in wrong_amounts.items()))
#
#     for inv, value in vendor_balance.items():
#         if str(inv) not in bc_balance:
#             missing_documents[inv] = value
#             continue
#
#         diff = float(value) + float(bc_balance[str(inv)])
#         if abs(diff) > 3:
#             wrong_amounts[inv] = diff
#
#     company_name = obj.__class__.__name__.replace('Model', '')
#     account_numbers = find_account_number()
#
#
#     report_lines = []
#     report_lines.append(f"Company name: {company_name}")
#     report_lines.append(f"Account No. in BC: {', '.join(account_numbers)}")
#     report_lines.append("===================================")
#     report_lines.append("All missing documents:")
#
#     if not missing_documents:
#         report_lines.append("There are no missing invoices")
#     else:
#         for inv, amount in missing_documents.items():
#             report_lines.append(f"Invoice {inv}, amount: {amount}")
#
#     report_lines.append("===================================")
#     report_lines.append("All wrong invoices:")
#
#     if not wrong_amounts:
#         report_lines.append("There are no wrong invoices")
#     else:
#         for inv, amount in wrong_amounts.items():
#             report_lines.append(f"Invoice {inv}, amount: {amount}")
#
#     # 2. Генерирай PDF
#     pdf_path = f"{company_name}_report.pdf"
#     c = canvas.Canvas(pdf_path, pagesize=A4)
#     width, height = A4
#     y = height - 40
#
#     for line in report_lines:
#         c.drawString(40, y, line)
#         y -= 20
#         if y < 40:
#             c.showPage()
#             y = height - 40
#
#     c.save()


# missing_doc_and_wrong_amount(bc_balance(), company_mapper["ah_fragt"].vendor_balance(), company_mapper["ah_fragt"])
