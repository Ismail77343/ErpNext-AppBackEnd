import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


STATUS_OPTIONS = "Open\nWorking\nBlocked\nOverdue\nCompleted\nCancelled"


def execute():
	if not frappe.db.exists("DocType", "Task Follow Up"):
		return

	custom_fields = {
		"Task Follow Up": [
			{
				"fieldname": "mobile_task_follow_up",
				"label": "Mobile Task Follow Up",
				"fieldtype": "Link",
				"options": "Mobile Task Follow Up",
				"insert_after": "ref_name",
				"read_only": 1,
			},
		],
	}

	if frappe.db.exists("DocType", "Child Follow"):
		custom_fields["Child Follow"] = [
			{
				"fieldname": "mobile_task_follow_up_update",
				"label": "Mobile Task Follow Up Update",
				"fieldtype": "Data",
				"insert_after": "file",
				"read_only": 1,
				"hidden": 1,
			},
		]

	create_custom_fields(custom_fields, ignore_validate=True)
	ensure_status_options()
	frappe.clear_cache(doctype="Task Follow Up")
	if frappe.db.exists("DocType", "Child Follow"):
		frappe.clear_cache(doctype="Child Follow")


def ensure_status_options():
	field_name = "Task Follow Up-status_task-options"
	if frappe.db.exists("Property Setter", field_name):
		frappe.db.set_value("Property Setter", field_name, "value", STATUS_OPTIONS)
		return

	frappe.get_doc(
		{
			"doctype": "Property Setter",
			"name": field_name,
			"doc_type": "Task Follow Up",
			"doctype_or_field": "DocField",
			"field_name": "status_task",
			"property": "options",
			"property_type": "Text",
			"value": STATUS_OPTIONS,
		}
	).insert(ignore_permissions=True)
