import frappe
from frappe import _


def validate_project_attendance_location(doc, method=None):
	settings = get_attendance_settings()
	if not settings:
		return
	if not settings.get("enabled") or not settings.get("require_project_attendance_location"):
		return
	if doc.is_new() or doc.get("status") != "Open" or doc.get("is_active") != "Yes":
		return

	location_name = doc.get("mobile_api_attendance_location")
	if not location_name:
		frappe.throw(
			_("Mobile Attendance Location is required before keeping this Project open and active.")
		)

	location = frappe.db.get_value(
		"Mobile HR Attendance Location",
		location_name,
		["name", "enabled", "latitude", "longitude", "radius_meters", "project"],
		as_dict=True,
	)
	if not location:
		frappe.throw(_("Selected Mobile Attendance Location does not exist."))
	if not location.enabled:
		frappe.throw(_("Selected Mobile Attendance Location must be enabled."))
	if location.latitude is None or location.longitude is None:
		frappe.throw(_("Selected Mobile Attendance Location must have latitude and longitude."))
	if not location.radius_meters or float(location.radius_meters) <= 0:
		frappe.throw(_("Selected Mobile Attendance Location must have a valid radius."))
	if location.project != doc.name:
		frappe.throw(
			_("Selected Mobile Attendance Location must be linked to this Project.")
		)


def get_attendance_settings():
	if not frappe.db.exists("DocType", "Mobile HR Attendance Settings"):
		return None
	return frappe.get_single("Mobile HR Attendance Settings")
