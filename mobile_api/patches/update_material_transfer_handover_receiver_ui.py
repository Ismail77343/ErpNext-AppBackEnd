import frappe


MATERIAL_TRANSFER_CONDITION = (
	"eval:doc.purpose == 'Material Transfer' || doc.stock_entry_type == 'Material Transfer'"
)
RECEIVER_REQUIRED_CONDITION = (
	"eval:(doc.purpose == 'Material Transfer' || doc.stock_entry_type == 'Material Transfer')"
	" && !doc.mobile_no_receiver_required"
)


def execute():
	updates = {
		"Stock Entry-mobile_material_handover_section": {
			"depends_on": MATERIAL_TRANSFER_CONDITION,
		},
		"Stock Entry-mobile_handover_receiver_user": {
			"depends_on": RECEIVER_REQUIRED_CONDITION,
			"mandatory_depends_on": RECEIVER_REQUIRED_CONDITION,
		},
		"Stock Entry-mobile_no_receiver_required": {
			"depends_on": MATERIAL_TRANSFER_CONDITION,
		},
		"Stock Entry-mobile_material_handover": {
			"depends_on": MATERIAL_TRANSFER_CONDITION,
		},
		"Stock Entry-mobile_handover_status": {
			"depends_on": MATERIAL_TRANSFER_CONDITION,
		},
		"Stock Entry-mobile_handover_task": {
			"depends_on": MATERIAL_TRANSFER_CONDITION,
		},
		"Stock Entry-mobile_pickup_photo": {
			"depends_on": MATERIAL_TRANSFER_CONDITION,
		},
		"Stock Entry-mobile_pickup_on": {
			"depends_on": MATERIAL_TRANSFER_CONDITION,
		},
		"Stock Entry-mobile_delivery_photo": {
			"depends_on": MATERIAL_TRANSFER_CONDITION,
		},
		"Stock Entry-mobile_delivery_on": {
			"depends_on": MATERIAL_TRANSFER_CONDITION,
		},
		"Stock Entry-mobile_last_return_stock_entry": {
			"depends_on": MATERIAL_TRANSFER_CONDITION,
		},
		"Stock Entry-mobile_last_return_photo": {
			"depends_on": MATERIAL_TRANSFER_CONDITION,
		},
		"Stock Entry-mobile_last_return_on": {
			"depends_on": MATERIAL_TRANSFER_CONDITION,
		},
	}
	for custom_field, values in updates.items():
		if frappe.db.exists("Custom Field", custom_field):
			frappe.db.set_value("Custom Field", custom_field, values)
	frappe.clear_cache(doctype="Stock Entry")
