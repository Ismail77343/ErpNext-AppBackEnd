import frappe

from mobile_api.services.lead_service import LeadService


@frappe.whitelist()
def get_leads(limit_start=0, limit_page_length=20, status=None, search=None):
    try:
        return LeadService.get_leads(
            limit_start=limit_start,
            limit_page_length=limit_page_length,
            status=status,
            search=search,
        )
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "get_leads")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def get_lead_details(lead_name):
    try:
        return LeadService.get_lead_details(lead_name)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "get_lead_details")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def get_lead_follow_ups(lead_name):
    try:
        return LeadService.get_lead_follow_ups(lead_name)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "get_lead_follow_ups")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def get_lead_required_fields(lead_name=None, data=None, **kwargs):
    try:
        return LeadService.get_required_fields(lead_name=lead_name, data=data, **kwargs)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "get_lead_required_fields")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def create_lead(data=None, **kwargs):
    try:
        return LeadService.create_lead(data=data, **kwargs)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "create_lead")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def update_lead(lead_name, data=None, **kwargs):
    try:
        return LeadService.update_lead(lead_name=lead_name, data=data, **kwargs)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "update_lead")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def add_lead_follow_up(lead_name, follow_up_date, expected_result_date, details, attachment=None):
    try:
        return LeadService.add_follow_up(
            lead_name=lead_name,
            follow_up_date=follow_up_date,
            expected_result_date=expected_result_date,
            details=details,
            attachment=attachment,
        )
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "add_lead_follow_up")
        return {"status": "error", "message": str(exc)}
