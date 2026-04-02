import frappe

from mobile_api.services.notification_service import NotificationService


@frappe.whitelist()
def get_workflow_notifications(limit_start=0, limit_page_length=20):
    try:
        return NotificationService.get_workflow_notifications(
            limit_start=limit_start,
            limit_page_length=limit_page_length,
        )
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "get_workflow_notifications")
        return {"status": "error", "message": str(exc)}


@frappe.whitelist()
def get_workflow_notifications_summary():
    try:
        return NotificationService.get_workflow_notifications_summary()
    except Exception as exc:
        frappe.log_error(frappe.get_traceback(), "get_workflow_notifications_summary")
        return {"status": "error", "message": str(exc)}
