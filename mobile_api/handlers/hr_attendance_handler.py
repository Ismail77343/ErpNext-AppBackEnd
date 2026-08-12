import frappe
from mobile_api.services.hr_attendance_service import HRAttendanceService


@frappe.whitelist()
def get_hr_attendance_context(project=None, device_id=None, platform=None):
	"""Return attendance settings, current employee, and allowed attendance locations."""
	try:
		return HRAttendanceService.get_attendance_context(project=project, device_id=device_id, platform=platform)
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "get_hr_attendance_context")
		return {"status": "error", "message": str(e), "error_code": getattr(e, "error_code", None)}


@frappe.whitelist()
def get_mobile_device_verification_status(device_id=None, platform=None):
	"""Return current employee mobile device verification status."""
	try:
		return HRAttendanceService.get_mobile_device_verification_status(
			device_id=device_id,
			platform=platform,
		)
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "get_mobile_device_verification_status")
		return {"status": "error", "message": str(e), "error_code": getattr(e, "error_code", None)}


@frappe.whitelist()
def request_mobile_device_verification(
	device_id=None,
	device_name=None,
	platform=None,
	app_version=None,
	phone_number=None,
):
	"""Create a pending mobile device verification request for the current employee."""
	try:
		return HRAttendanceService.request_mobile_device_verification(
			device_id=device_id,
			device_name=device_name,
			platform=platform,
			app_version=app_version,
			phone_number=phone_number,
		)
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "request_mobile_device_verification")
		return {"status": "error", "message": str(e), "error_code": getattr(e, "error_code", None)}


@frappe.whitelist()
def mobile_employee_checkin(
	log_type=None,
	latitude=None,
	longitude=None,
	attendance_location=None,
	device_id=None,
	accuracy=None,
	notes=None,
	project=None,
	photo_base64=None,
	photo_filename=None,
	photo_mime_type=None,
):
	"""Create Employee Checkin from the mobile app after assignment/geofence validation."""
	try:
		return HRAttendanceService.create_employee_checkin(
			log_type=log_type,
			latitude=latitude,
			longitude=longitude,
			attendance_location=attendance_location,
			device_id=device_id,
			accuracy=accuracy,
			notes=notes,
			project=project,
			photo_base64=photo_base64,
			photo_filename=photo_filename,
			photo_mime_type=photo_mime_type,
		)
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "mobile_employee_checkin")
		return {"status": "error", "message": str(e), "error_code": getattr(e, "error_code", None)}
