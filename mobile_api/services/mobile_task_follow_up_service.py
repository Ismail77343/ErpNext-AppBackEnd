import frappe
from frappe import _
from frappe.utils import add_days, cint, getdate, now, nowdate, nowtime

from mobile_api.repositories.mobile_task_follow_up_repository import MobileTaskFollowUpRepository


class MobileTaskFollowUpService:
	CLOSED_STATUSES = {"Completed", "Cancelled"}
	OPEN_STATUSES = {"Open", "Working", "Blocked", "Overdue"}
	VALID_STATUSES = OPEN_STATUSES | CLOSED_STATUSES
	VALID_PRIORITIES = {"Low", "Medium", "High"}

	@classmethod
	def create_task_follow_up(
		cls,
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
		user = cls.require_authenticated_user()
		settings = MobileTaskFollowUpRepository.get_settings()
		if not cint(settings.get("enabled")):
			return cls.error("Mobile Task Follow Up is disabled.", "FEATURE_DISABLED")

		subject = (subject or "").strip()
		if not subject:
			return cls.error("subject is required.", "SUBJECT_REQUIRED")

		priority = priority or "Medium"
		if priority not in cls.VALID_PRIORITIES:
			return cls.error("Invalid priority.", "INVALID_PRIORITY")

		targets = cls.resolve_targets(assigned_to_employees, assigned_to_users)
		if not targets:
			return cls.error("Send at least one employee or user.", "ASSIGNEE_REQUIRED")

		default_due_days = max(cint(settings.get("default_due_days") or 1), 0)
		start_date = getdate(start_date or nowdate())
		due_date = getdate(due_date or add_days(start_date, default_due_days))

		created = []
		for target in targets:
			doc = MobileTaskFollowUpRepository.insert(
				{
					"subject": subject,
					"details": details or "",
					"priority": priority,
					"status": "Open",
					"progress": 0,
					"assigned_to_employee": target.get("employee"),
					"assigned_to_user": target.get("user"),
					"assigned_by": user,
					"project": project,
					"task": task,
					"start_date": start_date,
					"due_date": due_date,
				}
			)
			created.append(cls.serialize(doc))

		MobileTaskFollowUpRepository.commit()
		return {
			"status": "success",
			"message": "Mobile task follow up created successfully.",
			"data": created,
			"count": len(created),
		}

	@classmethod
	def get_my_tasks(cls, status=None, only_open=0, limit_start=0, limit_page_length=20):
		user = cls.require_authenticated_user()
		filters = {"assigned_to_user": user}
		cls.apply_status_filters(filters, status=status, only_open=only_open)
		rows = MobileTaskFollowUpRepository.get_list(filters, limit_start, limit_page_length)
		return cls.success_list(rows, filters, limit_start, limit_page_length)

	@classmethod
	def get_assigned_tasks(cls, status=None, only_open=0, limit_start=0, limit_page_length=20):
		user = cls.require_authenticated_user()
		filters = {"assigned_by": user}
		cls.apply_status_filters(filters, status=status, only_open=only_open)
		rows = MobileTaskFollowUpRepository.get_list(filters, limit_start, limit_page_length)
		return cls.success_list(rows, filters, limit_start, limit_page_length)

	@classmethod
	def get_details(cls, name):
		cls.require_authenticated_user()
		doc = cls.get_permitted_doc(name)
		return {"status": "success", "data": cls.serialize(doc, include_updates=True)}

	@classmethod
	def add_update(cls, name, note, progress=None, status=None, attachment=None):
		user = cls.require_authenticated_user()
		settings = MobileTaskFollowUpRepository.get_settings()
		if not cint(settings.get("enabled")):
			return cls.error("Mobile Task Follow Up is disabled.", "FEATURE_DISABLED")

		doc = cls.get_permitted_doc(name)
		note = (note or "").strip()
		if not note:
			return cls.error("note is required.", "NOTE_REQUIRED")

		new_status = status or doc.status
		if new_status not in cls.VALID_STATUSES:
			return cls.error("Invalid status.", "INVALID_STATUS")
		if new_status in cls.CLOSED_STATUSES and not cls.can_close(doc, user):
			return cls.error("Only the task creator can close or cancel this follow up.", "CLOSE_NOT_ALLOWED")

		if progress is not None:
			doc.progress = max(0, min(100, cint(progress)))
		doc.status = new_status
		if doc.status in cls.CLOSED_STATUSES:
			doc.closed_by = user
			doc.closed_on = now()

		doc.append(
			"updates",
			{
				"update_date": nowdate(),
				"update_time": nowtime(),
				"note": note,
				"progress": doc.progress,
				"status": doc.status,
				"attachment": attachment or "",
				"updated_by": user,
			},
		)
		MobileTaskFollowUpRepository.save(doc)
		MobileTaskFollowUpRepository.commit()
		return {"status": "success", "message": "Update added successfully.", "data": cls.serialize(doc, True)}

	@classmethod
	def close_task(cls, name, status="Completed", note=None, progress=None, attachment=None):
		user = cls.require_authenticated_user()
		doc = cls.get_permitted_doc(name)
		status = status or "Completed"
		if status not in cls.CLOSED_STATUSES:
			return cls.error("close status must be Completed or Cancelled.", "INVALID_CLOSE_STATUS")
		if not cls.can_close(doc, user):
			return cls.error("Only the task creator can close or cancel this follow up.", "CLOSE_NOT_ALLOWED")
		if progress is None and status == "Completed":
			progress = 100
		return cls.add_update(
			name=name,
			note=note or _("Task closed by {0}.").format(user),
			progress=progress,
			status=status,
			attachment=attachment,
		)

	@classmethod
	def get_notifications(cls, limit_start=0, limit_page_length=20):
		user = cls.require_authenticated_user()
		settings = MobileTaskFollowUpRepository.get_settings()
		if not cint(settings.get("enabled")) or not cint(settings.get("notify_assignee_in_app")):
			return {"status": "success", "data": [], "total_count": 0, "unread_count": 0}

		filters = {
			"assigned_to_user": user,
			"read_by_assignee": 0,
			"status": ["not in", list(cls.CLOSED_STATUSES)],
		}
		rows = MobileTaskFollowUpRepository.get_list(filters, limit_start, limit_page_length)
		return {
			"status": "success",
			"data": [cls.notification_item(row) for row in rows],
			"total_count": MobileTaskFollowUpRepository.count(filters),
			"unread_count": MobileTaskFollowUpRepository.count(filters),
			"limit_start": cint(limit_start or 0),
			"limit_page_length": cint(limit_page_length or 20),
		}

	@classmethod
	def mark_read(cls, name):
		user = cls.require_authenticated_user()
		doc = cls.get_permitted_doc(name)
		if doc.assigned_to_user != user:
			return cls.error("Only the assignee can mark this follow up as read.", "READ_NOT_ALLOWED")
		doc.read_by_assignee = 1
		doc.read_on = now()
		MobileTaskFollowUpRepository.save(doc)
		MobileTaskFollowUpRepository.commit()
		return {"status": "success", "message": "Marked as read.", "data": cls.serialize(doc)}

	@classmethod
	def create_from_timesheet_distribution(cls, batch_doc):
		settings = MobileTaskFollowUpRepository.get_settings()
		if not cint(settings.get("enabled")) or not cint(settings.get("auto_create_from_timesheet_distribution")):
			return {"status": "skipped", "reason": "disabled"}

		created = []
		for row in batch_doc.get("entries") or []:
			if not row.get("employee"):
				continue
			if MobileTaskFollowUpRepository.has_source_task(batch_doc.doctype, batch_doc.name, row.name):
				continue

			employee = MobileTaskFollowUpRepository.get_employee(row.employee)
			if not employee or employee.status != "Active" or not employee.user_id:
				continue

			timesheet = row.get("timesheet") or frappe.db.get_value(row.doctype, row.name, "timesheet")
			subject = cls.get_timesheet_subject(batch_doc, row)
			due_date = add_days(getattr(batch_doc, "work_date", None) or nowdate(), max(cint(settings.default_due_days or 1), 0))

			doc = MobileTaskFollowUpRepository.insert(
				{
					"subject": subject,
					"details": row.get("description") or "",
					"priority": "Medium",
					"status": "Open",
					"progress": 0,
					"assigned_to_employee": employee.name,
					"assigned_to_user": employee.user_id,
					"assigned_by": frappe.session.user,
					"project": row.get("project"),
					"task": row.get("task"),
					"start_date": getattr(batch_doc, "work_date", None) or nowdate(),
					"due_date": due_date,
					"source_doctype": batch_doc.doctype,
					"source_name": batch_doc.name,
					"source_row": row.name,
					"source_timesheet": timesheet,
				}
			)
			created.append(doc.name)

		if created:
			MobileTaskFollowUpRepository.commit()
		return {"status": "success", "created": created, "count": len(created)}

	@classmethod
	def get_timesheet_subject(cls, batch_doc, row):
		task_subject = MobileTaskFollowUpRepository.get_task_subject(row.get("task"))
		work_date = getattr(batch_doc, "work_date", None) or nowdate()
		if task_subject:
			return _("Follow up: {0} - {1}").format(task_subject, work_date)
		return _("Timesheet follow up - {0}").format(work_date)

	@classmethod
	def resolve_targets(cls, assigned_to_employees=None, assigned_to_users=None):
		targets = []
		seen = set()

		for employee_name in cls.parse_list(assigned_to_employees):
			employee = MobileTaskFollowUpRepository.get_employee(employee_name)
			if not employee:
				frappe.throw(_("Employee {0} was not found.").format(frappe.bold(employee_name)))
			if employee.status != "Active":
				frappe.throw(_("Employee {0} is not active.").format(frappe.bold(employee_name)))
			if not employee.user_id:
				frappe.throw(_("Employee {0} has no linked User.").format(frappe.bold(employee_name)))
			key = employee.user_id
			if key not in seen:
				targets.append({"employee": employee.name, "user": employee.user_id})
				seen.add(key)

		for user_name in cls.parse_list(assigned_to_users):
			user = MobileTaskFollowUpRepository.get_user(user_name)
			if not user:
				frappe.throw(_("User {0} was not found.").format(frappe.bold(user_name)))
			if not cint(user.enabled):
				frappe.throw(_("User {0} is disabled.").format(frappe.bold(user_name)))
			employee = MobileTaskFollowUpRepository.find_employee_by_user(user.name)
			key = user.name
			if key not in seen:
				targets.append({"employee": employee.name if employee else None, "user": user.name})
				seen.add(key)

		return targets

	@staticmethod
	def parse_list(value):
		if not value:
			return []
		if isinstance(value, (list, tuple, set)):
			return [item for item in value if item]
		if isinstance(value, str):
			value = value.strip()
			if not value:
				return []
			if value.startswith("["):
				parsed = frappe.parse_json(value)
				return parsed if isinstance(parsed, list) else []
			return [item.strip() for item in value.split(",") if item.strip()]
		return [value]

	@classmethod
	def get_permitted_doc(cls, name):
		if not name or not MobileTaskFollowUpRepository.exists(name):
			frappe.throw(_("Mobile Task Follow Up {0} was not found.").format(name), frappe.DoesNotExistError)
		doc = MobileTaskFollowUpRepository.get_doc(name)
		user = frappe.session.user
		if not cls.can_access(doc, user):
			frappe.throw(_("Not permitted to access this Mobile Task Follow Up."), frappe.PermissionError)
		return doc

	@classmethod
	def can_access(cls, doc, user):
		if "System Manager" in frappe.get_roles(user):
			return True
		return doc.assigned_to_user == user or doc.assigned_by == user

	@classmethod
	def can_close(cls, doc, user):
		if "System Manager" in frappe.get_roles(user):
			return True
		return doc.assigned_by == user

	@classmethod
	def apply_status_filters(cls, filters, status=None, only_open=0):
		if status:
			if status not in cls.VALID_STATUSES:
				frappe.throw(_("Invalid status: {0}").format(status))
			filters["status"] = status
		elif cint(only_open):
			filters["status"] = ["not in", list(cls.CLOSED_STATUSES)]

	@classmethod
	def success_list(cls, rows, filters, limit_start, limit_page_length):
		return {
			"status": "success",
			"data": rows,
			"total_count": MobileTaskFollowUpRepository.count(filters),
			"limit_start": cint(limit_start or 0),
			"limit_page_length": cint(limit_page_length or 20),
		}

	@classmethod
	def serialize(cls, doc, include_updates=False):
		data = doc.as_dict()
		data["can_close"] = cls.can_close(doc, frappe.session.user)
		data["can_update"] = cls.can_access(doc, frappe.session.user)
		if include_updates:
			data["updates"] = [row.as_dict() for row in doc.get("updates") or []]
		else:
			data.pop("updates", None)
		return data

	@classmethod
	def notification_item(cls, row):
		return {
			"id": row.get("name"),
			"notification_type": "mobile_task_follow_up",
			"doctype": "Mobile Task Follow Up",
			"document_name": row.get("name"),
			"subject": row.get("subject"),
			"priority": row.get("priority"),
			"status": row.get("status"),
			"progress": row.get("progress"),
			"assigned_by": row.get("assigned_by"),
			"due_date": row.get("due_date"),
			"modified": row.get("modified"),
			"read": bool(row.get("read_by_assignee")),
			"detail_endpoint": {
				"method": "mobile_api.api.get_mobile_task_follow_up_details",
				"param_key": "name",
				"param_value": row.get("name"),
			},
		}

	@staticmethod
	def require_authenticated_user():
		user = frappe.session.user
		if not user or user == "Guest":
			frappe.throw(_("User is not authenticated."), frappe.PermissionError)
		return user

	@staticmethod
	def error(message, code):
		return {"status": "error", "message": message, "code": code}
