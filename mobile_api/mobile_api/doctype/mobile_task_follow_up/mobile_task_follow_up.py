import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, cint, getdate, now, today


CLOSED_STATUSES = {"Completed", "Cancelled"}
OPEN_STATUSES = {"Open", "Working", "Blocked", "Overdue"}
VALID_STATUSES = OPEN_STATUSES | CLOSED_STATUSES


class MobileTaskFollowUp(Document):
	def before_insert(self):
		if not self.assigned_by:
			self.assigned_by = frappe.session.user
		if not self.start_date:
			self.start_date = today()
		if not self.due_date:
			default_days = cint(
				frappe.db.get_single_value("Mobile Task Follow Up Settings", "default_due_days") or 1
			)
			self.due_date = add_days(self.start_date, max(default_days, 0))
		if not self.status:
			self.status = "Open"
		if not self.priority:
			self.priority = "Medium"

	def validate(self):
		self.validate_status()
		self.validate_progress()
		self.resolve_assignee()
		self.validate_reference_task()
		self.validate_close_permission()
		self.set_close_metadata()

	def validate_status(self):
		if self.status not in VALID_STATUSES:
			frappe.throw(_("Invalid Mobile Task Follow Up status: {0}").format(self.status))

	def validate_progress(self):
		self.progress = max(0, min(100, cint(self.progress or 0)))

	def resolve_assignee(self):
		if self.assigned_to_employee and not self.assigned_to_user:
			self.assigned_to_user = frappe.db.get_value("Employee", self.assigned_to_employee, "user_id")
		if not self.assigned_to_user:
			frappe.throw(_("Assigned To User is required."))
		if not frappe.db.exists("User", self.assigned_to_user):
			frappe.throw(_("Assigned user {0} was not found.").format(frappe.bold(self.assigned_to_user)))

		if self.assigned_to_employee:
			employee_user = frappe.db.get_value("Employee", self.assigned_to_employee, "user_id")
			if employee_user and employee_user != self.assigned_to_user:
				frappe.throw(_("Assigned employee is linked to another user."))

	def validate_reference_task(self):
		if not self.task:
			return
		task_project = frappe.db.get_value("Task", self.task, "project")
		if self.project and task_project and self.project != task_project:
			frappe.throw(_("Task {0} belongs to project {1}.").format(frappe.bold(self.task), frappe.bold(task_project)))
		if not self.project and task_project:
			self.project = task_project

	def validate_close_permission(self):
		if getattr(frappe.flags, "mobile_task_follow_up_syncing", False):
			return
		if getattr(frappe.flags, "mobile_material_handover_task_update", False):
			return
		if self.is_new() or self.status not in CLOSED_STATUSES:
			return

		old_status = frappe.db.get_value(self.doctype, self.name, "status")
		if old_status == self.status:
			return

		if not can_close_mobile_task_follow_up(self):
			frappe.throw(_("Only the task creator can close or cancel this follow up."), frappe.PermissionError)

	def set_close_metadata(self):
		if self.status in CLOSED_STATUSES:
			if not self.closed_by:
				self.closed_by = frappe.session.user
			if not self.closed_on:
				self.closed_on = now()
			return

		self.closed_by = None
		self.closed_on = None


def can_close_mobile_task_follow_up(doc, user=None):
	user = user or frappe.session.user
	if "System Manager" in frappe.get_roles(user):
		return True
	return doc.assigned_by == user
