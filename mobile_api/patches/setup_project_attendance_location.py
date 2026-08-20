import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	if not frappe.db.exists("DocType", "Project"):
		return

	create_custom_fields(
		{
			"Project": [
				{
					"fieldname": "mobile_api_attendance_location",
					"label": "Mobile Attendance Location",
					"fieldtype": "Link",
					"options": "Mobile HR Attendance Location",
					"insert_after": "is_active",
					"in_standard_filter": 1,
				},
			],
		},
		ignore_validate=True,
	)
	frappe.clear_cache(doctype="Project")
