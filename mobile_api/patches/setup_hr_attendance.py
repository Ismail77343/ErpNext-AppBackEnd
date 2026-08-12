import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	if not frappe.db.exists("DocType", "Employee Checkin"):
		return

	create_custom_fields(
		{
			"Employee Checkin": [
				{
					"fieldname": "mobile_api_attendance_section",
					"label": "Mobile Attendance",
					"fieldtype": "Section Break",
					"insert_after": "log_type",
				},
				{
					"fieldname": "mobile_api_attendance_location",
					"label": "Mobile Attendance Location",
					"fieldtype": "Link",
					"options": "Mobile HR Attendance Location",
					"insert_after": "mobile_api_attendance_section",
					"read_only": 1,
				},
				{
					"fieldname": "mobile_api_checkin_source",
					"label": "Checkin Source",
					"fieldtype": "Data",
					"insert_after": "mobile_api_attendance_location",
					"read_only": 1,
				},
				{
					"fieldname": "mobile_api_project",
					"label": "Mobile Project",
					"fieldtype": "Link",
					"options": "Project",
					"insert_after": "mobile_api_checkin_source",
					"read_only": 1,
				},
				{
					"fieldname": "mobile_api_location_column",
					"fieldtype": "Column Break",
					"insert_after": "mobile_api_project",
				},
				{
					"fieldname": "mobile_api_geofence_status",
					"label": "Geofence Status",
					"fieldtype": "Select",
					"options": "Valid\nOutside\nNot Required",
					"insert_after": "mobile_api_location_column",
					"read_only": 1,
				},
				{
					"fieldname": "mobile_api_distance_meters",
					"label": "Distance (Meters)",
					"fieldtype": "Float",
					"insert_after": "mobile_api_geofence_status",
					"read_only": 1,
				},
				{
					"fieldname": "mobile_api_latitude",
					"label": "Latitude",
					"fieldtype": "Float",
					"precision": "8",
					"insert_after": "mobile_api_distance_meters",
					"read_only": 1,
				},
				{
					"fieldname": "mobile_api_longitude",
					"label": "Longitude",
					"fieldtype": "Float",
					"precision": "8",
					"insert_after": "mobile_api_latitude",
					"read_only": 1,
				},
				{
					"fieldname": "mobile_api_location_accuracy",
					"label": "GPS Accuracy",
					"fieldtype": "Float",
					"insert_after": "mobile_api_longitude",
					"read_only": 1,
				},
				{
					"fieldname": "mobile_api_device_id",
					"label": "Device ID",
					"fieldtype": "Data",
					"insert_after": "mobile_api_location_accuracy",
					"read_only": 1,
				},
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
				{
					"fieldname": "mobile_api_notes",
					"label": "Mobile Notes",
					"fieldtype": "Small Text",
					"insert_after": "mobile_api_photo_file",
					"read_only": 1,
				},
			]
		},
		ignore_validate=True,
	)
