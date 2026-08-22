import frappe
from frappe import _
from frappe.utils import add_days, cint, now, nowdate

from mobile_api.repositories.material_transfer_handover_repository import (
	MaterialTransferHandoverRepository,
)
from mobile_api.services.material_transfer_handover_service import (
	MaterialTransferHandoverService,
	create_task_for_handover,
)


def validate_material_transfer_handover(doc, method=None):
	if not _is_enabled():
		return
	if not _is_material_transfer_candidate(doc):
		return
	if doc.get("mobile_no_receiver_required"):
		return
	if not doc.get("mobile_handover_receiver_user"):
		frappe.throw(_("Receiver User is required for Material Transfer handover."))


def create_material_transfer_handover(doc, method=None):
	if not _is_enabled():
		return
	if not _is_material_transfer_candidate(doc):
		return
	if doc.get("mobile_no_receiver_required"):
		return

	receiver_user = doc.get("mobile_handover_receiver_user")
	if not receiver_user:
		frappe.throw(_("Receiver User is required for Material Transfer handover."))

	existing = MaterialTransferHandoverRepository.find_by_stock_entry(doc.name)
	if existing:
		MaterialTransferHandoverService.set_stock_entry_values(
			doc.name,
			{
				"mobile_material_handover": existing,
				"mobile_handover_status": frappe.db.get_value(
					"Mobile Material Transfer Handover",
					existing,
					"status",
				),
			},
		)
		return

	settings = MaterialTransferHandoverRepository.get_settings()
	from_warehouse, to_warehouse = _get_transfer_warehouses(doc)
	employee = frappe.db.get_value(
		"Employee",
		{"user_id": receiver_user, "status": "Active"},
		"name",
	)
	handover = MaterialTransferHandoverRepository.insert(
		{
			"stock_entry": doc.name,
			"company": doc.get("company"),
			"posting_date": doc.get("posting_date"),
			"submitted_on": now(),
			"status": "Pending Pickup",
			"receiver_user": receiver_user,
			"receiver_employee": employee,
			"assigned_by": frappe.session.user,
			"from_warehouse": from_warehouse,
			"to_warehouse": to_warehouse,
			"return_allowed_until": add_days(
				doc.get("posting_date") or nowdate(),
				max(cint(settings.get("return_allowed_days_after_submit") or 1), 0),
			),
		}
	)
	task_name = create_task_for_handover(handover)
	if task_name:
		handover.task_follow_up = task_name
		MaterialTransferHandoverRepository.save(handover)

	MaterialTransferHandoverService.set_stock_entry_values(
		doc.name,
		{
			"mobile_material_handover": handover.name,
			"mobile_handover_status": handover.status,
			"mobile_handover_task": handover.task_follow_up,
		},
	)


def cancel_material_transfer_handover(doc, method=None):
	if not frappe.db.exists("DocType", "Mobile Material Transfer Handover"):
		return
	handover_name = (
		doc.get("mobile_material_handover")
		or MaterialTransferHandoverRepository.find_by_stock_entry(doc.name)
	)
	if not handover_name:
		return

	handover = MaterialTransferHandoverRepository.get_doc(handover_name)
	if handover.status == "Pending Pickup":
		handover.status = "Cancelled"
		MaterialTransferHandoverService.append_log(
			handover,
			"Cancelled",
			now(),
			frappe.session.user,
			stock_entry=doc.name,
			notes=_("Original Stock Entry was cancelled before pickup."),
		)
		MaterialTransferHandoverRepository.save(handover)
		MaterialTransferHandoverService.sync_stock_entry_fields(handover)
		return

	MaterialTransferHandoverService.append_log(
		handover,
		"Cancelled",
		now(),
		frappe.session.user,
		stock_entry=doc.name,
		notes=_("Original Stock Entry was cancelled after handover activity."),
	)
	MaterialTransferHandoverRepository.save(handover)


def _is_enabled():
	settings = MaterialTransferHandoverRepository.get_settings()
	return bool(cint(settings.get("enabled")))


def _is_material_transfer_candidate(doc):
	if doc.doctype != "Stock Entry":
		return False
	if doc.get("purpose") != "Material Transfer":
		return False
	if doc.get("mobile_handover_return_for"):
		return False
	return True


def _get_transfer_warehouses(doc):
	from_warehouse = doc.get("from_warehouse")
	to_warehouse = doc.get("to_warehouse")
	for row in doc.get("items") or []:
		if not from_warehouse and row.get("s_warehouse"):
			from_warehouse = row.get("s_warehouse")
		if not to_warehouse and row.get("t_warehouse"):
			to_warehouse = row.get("t_warehouse")
		if from_warehouse and to_warehouse:
			break
	return from_warehouse, to_warehouse
