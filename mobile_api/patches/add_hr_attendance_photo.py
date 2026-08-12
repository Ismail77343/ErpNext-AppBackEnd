import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	if not frappe.db.exists("DocType", "Employee Checkin"):
		return

	create_custom_fields(
		{
			"Employee Checkin": [
				{
					"fieldname": "mobile_api_photo",
					"label": "Mobile Attendance Photo",
					"fieldtype": "Attach Image",
					"insert_after": "mobile_api_device_id",
					"read_only": 1,
				},
				{
					"fieldname": "mobile_api_photo_uploaded",
					"label": "Mobile Photo Uploaded",
					"fieldtype": "Check",
					"insert_after": "mobile_api_photo",
					"read_only": 1,
				},
				{
					"fieldname": "mobile_api_photo_file",
					"label": "Mobile Photo File",
					"fieldtype": "Link",
					"options": "File",
					"insert_after": "mobile_api_photo_uploaded",
					"read_only": 1,
				},
			]
		},
		ignore_validate=True,
	)

	if frappe.db.exists("Custom Field", "Employee Checkin-mobile_api_notes"):
		frappe.db.set_value(
			"Custom Field",
			"Employee Checkin-mobile_api_notes",
			"insert_after",
			"mobile_api_photo_file",
		)
