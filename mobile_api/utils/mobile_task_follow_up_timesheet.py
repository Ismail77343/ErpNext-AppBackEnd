import frappe

from mobile_api.services.mobile_task_follow_up_service import MobileTaskFollowUpService


def create_from_project_daily_timesheet_batch(doc, method=None):
	if not frappe.db.exists("DocType", "Mobile Task Follow Up"):
		return
	if doc.doctype != "Project Daily Timesheet Batch":
		return

	try:
		MobileTaskFollowUpService.create_from_timesheet_distribution(doc)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Mobile Task Follow Up Timesheet Integration")
