import base64
import json
import mimetypes

import frappe
from frappe import _
from frappe.utils import add_days, cint, flt, getdate, now, nowdate, nowtime
from frappe.utils.file_manager import save_file

from mobile_api.repositories.material_transfer_handover_repository import (
	MaterialTransferHandoverRepository,
)
from mobile_api.repositories.mobile_task_follow_up_repository import MobileTaskFollowUpRepository


class MaterialTransferHandoverService:
	VALID_STATUSES = {
		"Pending Pickup",
		"Picked Up",
		"Delivered",
		"Return Draft Created",
		"Closed",
		"Cancelled",
	}
	RETURNABLE_STATUSES = {"Delivered", "Return Draft Created"}

	@classmethod
	def get_my_handovers(cls, status=None, limit_start=0, limit_page_length=20):
		user = cls.require_authenticated_user()
		filters = {"receiver_user": user}
		if status:
			if status not in cls.VALID_STATUSES:
				return cls.error("Invalid status.", "INVALID_STATUS")
			filters["status"] = status
		rows = MaterialTransferHandoverRepository.get_list(filters, limit_start, limit_page_length)
		return {
			"status": "success",
			"data": rows,
			"total_count": MaterialTransferHandoverRepository.count(filters),
			"limit_start": cint(limit_start or 0),
			"limit_page_length": cint(limit_page_length or 20),
		}

	@classmethod
	def get_details(cls, name):
		doc = cls.get_permitted_doc(name)
		data = cls.serialize(doc, include_logs=True)
		data["items"] = cls.get_original_items(doc)
		data["return_options"] = cls.get_return_options_data(doc)
		return {"status": "success", "data": data}

	@classmethod
	def confirm_pickup(
		cls,
		name,
		photo_base64,
		photo_filename=None,
		notes=None,
		latitude=None,
		longitude=None,
		accuracy_meters=None,
	):
		user = cls.require_authenticated_user()
		doc = cls.get_receiver_doc(name, user)
		settings = MaterialTransferHandoverRepository.get_settings()
		if not cint(settings.get("enabled")):
			return cls.error("Material Transfer Handover is disabled.", "FEATURE_DISABLED")
		if doc.status != "Pending Pickup":
			return cls.error("Pickup can only be confirmed while status is Pending Pickup.", "INVALID_STATUS")

		photo = cls.prepare_photo(
			photo_base64,
			photo_filename,
			required=bool(cint(settings.get("require_pickup_photo"))),
			code="PICKUP_PHOTO_REQUIRED",
			max_size_kb=cls.get_max_photo_size_kb(settings),
		)
		location = cls.prepare_location(
			latitude,
			longitude,
			accuracy_meters,
			required=bool(cint(settings.get("require_pickup_location"))),
			code="PICKUP_LOCATION_REQUIRED",
		)
		file_doc = cls.attach_photo(doc.stock_entry, photo) if photo else None
		event_on = now()
		doc.status = "Picked Up"
		doc.pickup_by = user
		doc.pickup_on = event_on
		if file_doc:
			doc.pickup_photo = file_doc.file_url
			doc.pickup_file = file_doc.name
		cls.apply_location(doc, "pickup", location)
		cls.append_log(doc, "Pickup", event_on, user, file_doc, doc.stock_entry, notes, location)
		MaterialTransferHandoverRepository.save(doc)
		cls.sync_stock_entry_fields(doc)
		cls.add_task_update(doc, "Working", 50, notes or _("Materials picked up."), doc.pickup_photo)
		MaterialTransferHandoverRepository.commit()
		return {"status": "success", "message": "Pickup confirmed.", "data": cls.serialize(doc, True)}

	@classmethod
	def confirm_delivery(
		cls,
		name,
		photo_base64,
		photo_filename=None,
		notes=None,
		latitude=None,
		longitude=None,
		accuracy_meters=None,
	):
		user = cls.require_authenticated_user()
		doc = cls.get_receiver_doc(name, user)
		settings = MaterialTransferHandoverRepository.get_settings()
		if not cint(settings.get("enabled")):
			return cls.error("Material Transfer Handover is disabled.", "FEATURE_DISABLED")
		if doc.status != "Picked Up":
			return cls.error("Delivery can only be confirmed after pickup.", "INVALID_STATUS")

		photo = cls.prepare_photo(
			photo_base64,
			photo_filename,
			required=bool(cint(settings.get("require_delivery_photo"))),
			code="DELIVERY_PHOTO_REQUIRED",
			max_size_kb=cls.get_max_photo_size_kb(settings),
		)
		location = cls.prepare_location(
			latitude,
			longitude,
			accuracy_meters,
			required=bool(cint(settings.get("require_delivery_location"))),
			code="DELIVERY_LOCATION_REQUIRED",
		)
		file_doc = cls.attach_photo(doc.stock_entry, photo) if photo else None
		event_on = now()
		doc.status = "Delivered"
		doc.delivery_by = user
		doc.delivery_on = event_on
		if file_doc:
			doc.delivery_photo = file_doc.file_url
			doc.delivery_file = file_doc.name
		cls.apply_location(doc, "delivery", location)
		cls.append_log(doc, "Delivery", event_on, user, file_doc, doc.stock_entry, notes, location)
		MaterialTransferHandoverRepository.save(doc)
		cls.sync_stock_entry_fields(doc)
		cls.add_task_update(doc, "Completed", 100, notes or _("Materials delivered."), doc.delivery_photo)
		MaterialTransferHandoverRepository.commit()
		return {"status": "success", "message": "Delivery confirmed.", "data": cls.serialize(doc, True)}

	@classmethod
	def get_return_options(cls, name):
		user = cls.require_authenticated_user()
		doc = cls.get_receiver_doc(name, user)
		return {"status": "success", "data": cls.get_return_options_data(doc)}

	@classmethod
	def create_return(
		cls,
		name,
		items,
		photo_base64=None,
		photo_filename=None,
		notes=None,
		latitude=None,
		longitude=None,
		accuracy_meters=None,
	):
		user = cls.require_authenticated_user()
		doc = cls.get_receiver_doc(name, user)
		settings = MaterialTransferHandoverRepository.get_settings()
		if not cint(settings.get("enabled")):
			return cls.error("Material Transfer Handover is disabled.", "FEATURE_DISABLED")
		if doc.status not in cls.RETURNABLE_STATUSES:
			return cls.error("Return can only be created after delivery.", "INVALID_STATUS")
		if not cls.is_return_window_open(doc):
			return cls.error("Return window is closed for this material transfer.", "RETURN_WINDOW_CLOSED")

		selected_items = cls.validate_return_items(doc, items)
		if not selected_items:
			return cls.error("Select at least one item to return.", "RETURN_ITEMS_REQUIRED")

		photo = cls.prepare_photo(
			photo_base64,
			photo_filename,
			required=bool(cint(settings.get("require_return_photo"))),
			code="RETURN_PHOTO_REQUIRED",
			max_size_kb=cls.get_max_photo_size_kb(settings),
		)
		location = cls.prepare_location(
			latitude,
			longitude,
			accuracy_meters,
			required=bool(cint(settings.get("require_return_location"))),
			code="RETURN_LOCATION_REQUIRED",
		)
		return_doc = cls.build_return_stock_entry(doc, selected_items, notes)
		return_doc.insert(ignore_permissions=True)
		file_doc = cls.attach_photo(return_doc.name, photo) if photo else None
		event_on = now()

		if file_doc:
			cls.set_if_field_exists(return_doc, "mobile_last_return_photo", file_doc.file_url)
			cls.set_if_field_exists(return_doc, "mobile_last_return_on", event_on)
		cls.apply_stock_entry_location(return_doc, "mobile_last_return", location)
		if file_doc or location:
			return_doc.save(ignore_permissions=True)

		doc.status = "Return Draft Created"
		doc.last_return_stock_entry = return_doc.name
		doc.last_return_on = event_on
		doc.return_count = cint(doc.return_count or 0) + 1
		if file_doc:
			doc.last_return_photo = file_doc.file_url
			doc.last_return_file = file_doc.name
		cls.apply_location(doc, "last_return", location)
		cls.append_log(doc, "Return Draft Created", event_on, user, file_doc, return_doc.name, notes, location)
		MaterialTransferHandoverRepository.save(doc)
		cls.sync_stock_entry_fields(doc)
		cls.add_task_update(
			doc,
			"Working",
			100,
			notes or _("Return draft {0} was created.").format(return_doc.name),
			doc.last_return_photo,
		)
		MaterialTransferHandoverRepository.commit()
		return {
			"status": "success",
			"message": "Return Stock Entry draft created.",
			"data": {
				"handover": cls.serialize(doc, True),
				"return_stock_entry": return_doc.name,
				"docstatus": return_doc.docstatus,
			},
		}

	@classmethod
	def get_permitted_doc(cls, name):
		cls.require_authenticated_user()
		if not name or not MaterialTransferHandoverRepository.exists(name):
			frappe.throw(_("Material Transfer Handover {0} was not found.").format(name), frappe.DoesNotExistError)
		doc = MaterialTransferHandoverRepository.get_doc(name)
		if not cls.can_access(doc):
			frappe.throw(_("Not permitted to access this Material Transfer Handover."), frappe.PermissionError)
		return doc

	@classmethod
	def get_receiver_doc(cls, name, user):
		doc = cls.get_permitted_doc(name)
		if doc.receiver_user != user:
			frappe.throw(_("Only the assigned receiver can update this handover."), frappe.PermissionError)
		return doc

	@staticmethod
	def can_access(doc):
		user = frappe.session.user
		if user == doc.receiver_user:
			return True
		return bool({"System Manager", "Stock Manager"} & set(frappe.get_roles(user)))

	@classmethod
	def get_return_options_data(cls, doc):
		options = {
			"can_return": doc.status in cls.RETURNABLE_STATUSES and cls.is_return_window_open(doc),
			"return_allowed_until": doc.return_allowed_until,
			"server_date": nowdate(),
			"items": [],
		}
		returned_by_row = cls.get_returned_quantities(doc)
		for row in cls.get_original_items(doc):
			returned_qty = flt(returned_by_row.get(row.get("stock_entry_detail")) or 0)
			remaining_qty = max(flt(row.get("qty")) - returned_qty, 0)
			row.update(
				{
					"returned_qty": returned_qty,
					"remaining_qty": remaining_qty,
					"returnable": remaining_qty > 0,
				}
			)
			options["items"].append(row)
		return options

	@staticmethod
	def get_original_items(doc):
		stock_entry = frappe.get_doc("Stock Entry", doc.stock_entry)
		items = []
		for row in stock_entry.get("items") or []:
			items.append(
				{
					"stock_entry_detail": row.name,
					"item_code": row.item_code,
					"item_name": row.item_name,
					"description": row.description,
					"qty": flt(row.qty),
					"uom": row.uom,
					"stock_uom": row.stock_uom,
					"conversion_factor": flt(row.conversion_factor or 1),
					"s_warehouse": row.s_warehouse or stock_entry.from_warehouse,
					"t_warehouse": row.t_warehouse or stock_entry.to_warehouse,
					"project": row.get("project") or stock_entry.get("project"),
					"basic_rate": flt(row.get("basic_rate") or 0),
				}
			)
		return items

	@staticmethod
	def get_returned_quantities(doc):
		return_entries = frappe.get_all(
			"Stock Entry",
			filters={
				"mobile_material_handover": doc.name,
				"mobile_handover_return_for": doc.stock_entry,
				"docstatus": ["<", 2],
			},
			pluck="name",
		)
		if not return_entries:
			return {}

		returned = {}
		rows = frappe.get_all(
			"Stock Entry Detail",
			filters={"parent": ["in", return_entries]},
			fields=["mobile_original_stock_entry_detail", "qty"],
		)
		for row in rows:
			key = row.get("mobile_original_stock_entry_detail")
			if key:
				returned[key] = flt(returned.get(key) or 0) + flt(row.get("qty") or 0)
		return returned

	@classmethod
	def validate_return_items(cls, doc, items):
		if isinstance(items, str):
			items = frappe.parse_json(items)
		if not isinstance(items, list):
			frappe.throw(_("items must be a list."))

		original_by_row = {row["stock_entry_detail"]: row for row in cls.get_original_items(doc)}
		returned_by_row = cls.get_returned_quantities(doc)
		selected = []
		for item in items:
			row_name = (item or {}).get("stock_entry_detail")
			qty = flt((item or {}).get("qty") or 0)
			if not row_name or row_name not in original_by_row:
				frappe.throw(_("Invalid Stock Entry Detail row: {0}").format(row_name))
			if qty <= 0:
				continue
			original = original_by_row[row_name]
			remaining = flt(original.get("qty")) - flt(returned_by_row.get(row_name) or 0)
			if qty > remaining:
				frappe.throw(
					_("Return quantity for item {0} exceeds remaining quantity {1}.").format(
						frappe.bold(original.get("item_code")),
						remaining,
					)
				)
			selected.append({"original": original, "qty": qty})
		return selected

	@classmethod
	def build_return_stock_entry(cls, doc, selected_items, notes=None):
		original = frappe.get_doc("Stock Entry", doc.stock_entry)
		return_doc = frappe.new_doc("Stock Entry")
		return_doc.stock_entry_type = "Material Transfer"
		return_doc.purpose = "Material Transfer"
		return_doc.company = original.company
		return_doc.posting_date = nowdate()
		return_doc.from_warehouse = doc.to_warehouse
		return_doc.to_warehouse = doc.from_warehouse
		return_doc.remarks = notes or _("Return draft for Material Transfer Handover {0}.").format(doc.name)
		cls.set_if_field_exists(return_doc, "mobile_material_handover", doc.name)
		cls.set_if_field_exists(return_doc, "mobile_handover_return_for", doc.stock_entry)
		cls.set_if_field_exists(return_doc, "mobile_no_receiver_required", 1)
		cls.set_if_field_exists(return_doc, "mobile_handover_status", "Return Draft Created")
		for item in selected_items:
			original_row = item["original"]
			row = return_doc.append(
				"items",
				{
					"item_code": original_row.get("item_code"),
					"qty": item.get("qty"),
					"uom": original_row.get("uom"),
					"stock_uom": original_row.get("stock_uom"),
					"conversion_factor": original_row.get("conversion_factor") or 1,
					"s_warehouse": original_row.get("t_warehouse"),
					"t_warehouse": original_row.get("s_warehouse"),
					"project": original_row.get("project"),
					"basic_rate": original_row.get("basic_rate"),
				},
			)
			cls.set_if_field_exists(row, "mobile_material_handover", doc.name)
			cls.set_if_field_exists(row, "mobile_original_stock_entry_detail", original_row.get("stock_entry_detail"))
		return return_doc

	@staticmethod
	def is_return_window_open(doc):
		if not doc.return_allowed_until:
			return False
		return getdate(nowdate()) <= getdate(doc.return_allowed_until)

	@classmethod
	def serialize(cls, doc, include_logs=False):
		data = doc.as_dict()
		data["can_update"] = cls.can_access(doc)
		data["can_confirm_pickup"] = doc.receiver_user == frappe.session.user and doc.status == "Pending Pickup"
		data["can_confirm_delivery"] = doc.receiver_user == frappe.session.user and doc.status == "Picked Up"
		data["can_create_return"] = (
			doc.receiver_user == frappe.session.user
			and doc.status in cls.RETURNABLE_STATUSES
			and cls.is_return_window_open(doc)
		)
		if include_logs:
			data["logs"] = [row.as_dict() for row in doc.get("logs") or []]
		else:
			data.pop("logs", None)
		return data

	@classmethod
	def sync_stock_entry_fields(cls, doc):
		values = {
			"mobile_material_handover": doc.name,
			"mobile_handover_status": doc.status,
			"mobile_handover_task": doc.task_follow_up,
			"mobile_pickup_photo": doc.pickup_photo,
			"mobile_pickup_on": doc.pickup_on,
			"mobile_pickup_location": doc.pickup_location,
			"mobile_pickup_latitude": doc.pickup_latitude,
			"mobile_pickup_longitude": doc.pickup_longitude,
			"mobile_pickup_accuracy_meters": doc.pickup_accuracy_meters,
			"mobile_delivery_photo": doc.delivery_photo,
			"mobile_delivery_on": doc.delivery_on,
			"mobile_delivery_location": doc.delivery_location,
			"mobile_delivery_latitude": doc.delivery_latitude,
			"mobile_delivery_longitude": doc.delivery_longitude,
			"mobile_delivery_accuracy_meters": doc.delivery_accuracy_meters,
			"mobile_last_return_stock_entry": doc.last_return_stock_entry,
			"mobile_last_return_photo": doc.last_return_photo,
			"mobile_last_return_on": doc.last_return_on,
			"mobile_last_return_location": doc.last_return_location,
			"mobile_last_return_latitude": doc.last_return_latitude,
			"mobile_last_return_longitude": doc.last_return_longitude,
			"mobile_last_return_accuracy_meters": doc.last_return_accuracy_meters,
		}
		cls.set_stock_entry_values(doc.stock_entry, values)

	@staticmethod
	def set_stock_entry_values(stock_entry, values):
		meta = frappe.get_meta("Stock Entry")
		for fieldname, value in values.items():
			if meta.has_field(fieldname):
				frappe.db.set_value("Stock Entry", stock_entry, fieldname, value, update_modified=False)

	@classmethod
	def add_task_update(cls, doc, status, progress, note, attachment=None):
		if not doc.task_follow_up or not frappe.db.exists("Mobile Task Follow Up", doc.task_follow_up):
			return
		task = frappe.get_doc("Mobile Task Follow Up", doc.task_follow_up)
		task.status = status
		task.progress = progress
		if status in {"Completed", "Cancelled"}:
			task.closed_by = frappe.session.user
			task.closed_on = now()
		task.append(
			"updates",
			{
				"update_date": nowdate(),
				"update_time": nowtime(),
				"note": note,
				"progress": task.progress,
				"status": task.status,
				"attachment": attachment or "",
				"updated_by": frappe.session.user,
			},
		)
		frappe.flags.mobile_material_handover_task_update = True
		try:
			task.save(ignore_permissions=True)
		finally:
			frappe.flags.mobile_material_handover_task_update = False

	@staticmethod
	def append_log(doc, event_type, event_on, event_by, file_doc=None, stock_entry=None, notes=None, location=None):
		doc.append(
			"logs",
			{
				"event_type": event_type,
				"event_on": event_on,
				"event_by": event_by,
				"stock_entry": stock_entry,
				"photo": file_doc.file_url if file_doc else None,
				"photo_file": file_doc.name if file_doc else None,
				"location": location.get("geolocation") if location else None,
				"latitude": location.get("latitude") if location else None,
				"longitude": location.get("longitude") if location else None,
				"accuracy_meters": location.get("accuracy_meters") if location else None,
				"notes": notes,
			},
		)

	@classmethod
	def prepare_location(
		cls,
		latitude=None,
		longitude=None,
		accuracy_meters=None,
		required=False,
		code="LOCATION_REQUIRED",
	):
		has_latitude = not cls.is_blank(latitude)
		has_longitude = not cls.is_blank(longitude)
		if not has_latitude and not has_longitude:
			if required:
				exc = frappe.ValidationError("Location is required.")
				exc.error_code = code
				raise exc
			return None
		if not has_latitude or not has_longitude:
			exc = frappe.ValidationError("Both latitude and longitude are required.")
			exc.error_code = "INVALID_LOCATION"
			raise exc

		lat = cls.parse_float(latitude, "latitude")
		lng = cls.parse_float(longitude, "longitude")
		if lat < -90 or lat > 90:
			exc = frappe.ValidationError("Latitude must be between -90 and 90.")
			exc.error_code = "INVALID_LATITUDE"
			raise exc
		if lng < -180 or lng > 180:
			exc = frappe.ValidationError("Longitude must be between -180 and 180.")
			exc.error_code = "INVALID_LONGITUDE"
			raise exc

		accuracy = None
		if not cls.is_blank(accuracy_meters):
			accuracy = cls.parse_float(accuracy_meters, "accuracy_meters")
			if accuracy < 0:
				exc = frappe.ValidationError("Accuracy meters must be zero or greater.")
				exc.error_code = "INVALID_ACCURACY"
				raise exc

		return {
			"latitude": lat,
			"longitude": lng,
			"accuracy_meters": accuracy,
			"geolocation": cls.build_geolocation(lat, lng, accuracy),
		}

	@staticmethod
	def build_geolocation(latitude, longitude, accuracy_meters=None):
		properties = {"point_type": "marker"}
		if accuracy_meters is not None:
			properties["accuracy_meters"] = accuracy_meters
		return json.dumps(
			{
				"type": "FeatureCollection",
				"features": [
					{
						"type": "Feature",
						"properties": properties,
						"geometry": {"type": "Point", "coordinates": [longitude, latitude]},
					}
				],
			},
			separators=(",", ":"),
		)

	@classmethod
	def apply_location(cls, doc, prefix, location):
		if not location:
			return
		cls.set_if_field_exists(doc, f"{prefix}_latitude", location.get("latitude"))
		cls.set_if_field_exists(doc, f"{prefix}_longitude", location.get("longitude"))
		cls.set_if_field_exists(doc, f"{prefix}_accuracy_meters", location.get("accuracy_meters"))
		cls.set_if_field_exists(doc, f"{prefix}_location", location.get("geolocation"))

	@classmethod
	def apply_stock_entry_location(cls, doc, prefix, location):
		if not location:
			return
		cls.set_if_field_exists(doc, f"{prefix}_latitude", location.get("latitude"))
		cls.set_if_field_exists(doc, f"{prefix}_longitude", location.get("longitude"))
		cls.set_if_field_exists(doc, f"{prefix}_accuracy_meters", location.get("accuracy_meters"))
		cls.set_if_field_exists(doc, f"{prefix}_location", location.get("geolocation"))

	@staticmethod
	def parse_float(value, label):
		try:
			return float(str(value).strip())
		except (TypeError, ValueError):
			exc = frappe.ValidationError(f"Invalid {label}.")
			exc.error_code = "INVALID_LOCATION"
			raise exc

	@staticmethod
	def is_blank(value):
		return value is None or str(value).strip() == ""

	@classmethod
	def prepare_photo(cls, photo_base64, photo_filename=None, required=False, code="PHOTO_REQUIRED", max_size_kb=2048):
		if not photo_base64:
			if required:
				exc = frappe.ValidationError("Photo is required.")
				exc.error_code = code
				raise exc
			return None

		data = (photo_base64 or "").strip()
		detected_mime_type = None
		if data.startswith("data:"):
			header, _separator, payload = data.partition(",")
			data = payload
			detected_mime_type = header[5:].split(";")[0].strip().lower()

		data = "".join(data.split())
		mime_type = (
			detected_mime_type
			or mimetypes.guess_type(photo_filename or "")[0]
			or ""
		).lower()
		if mime_type in ("image/jpg", "image/pjpeg"):
			mime_type = "image/jpeg"
		if mime_type not in ("image/jpeg", "image/png"):
			exc = frappe.ValidationError("Only JPEG and PNG photos are supported.")
			exc.error_code = "UNSUPPORTED_PHOTO_TYPE"
			raise exc

		try:
			content = base64.b64decode(data, validate=True)
		except Exception:
			exc = frappe.ValidationError("Invalid photo data.")
			exc.error_code = "INVALID_PHOTO"
			raise exc

		if not content:
			exc = frappe.ValidationError("Photo data is empty.")
			exc.error_code = "INVALID_PHOTO"
			raise exc
		if len(content) > max_size_kb * 1024:
			exc = frappe.ValidationError(f"Photo exceeds maximum size of {max_size_kb} KB.")
			exc.error_code = "PHOTO_TOO_LARGE"
			raise exc

		return {
			"content": content,
			"filename": cls.safe_photo_filename(photo_filename, mime_type),
		}

	@staticmethod
	def attach_photo(stock_entry, photo):
		if not photo:
			return None
		return save_file(
			photo.get("filename"),
			photo.get("content"),
			"Stock Entry",
			stock_entry,
			is_private=1,
		)

	@staticmethod
	def safe_photo_filename(photo_filename, mime_type):
		extension = ".jpg" if mime_type == "image/jpeg" else ".png"
		filename = (photo_filename or "").strip()
		if not filename:
			filename = f"material_handover_{frappe.generate_hash(length=8)}{extension}"
		filename = filename.split("/")[-1].split("\\")[-1]
		if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
			filename = f"{filename}{extension}"
		return filename

	@staticmethod
	def get_max_photo_size_kb(settings):
		return max(cint(settings.get("max_photo_size_kb") or 2048), 1)

	@staticmethod
	def set_if_field_exists(doc, fieldname, value):
		if doc.meta.has_field(fieldname):
			doc.set(fieldname, value)

	@staticmethod
	def require_authenticated_user():
		user = frappe.session.user
		if not user or user == "Guest":
			frappe.throw(_("User is not authenticated."), frappe.PermissionError)
		return user

	@staticmethod
	def error(message, code):
		return {"status": "error", "message": message, "code": code}


def create_task_for_handover(handover_doc):
	settings = MaterialTransferHandoverRepository.get_settings()
	if not cint(settings.get("auto_create_task_follow_up")):
		return None
	task_settings = MobileTaskFollowUpRepository.get_settings()
	if not cint(task_settings.get("enabled")):
		return None

	task = MobileTaskFollowUpRepository.insert(
		{
			"subject": _("Material Transfer Handover: {0}").format(handover_doc.stock_entry),
			"details": _("Receive and deliver materials from {0} to {1}.").format(
				handover_doc.from_warehouse or "-",
				handover_doc.to_warehouse or "-",
			),
			"priority": "Medium",
			"status": "Open",
			"progress": 0,
			"assigned_to_employee": handover_doc.receiver_employee,
			"assigned_to_user": handover_doc.receiver_user,
			"assigned_by": handover_doc.assigned_by or frappe.session.user,
			"start_date": handover_doc.posting_date or nowdate(),
			"due_date": handover_doc.return_allowed_until or handover_doc.posting_date or nowdate(),
			"source_doctype": "Stock Entry",
			"source_name": handover_doc.stock_entry,
		}
	)
	return task.name
