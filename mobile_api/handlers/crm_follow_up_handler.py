import frappe

from mobile_api.services.crm_follow_up_service import CRMFollowUpService


@frappe.whitelist()
def get_crm_doc_details(doctype, docname):
    try:
        return CRMFollowUpService.get_document_with_follow_up(doctype, docname)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "get_crm_doc_details")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def add_crm_follow_up(doctype, docname, follow_up_date, expected_result_date, details, attachment=None):
    try:
        return CRMFollowUpService.add_follow_up(
            doctype=doctype,
            docname=docname,
            follow_up_date=follow_up_date,
            expected_result_date=expected_result_date,
            details=details,
            attachment=attachment,
        )
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "add_crm_follow_up")
        return {"status": "error", "message": str(exc)}
