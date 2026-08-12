import base64
import math
import mimetypes

import frappe
from frappe.utils import now_datetime, today
from frappe.utils.file_manager import save_file


class HRAttendanceService:
	@staticmethod
	def get_settings():
		if not frappe.db.exists("DocType", "Mobile HR Attendance Settings"):
			return frappe._dict()
		return frappe.get_single("Mobile HR Attendance Settings")

	@staticmethod
	def get_current_employee():
		employee_fields = ["name", "employee_name", "company", "department", "user_id"]
		meta = frappe.get_meta("Employee")
		if meta.has_field("branch"):
			employee_fields.append("branch")

		employee = frappe.db.get_value(
			"Employee",
			{"user_id": frappe.session.user, "status": "Active"},
			employee_fields,
			as_dict=True,
		)
		if not employee:
			frappe.throw("No active Employee is linked with the current user.")
		if not employee.get("branch"):
			employee["branch"] = None
		return employee

	@classmethod
	def get_attendance_context(cls, project=None, device_id=None, platform=None):
		settings = cls.get_settings()
		employee = cls.get_current_employee()
		locations = cls.get_allowed_locations(employee, settings, project=project)
		device_verification = cls.get_device_verification_status(
			settings,
			employee,
			device_id=device_id,
			platform=platform,
		)
		last_checkin = frappe.db.get_value(
			"Employee Checkin",
			{"employee": employee.name},
			["name", "time", "log_type"],
			order_by="time desc",
			as_dict=True,
		)

		return {
			"status": "success",
			"enabled": bool(settings.get("enabled")),
			"employee": employee,
			"settings": {
				"require_geo_location": bool(settings.get("require_geo_location")),
				"enforce_geofence": bool(settings.get("enforce_geofence")),
				"allow_checkout_outside_geofence": bool(settings.get("allow_checkout_outside_geofence")),
				"allow_checkin_without_assignment": bool(settings.get("allow_checkin_without_assignment")),
				"default_radius_meters": settings.get("default_radius_meters") or 150,
				"default_log_type": settings.get("default_log_type") or "IN",
				"skip_auto_attendance": bool(settings.get("skip_auto_attendance")),
				"require_verified_mobile_device": bool(settings.get("require_verified_mobile_device")),
				"allow_multiple_verified_devices": bool(settings.get("allow_multiple_verified_devices")),
				"device_verification_approver_role": settings.get("device_verification_approver_role") or "HR Manager",
				"require_checkin_photo": bool(settings.get("require_checkin_photo")),
				"photo_required_for": settings.get("photo_required_for") or "IN and OUT",
				"max_photo_size_kb": settings.get("max_photo_size_kb") or 2048,
			},
			"allowed_locations": locations,
			"last_checkin": last_checkin,
			"device_verification": device_verification,
			"device_verification_required": device_verification.get("required"),
			"device_verified": device_verification.get("verified"),
			"device_verification_status": device_verification.get("status"),
			"can_checkin": device_verification.get("can_checkin"),
			"blocking_reason": device_verification.get("blocking_reason"),
		}

	@classmethod
	def get_mobile_device_verification_status(cls, device_id=None, platform=None):
		settings = cls.get_settings()
		employee = cls.get_current_employee()
		verification = cls.get_device_verification_status(
			settings,
			employee,
			device_id=device_id,
			platform=platform,
		)
		return {
			"status": "success",
			"required": verification.get("required"),
			"verified": verification.get("verified"),
			"verification_status": verification.get("status"),
			"request_name": verification.get("request_name"),
			"can_request": verification.get("can_request"),
			"can_checkin": verification.get("can_checkin"),
			"blocking_reason": verification.get("blocking_reason"),
			"device_verification": verification,
		}

	@classmethod
	def request_mobile_device_verification(
		cls,
		device_id=None,
		device_name=None,
		platform=None,
		app_version=None,
		phone_number=None,
	):
		settings = cls.get_settings()
		if not settings.get("enabled"):
			cls._raise_mobile_error("Mobile HR Attendance is disabled.", "ATTENDANCE_DISABLED")

		employee = cls.get_current_employee()
		device_id = (device_id or "").strip()
		if not device_id:
			cls._raise_mobile_error("Device ID is required to request mobile verification.", "DEVICE_ID_REQUIRED")

		platform = cls._normalize_platform(platform)
		existing = cls._get_latest_device_verification(employee.name, device_id)
		if existing and existing.status in ("Pending Approval", "Approved"):
			return {
				"status": "success",
				"request_name": existing.name,
				"verification_status": existing.status,
				"verified": existing.status == "Approved",
				"can_checkin": existing.status == "Approved",
				"message": "Mobile device verification request already exists.",
			}

		doc = frappe.get_doc(
			{
				"doctype": "Mobile HR Device Verification",
				"status": "Pending Approval",
				"employee": employee.name,
				"user": employee.user_id or frappe.session.user,
				"device_id": device_id,
				"device_name": device_name,
				"platform": platform,
				"app_version": app_version,
				"phone_number": phone_number,
				"requested_on": now_datetime(),
			}
		)
		doc.insert(ignore_permissions=True)
		frappe.db.commit()

		return {
			"status": "success",
			"request_name": doc.name,
			"verification_status": doc.status,
			"verified": False,
			"can_checkin": False,
			"message": "Mobile device verification request created and is pending HR approval.",
		}

	@classmethod
	def get_device_verification_status(cls, settings, employee, device_id=None, platform=None):
		required = bool(settings.get("require_verified_mobile_device"))
		if not required:
			return {
				"required": False,
				"verified": True,
				"status": "Not Required",
				"request_name": None,
				"can_request": False,
				"can_checkin": True,
				"blocking_reason": None,
			}

		device_id = (device_id or "").strip()
		if not device_id:
			return {
				"required": True,
				"verified": False,
				"status": "Device ID Required",
				"request_name": None,
				"can_request": False,
				"can_checkin": False,
				"blocking_reason": "DEVICE_ID_REQUIRED",
			}

		existing = cls._get_latest_device_verification(employee.name, device_id)
		if not existing:
			return {
				"required": True,
				"verified": False,
				"status": "Not Requested",
				"request_name": None,
				"can_request": True,
				"can_checkin": False,
				"blocking_reason": "DEVICE_NOT_VERIFIED",
			}

		if existing.status == "Approved":
			return {
				"required": True,
				"verified": True,
				"status": existing.status,
				"request_name": existing.name,
				"can_request": False,
				"can_checkin": True,
				"blocking_reason": None,
			}

		blocking_reason_by_status = {
			"Pending Approval": "PENDING_APPROVAL",
			"Rejected": "DEVICE_REJECTED",
			"Revoked": "DEVICE_REVOKED",
		}
		can_request = existing.status in ("Rejected", "Revoked")
		return {
			"required": True,
			"verified": False,
			"status": existing.status,
			"request_name": existing.name,
			"can_request": can_request,
			"can_checkin": False,
			"blocking_reason": blocking_reason_by_status.get(existing.status) or "DEVICE_NOT_VERIFIED",
		}

	@staticmethod
	def _get_latest_device_verification(employee, device_id):
		rows = frappe.get_all(
			"Mobile HR Device Verification",
			filters={"employee": employee, "device_id": device_id},
			fields=["name", "status", "device_name", "platform", "requested_on", "reviewed_on"],
			order_by="modified desc",
			limit_page_length=1,
		)
		return rows[0] if rows else None

	@staticmethod
	def _normalize_platform(platform):
		value = (platform or "Other").strip().lower()
		if value == "android":
			return "Android"
		if value == "ios":
			return "iOS"
		if value == "web":
			return "Web"
		return "Other"

	@classmethod
	def get_allowed_locations(cls, employee, settings=None, project=None):
		settings = settings or cls.get_settings()
		if not settings.get("enabled"):
			return []

		location_names = set()
		assignment_filters = {
			"enabled": 1,
			"attendance_location": ["is", "set"],
		}
		assignments = frappe.get_all(
			"Mobile HR Attendance Assignment",
			filters=assignment_filters,
			fields=[
				"name",
				"attendance_location",
				"assignment_basis",
				"employee",
				"department",
				"project",
				"branch",
				"company",
				"valid_from",
				"valid_to",
			],
		)
		for assignment in assignments:
			if not cls._assignment_is_current(assignment):
				continue
			if cls._assignment_matches_employee(assignment, employee, project=project):
				location_names.add(assignment.attendance_location)

		if settings.get("return_all_active_locations") or settings.get("allow_checkin_without_assignment"):
			for row in frappe.get_all("Mobile HR Attendance Location", filters={"enabled": 1}, pluck="name"):
				location_names.add(row)

		if not location_names:
			return []

		locations = frappe.get_all(
			"Mobile HR Attendance Location",
			filters={"name": ["in", list(location_names)], "enabled": 1},
			fields=[
				"name",
				"location_name",
				"location_type",
				"company",
				"branch",
				"department",
				"project",
				"cost_center",
				"latitude",
				"longitude",
				"radius_meters",
				"address",
			],
			order_by="location_name asc",
		)
		return [dict(row) for row in locations]

	@staticmethod
	def _assignment_is_current(assignment):
		current_date = today()
		if assignment.valid_from and str(assignment.valid_from) > current_date:
			return False
		if assignment.valid_to and str(assignment.valid_to) < current_date:
			return False
		return True

	@staticmethod
	def _assignment_matches_employee(assignment, employee, project=None):
		basis = assignment.assignment_basis
		if basis == "Employee":
			return assignment.employee == employee.name
		if basis == "Department":
			return bool(employee.department and assignment.department == employee.department)
		if basis == "Branch":
			return bool(employee.get("branch") and assignment.branch == employee.get("branch"))
		if basis == "Company":
			return bool(employee.company and assignment.company == employee.company)
		if basis == "Project":
			if project and assignment.project == project:
				return True
			return HRAttendanceService._user_is_on_project(assignment.project)
		return False

	@staticmethod
	def _user_is_on_project(project):
		if not project:
			return False
		if frappe.db.exists("DocType", "Project User"):
			if frappe.db.exists("Project User", {"parent": project, "user": frappe.session.user}):
				return True
		project_meta = frappe.get_meta("Project")
		if project_meta.has_field("project_manager"):
			manager = frappe.db.get_value("Project", project, "project_manager")
			if manager and manager == frappe.session.user:
				return True
		return False

	@classmethod
	def create_employee_checkin(
		cls,
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
		settings = cls.get_settings()
		if not settings.get("enabled"):
			frappe.throw("Mobile HR Attendance is disabled.")

		employee = cls.get_current_employee()
		log_type = (log_type or settings.get("default_log_type") or "IN").upper()
		if log_type not in ("IN", "OUT"):
			frappe.throw("Log Type must be IN or OUT.")

		device_verification = cls.get_device_verification_status(settings, employee, device_id=device_id)
		if not device_verification.get("can_checkin"):
			cls._raise_mobile_error(
				cls._get_device_verification_error_message(device_verification),
				device_verification.get("blocking_reason") or "DEVICE_NOT_VERIFIED",
			)

		if settings.get("require_geo_location") and (latitude is None or longitude is None):
			frappe.throw("GPS latitude and longitude are required for mobile attendance.")

		photo_payload = cls._prepare_checkin_photo(
			settings=settings,
			log_type=log_type,
			photo_base64=photo_base64,
			photo_filename=photo_filename,
			photo_mime_type=photo_mime_type,
		)

		latitude = cls._to_float(latitude, "Latitude") if latitude is not None else None
		longitude = cls._to_float(longitude, "Longitude") if longitude is not None else None
		allowed_locations = cls.get_allowed_locations(employee, settings, project=project)
		selected_location = cls._select_location(attendance_location, allowed_locations, latitude, longitude)

		if not selected_location and not settings.get("allow_checkin_without_assignment"):
			frappe.throw("No attendance location is assigned to this employee.")

		distance = None
		geofence_status = "Not Required"
		skip_auto_attendance = 1 if settings.get("skip_auto_attendance") else 0
		if selected_location and latitude is not None and longitude is not None:
			distance = cls._distance_meters(
				latitude,
				longitude,
				float(selected_location.get("latitude")),
				float(selected_location.get("longitude")),
			)
			allowed_radius = selected_location.get("radius_meters") or settings.get("default_radius_meters") or 150
			geofence_status = "Valid" if distance <= float(allowed_radius) else "Outside"
			is_checkout_outside_allowed = (
				log_type == "OUT"
				and geofence_status == "Outside"
				and settings.get("allow_checkout_outside_geofence")
			)
			if is_checkout_outside_allowed:
				skip_auto_attendance = 1
			if settings.get("enforce_geofence") and geofence_status == "Outside" and not is_checkout_outside_allowed:
				frappe.throw(
					f"You are outside the allowed attendance location. Distance: {round(distance, 2)} m, Allowed: {allowed_radius} m."
				)

		doc = frappe.get_doc(
			{
				"doctype": "Employee Checkin",
				"employee": employee.name,
				"time": now_datetime(),
				"log_type": log_type,
				"skip_auto_attendance": skip_auto_attendance,
			}
		)
		cls._set_if_field_exists(doc, "mobile_api_attendance_location", selected_location.get("name") if selected_location else None)
		cls._set_if_field_exists(doc, "mobile_api_latitude", latitude)
		cls._set_if_field_exists(doc, "mobile_api_longitude", longitude)
		cls._set_if_field_exists(doc, "mobile_api_distance_meters", distance)
		cls._set_if_field_exists(doc, "mobile_api_geofence_status", geofence_status)
		cls._set_if_field_exists(doc, "mobile_api_device_id", device_id)
		cls._set_if_field_exists(doc, "mobile_api_location_accuracy", cls._to_float(accuracy, "Accuracy") if accuracy else None)
		cls._set_if_field_exists(doc, "mobile_api_notes", notes)
		cls._set_if_field_exists(doc, "mobile_api_project", project or (selected_location.get("project") if selected_location else None))
		cls._set_if_field_exists(doc, "mobile_api_checkin_source", "Mobile API")

		doc.insert(ignore_permissions=True)
		photo_url = cls._attach_checkin_photo(doc, photo_payload)
		frappe.db.commit()

		return {
			"status": "success",
			"message": "Employee checkin created successfully.",
			"checkin": doc.name,
			"employee": employee.name,
			"log_type": log_type,
			"attendance_location": selected_location.get("name") if selected_location else None,
			"distance_meters": distance,
			"geofence_status": geofence_status,
			"photo_required": photo_payload.get("required"),
			"photo_uploaded": bool(photo_url),
			"photo_url": photo_url,
		}

	@classmethod
	def _prepare_checkin_photo(
		cls,
		settings,
		log_type,
		photo_base64=None,
		photo_filename=None,
		photo_mime_type=None,
	):
		required = cls._is_checkin_photo_required(settings, log_type)
		if not photo_base64:
			if required:
				cls._raise_mobile_error(
					"Attendance photo is required for this check-in.",
					"CHECKIN_PHOTO_REQUIRED",
				)
			return {"required": required, "uploaded": False}

		data = (photo_base64 or "").strip()
		detected_mime_type = None
		if data.startswith("data:"):
			header, _separator, payload = data.partition(",")
			data = payload
			detected_mime_type = header[5:].split(";")[0].strip().lower()

		data = "".join(data.split())
		mime_type = (
			photo_mime_type
			or detected_mime_type
			or mimetypes.guess_type(photo_filename or "")[0]
			or ""
		).lower()
		if mime_type in ("image/jpg", "image/pjpeg"):
			mime_type = "image/jpeg"
		if mime_type not in ("image/jpeg", "image/png"):
			cls._raise_mobile_error(
				"Only JPEG and PNG attendance photos are supported.",
				"UNSUPPORTED_CHECKIN_PHOTO_TYPE",
			)

		try:
			content = base64.b64decode(data, validate=True)
		except Exception:
			cls._raise_mobile_error("Invalid attendance photo data.", "INVALID_CHECKIN_PHOTO")

		if not content:
			cls._raise_mobile_error("Attendance photo data is empty.", "INVALID_CHECKIN_PHOTO")

		max_size_kb = cls._get_max_photo_size_kb(settings)
		if len(content) > max_size_kb * 1024:
			cls._raise_mobile_error(
				f"Attendance photo exceeds maximum size of {max_size_kb} KB.",
				"CHECKIN_PHOTO_TOO_LARGE",
			)

		return {
			"required": required,
			"uploaded": True,
			"content": content,
			"filename": cls._safe_photo_filename(photo_filename, mime_type),
			"mime_type": mime_type,
		}

	@classmethod
	def _attach_checkin_photo(cls, doc, photo_payload):
		if not photo_payload or not photo_payload.get("uploaded"):
			return None

		file_doc = save_file(
			photo_payload.get("filename"),
			photo_payload.get("content"),
			doc.doctype,
			doc.name,
			is_private=1,
		)
		photo_url = file_doc.file_url
		cls._set_if_field_exists(doc, "mobile_api_photo", photo_url)
		cls._set_if_field_exists(doc, "mobile_api_photo_uploaded", 1)
		cls._set_if_field_exists(doc, "mobile_api_photo_file", file_doc.name)
		doc.save(ignore_permissions=True)
		return photo_url

	@staticmethod
	def _is_checkin_photo_required(settings, log_type):
		if not settings.get("require_checkin_photo"):
			return False

		required_for = (settings.get("photo_required_for") or "IN and OUT").strip()
		if required_for == "IN and OUT":
			return True
		if required_for == "IN Only":
			return log_type == "IN"
		if required_for == "OUT Only":
			return log_type == "OUT"
		return False

	@staticmethod
	def _get_max_photo_size_kb(settings):
		try:
			max_size_kb = int(settings.get("max_photo_size_kb") or 2048)
		except (TypeError, ValueError):
			max_size_kb = 2048
		return max(max_size_kb, 1)

	@staticmethod
	def _safe_photo_filename(photo_filename, mime_type):
		extension = ".jpg" if mime_type == "image/jpeg" else ".png"
		filename = (photo_filename or "").strip()
		if not filename:
			filename = f"mobile_checkin_{frappe.generate_hash(length=8)}{extension}"
		filename = filename.split("/")[-1].split("\\")[-1]
		if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
			filename = f"{filename}{extension}"
		return filename

	@staticmethod
	def _select_location(attendance_location, allowed_locations, latitude, longitude):
		if attendance_location:
			for location in allowed_locations:
				if location.get("name") == attendance_location:
					return location
			frappe.throw("Selected attendance location is not allowed for this employee.")

		if latitude is None or longitude is None or not allowed_locations:
			return allowed_locations[0] if allowed_locations else None

		nearest = None
		nearest_distance = None
		for location in allowed_locations:
			distance = HRAttendanceService._distance_meters(
				latitude,
				longitude,
				float(location.get("latitude")),
				float(location.get("longitude")),
			)
			if nearest_distance is None or distance < nearest_distance:
				nearest = location
				nearest_distance = distance
		return nearest

	@staticmethod
	def _set_if_field_exists(doc, fieldname, value):
		if doc.meta.has_field(fieldname):
			doc.set(fieldname, value)

	@staticmethod
	def _get_device_verification_error_message(verification):
		reason = verification.get("blocking_reason")
		if reason == "DEVICE_ID_REQUIRED":
			return "Device ID is required before mobile attendance check-in."
		if reason == "PENDING_APPROVAL":
			return "Mobile device verification is pending HR approval."
		if reason == "DEVICE_REJECTED":
			return "Mobile device verification request was rejected. Please submit a new request if needed."
		if reason == "DEVICE_REVOKED":
			return "Mobile device verification was revoked. Please request approval again."
		return "This mobile device is not verified for attendance check-in."

	@staticmethod
	def _raise_mobile_error(message, code):
		exc = frappe.ValidationError(message)
		exc.error_code = code
		raise exc

	@staticmethod
	def _to_float(value, label):
		try:
			return float(value)
		except (TypeError, ValueError):
			frappe.throw(f"{label} must be a number.")

	@staticmethod
	def _distance_meters(lat1, lon1, lat2, lon2):
		radius = 6371000
		phi1 = math.radians(lat1)
		phi2 = math.radians(lat2)
		delta_phi = math.radians(lat2 - lat1)
		delta_lambda = math.radians(lon2 - lon1)
		a = (
			math.sin(delta_phi / 2) ** 2
			+ math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
		)
		c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
		return radius * c
