import frappe

from mobile_api.services.opportunity_service import OpportunityService


@frappe.whitelist()
def get_opportunity_workflow_actions(opportunity_name):
    try:
        return OpportunityService.get_workflow_actions(opportunity_name)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "get_opportunity_workflow_actions")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def execute_opportunity_workflow_action(opportunity_name, action):
    try:
        return OpportunityService.execute_workflow_action(opportunity_name, action)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "execute_opportunity_workflow_action")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def send_opportunity_for_approval(opportunity_name, action=None):
    try:
        return OpportunityService.send_for_approval(opportunity_name, action)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "send_opportunity_for_approval")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def return_opportunity_workflow(opportunity_name, action=None):
    try:
        return OpportunityService.return_workflow(opportunity_name, action)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "return_opportunity_workflow")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def get_opportunity_form(opportunity_name=None):
    try:
        return OpportunityService.get_opportunity_form(opportunity_name=opportunity_name)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "get_opportunity_form")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def get_opportunities(limit_start=0, limit_page_length=20, status=None, search=None, follow_up_filter=None, sort_by=None):
    try:
        return OpportunityService.get_opportunities(
            limit_start=limit_start,
            limit_page_length=limit_page_length,
            status=status,
            search=search,
            follow_up_filter=follow_up_filter,
            sort_by=sort_by,
        )
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "get_opportunities")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def get_opportunities_dashboard_summary(status=None, search=None):
    try:
        return OpportunityService.get_opportunities_dashboard_summary(status=status, search=search)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "get_opportunities_dashboard_summary")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def get_opportunity_details(opportunity_name):
    try:
        return OpportunityService.get_opportunity_details(opportunity_name)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "get_opportunity_details")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def get_opportunity_follow_ups(opportunity_name):
    try:
        return OpportunityService.get_opportunity_follow_ups(opportunity_name)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "get_opportunity_follow_ups")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def get_opportunity_required_fields(opportunity_name=None, data=None, **kwargs):
    try:
        return OpportunityService.get_required_fields(opportunity_name=opportunity_name, data=data, **kwargs)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "get_opportunity_required_fields")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def create_opportunity(data=None, **kwargs):
    try:
        return OpportunityService.create_opportunity(data=data, **kwargs)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "create_opportunity")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def update_opportunity(opportunity_name, data=None, **kwargs):
    try:
        return OpportunityService.update_opportunity(opportunity_name=opportunity_name, data=data, **kwargs)
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "update_opportunity")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def add_opportunity_follow_up(opportunity_name, follow_up_date, expected_result_date, details, attachment=None):
    try:
        return OpportunityService.add_follow_up(
            opportunity_name=opportunity_name,
            follow_up_date=follow_up_date,
            expected_result_date=expected_result_date,
            details=details,
            attachment=attachment,
        )
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "add_opportunity_follow_up")
        return {"status": "error", "message": str(exc)}
