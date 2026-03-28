import frappe

from mobile_api.services.quotation_service import QuotationService


@frappe.whitelist()
def get_quotations(limit_start=0, limit_page_length=20, status=None, search=None, follow_up_filter=None, sort_by=None):
    try:
        return QuotationService.get_quotations(
            limit_start=limit_start,
            limit_page_length=limit_page_length,
            status=status,
            search=search,
            follow_up_filter=follow_up_filter,
            sort_by=sort_by,
        )
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "get_quotations")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def get_quotations_dashboard_summary(status=None, search=None):
    try:
        return QuotationService.get_quotations_dashboard_summary(status=status, search=search)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "get_quotations_dashboard_summary")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def get_quotation_details(quotation_name, print_format=None):
    try:
        return QuotationService.get_quotation_details(quotation_name, print_format=print_format)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "get_quotation_details")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def get_quotation_print_data(quotation_name, print_format=None):
    try:
        return QuotationService.get_quotation_print_data(quotation_name, print_format=print_format)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "get_quotation_print_data")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def get_quotation_follow_ups(quotation_name):
    try:
        return QuotationService.get_quotation_follow_ups(quotation_name)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "get_quotation_follow_ups")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def add_quotation_follow_up(quotation_name, follow_up_date, expected_result_date, details, attachment=None):
    try:
        return QuotationService.add_follow_up(
            quotation_name=quotation_name,
            follow_up_date=follow_up_date,
            expected_result_date=expected_result_date,
            details=details,
            attachment=attachment,
        )
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "add_quotation_follow_up")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def get_quotation_workflow_actions(quotation_name):
    try:
        return QuotationService.get_workflow_actions(quotation_name)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "get_quotation_workflow_actions")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def execute_quotation_workflow_action(quotation_name, action):
    try:
        return QuotationService.execute_workflow_action(quotation_name, action)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "execute_quotation_workflow_action")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def send_quotation_for_approval(quotation_name, action=None):
    try:
        return QuotationService.send_for_approval(quotation_name, action)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "send_quotation_for_approval")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def return_quotation_workflow(quotation_name, action=None):
    try:
        return QuotationService.return_workflow(quotation_name, action)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "return_quotation_workflow")
        return {"status": "error", "message": str(exc)}
