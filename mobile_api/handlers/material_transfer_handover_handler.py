import frappe

from mobile_api.services.material_transfer_handover_service import MaterialTransferHandoverService


def _handle_error(title, exc):
	frappe.log_error(frappe.get_traceback(), title)
	code = getattr(exc, "error_code", None)
	if not code:
		code = "PERMISSION_DENIED" if isinstance(exc, frappe.PermissionError) else "SERVER_ERROR"
	return {"status": "error", "message": str(exc), "code": code}


@frappe.whitelist()
def get_my_material_transfer_handovers(status=None, limit_start=0, limit_page_length=20):
	try:
		return MaterialTransferHandoverService.get_my_handovers(
			status=status,
			limit_start=limit_start,
			limit_page_length=limit_page_length,
		)
	except Exception as exc:
		return _handle_error("get_my_material_transfer_handovers", exc)


@frappe.whitelist()
def get_material_transfer_handover_details(name):
	try:
		return MaterialTransferHandoverService.get_details(name)
	except Exception as exc:
		return _handle_error("get_material_transfer_handover_details", exc)


@frappe.whitelist()
def confirm_material_transfer_pickup(
	name,
	photo_base64,
	photo_filename=None,
	notes=None,
	latitude=None,
	longitude=None,
	accuracy_meters=None,
):
	try:
		return MaterialTransferHandoverService.confirm_pickup(
			name=name,
			photo_base64=photo_base64,
			photo_filename=photo_filename,
			notes=notes,
			latitude=latitude,
			longitude=longitude,
			accuracy_meters=accuracy_meters,
		)
	except Exception as exc:
		return _handle_error("confirm_material_transfer_pickup", exc)


@frappe.whitelist()
def confirm_material_transfer_delivery(
	name,
	photo_base64,
	photo_filename=None,
	notes=None,
	latitude=None,
	longitude=None,
	accuracy_meters=None,
):
	try:
		return MaterialTransferHandoverService.confirm_delivery(
			name=name,
			photo_base64=photo_base64,
			photo_filename=photo_filename,
			notes=notes,
			latitude=latitude,
			longitude=longitude,
			accuracy_meters=accuracy_meters,
		)
	except Exception as exc:
		return _handle_error("confirm_material_transfer_delivery", exc)


@frappe.whitelist()
def get_material_transfer_return_options(name):
	try:
		return MaterialTransferHandoverService.get_return_options(name)
	except Exception as exc:
		return _handle_error("get_material_transfer_return_options", exc)


@frappe.whitelist()
def create_material_transfer_return(
	name,
	items,
	photo_base64=None,
	photo_filename=None,
	notes=None,
	latitude=None,
	longitude=None,
	accuracy_meters=None,
):
	try:
		return MaterialTransferHandoverService.create_return(
			name=name,
			items=items,
			photo_base64=photo_base64,
			photo_filename=photo_filename,
			notes=notes,
			latitude=latitude,
			longitude=longitude,
			accuracy_meters=accuracy_meters,
		)
	except Exception as exc:
		return _handle_error("create_material_transfer_return", exc)
