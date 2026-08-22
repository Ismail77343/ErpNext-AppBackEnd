import frappe

from mobile_api.services.mobile_task_follow_up_service import MobileTaskFollowUpService


def _handle_error(title, exc):
	frappe.log_error(frappe.get_traceback(), title)
	code = "PERMISSION_DENIED" if isinstance(exc, frappe.PermissionError) else "SERVER_ERROR"
	return {"status": "error", "message": str(exc), "code": code}


@frappe.whitelist()
def create_mobile_task_follow_up(
	assigned_to_employees=None,
	assigned_to_users=None,
	subject=None,
	details=None,
	priority=None,
	project=None,
	task=None,
	start_date=None,
	due_date=None,
):
	try:
		return MobileTaskFollowUpService.create_task_follow_up(
			assigned_to_employees=assigned_to_employees,
			assigned_to_users=assigned_to_users,
			subject=subject,
			details=details,
			priority=priority,
			project=project,
			task=task,
			start_date=start_date,
			due_date=due_date,
		)
	except Exception as exc:
		return _handle_error("create_mobile_task_follow_up", exc)


@frappe.whitelist()
def get_my_mobile_task_follow_ups(status=None, only_open=0, limit_start=0, limit_page_length=20):
	try:
		return MobileTaskFollowUpService.get_my_tasks(
			status=status,
			only_open=only_open,
			limit_start=limit_start,
			limit_page_length=limit_page_length,
		)
	except Exception as exc:
		return _handle_error("get_my_mobile_task_follow_ups", exc)


@frappe.whitelist()
def get_assigned_mobile_task_follow_ups(status=None, only_open=0, limit_start=0, limit_page_length=20):
	try:
		return MobileTaskFollowUpService.get_assigned_tasks(
			status=status,
			only_open=only_open,
			limit_start=limit_start,
			limit_page_length=limit_page_length,
		)
	except Exception as exc:
		return _handle_error("get_assigned_mobile_task_follow_ups", exc)


@frappe.whitelist()
def get_mobile_task_follow_up_details(name):
	try:
		return MobileTaskFollowUpService.get_details(name)
	except Exception as exc:
		return _handle_error("get_mobile_task_follow_up_details", exc)


@frappe.whitelist()
def add_mobile_task_follow_up_update(name, note, progress=None, status=None, attachment=None):
	try:
		return MobileTaskFollowUpService.add_update(
			name=name,
			note=note,
			progress=progress,
			status=status,
			attachment=attachment,
		)
	except Exception as exc:
		return _handle_error("add_mobile_task_follow_up_update", exc)


@frappe.whitelist()
def close_mobile_task_follow_up(name, status="Completed", note=None, progress=None, attachment=None):
	try:
		return MobileTaskFollowUpService.close_task(
			name=name,
			status=status,
			note=note,
			progress=progress,
			attachment=attachment,
		)
	except Exception as exc:
		return _handle_error("close_mobile_task_follow_up", exc)


@frappe.whitelist()
def get_mobile_task_follow_up_notifications(limit_start=0, limit_page_length=20):
	try:
		return MobileTaskFollowUpService.get_notifications(
			limit_start=limit_start,
			limit_page_length=limit_page_length,
		)
	except Exception as exc:
		return _handle_error("get_mobile_task_follow_up_notifications", exc)


@frappe.whitelist()
def mark_mobile_task_follow_up_read(name):
	try:
		return MobileTaskFollowUpService.mark_read(name)
	except Exception as exc:
		return _handle_error("mark_mobile_task_follow_up_read", exc)
