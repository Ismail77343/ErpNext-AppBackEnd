import frappe


class MobileTaskFollowUpRepository:
	DOCTYPE = "Mobile Task Follow Up"
	SETTINGS_DOCTYPE = "Mobile Task Follow Up Settings"
	CLOSED_STATUSES = {"Completed", "Cancelled"}

	@classmethod
	def get_settings(cls):
		if not frappe.db.exists("DocType", cls.SETTINGS_DOCTYPE):
			return frappe._dict(
				enabled=0,
				auto_create_from_timesheet_distribution=0,
				notify_assignee_in_app=0,
				default_due_days=1,
			)
		return frappe.get_cached_doc(cls.SETTINGS_DOCTYPE)

	@classmethod
	def get_doc(cls, name):
		return frappe.get_doc(cls.DOCTYPE, name)

	@classmethod
	def exists(cls, name):
		return bool(frappe.db.exists(cls.DOCTYPE, name))

	@classmethod
	def get_employee_for_user(cls, user):
		return frappe.db.get_value(
			"Employee",
			{"user_id": user, "status": "Active"},
			["name", "employee_name", "user_id"],
			as_dict=True,
		)

	@classmethod
	def get_employee(cls, employee):
		return frappe.db.get_value(
			"Employee",
			employee,
			["name", "employee_name", "user_id", "status"],
			as_dict=True,
		)

	@classmethod
	def get_user(cls, user):
		return frappe.db.get_value("User", user, ["name", "full_name", "enabled"], as_dict=True)

	@classmethod
	def find_employee_by_user(cls, user):
		return frappe.db.get_value(
			"Employee",
			{"user_id": user, "status": "Active"},
			["name", "employee_name", "user_id"],
			as_dict=True,
		)

	@classmethod
	def insert(cls, values):
		doc = frappe.get_doc({"doctype": cls.DOCTYPE, **values})
		doc.insert(ignore_permissions=True)
		return doc

	@classmethod
	def save(cls, doc):
		doc.save(ignore_permissions=True)
		return doc

	@classmethod
	def commit(cls):
		frappe.db.commit()

	@classmethod
	def has_source_task(cls, source_doctype, source_name, source_row):
		if not source_doctype or not source_name or not source_row:
			return None
		return frappe.db.get_value(
			cls.DOCTYPE,
			{
				"source_doctype": source_doctype,
				"source_name": source_name,
				"source_row": source_row,
			},
			"name",
		)

	@classmethod
	def get_list(cls, filters, limit_start=0, limit_page_length=20):
		return frappe.get_all(
			cls.DOCTYPE,
			filters=filters,
			fields=cls.list_fields(),
			order_by="modified desc",
			limit_start=int(limit_start or 0),
			limit_page_length=int(limit_page_length or 20),
		)

	@classmethod
	def count(cls, filters):
		return frappe.db.count(cls.DOCTYPE, filters=filters)

	@classmethod
	def list_fields(cls):
		return [
			"name",
			"subject",
			"priority",
			"status",
			"progress",
			"assigned_to_employee",
			"assigned_to_user",
			"assigned_by",
			"read_by_assignee",
			"read_on",
			"start_date",
			"due_date",
			"closed_by",
			"closed_on",
			"project",
			"task",
			"tpg_task_follow_up",
			"source_doctype",
			"source_name",
			"source_timesheet",
			"creation",
			"modified",
		]

	@classmethod
	def get_task_subject(cls, task):
		if not task:
			return None
		return frappe.db.get_value("Task", task, "subject")
