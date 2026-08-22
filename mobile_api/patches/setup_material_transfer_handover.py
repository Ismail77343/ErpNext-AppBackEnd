import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


STATUS_OPTIONS = "Not Started\nPending Pickup\nPicked Up\nDelivered\nReturn Draft Created\nClosed\nCancelled"
MATERIAL_TRANSFER_CONDITION = (
	"eval:doc.purpose == 'Material Transfer' || doc.stock_entry_type == 'Material Transfer'"
)
RECEIVER_REQUIRED_CONDITION = (
	"eval:(doc.purpose == 'Material Transfer' || doc.stock_entry_type == 'Material Transfer')"
	" && !doc.mobile_no_receiver_required"
)


def execute():
	if not frappe.db.exists("DocType", "Stock Entry"):
		return

	create_custom_fields(
		{
			"Stock Entry": [
				{
					"fieldname": "mobile_material_handover_section",
					"label": "Material Transfer Handover",
					"fieldtype": "Section Break",
					"insert_after": "task",
					"depends_on": MATERIAL_TRANSFER_CONDITION,
				},
				{
					"fieldname": "mobile_handover_receiver_user",
					"label": "Receiver User",
					"fieldtype": "Link",
					"options": "User",
					"insert_after": "mobile_material_handover_section",
					"depends_on": RECEIVER_REQUIRED_CONDITION,
					"mandatory_depends_on": RECEIVER_REQUIRED_CONDITION,
				},
				{
					"fieldname": "mobile_no_receiver_required",
					"label": "No Receiver Required",
					"fieldtype": "Check",
					"insert_after": "mobile_handover_receiver_user",
					"depends_on": MATERIAL_TRANSFER_CONDITION,
				},
				{
					"fieldname": "mobile_material_handover",
					"label": "Mobile Material Handover",
					"fieldtype": "Link",
					"options": "Mobile Material Transfer Handover",
					"insert_after": "mobile_no_receiver_required",
					"read_only": 1,
					"depends_on": MATERIAL_TRANSFER_CONDITION,
				},
				{
					"fieldname": "mobile_handover_status",
					"label": "Handover Status",
					"fieldtype": "Select",
					"options": STATUS_OPTIONS,
					"default": "Not Started",
					"insert_after": "mobile_material_handover",
					"read_only": 1,
					"depends_on": MATERIAL_TRANSFER_CONDITION,
				},
				{
					"fieldname": "mobile_handover_task",
					"label": "Handover Task",
					"fieldtype": "Link",
					"options": "Mobile Task Follow Up",
					"insert_after": "mobile_handover_status",
					"read_only": 1,
					"depends_on": MATERIAL_TRANSFER_CONDITION,
				},
				{
					"fieldname": "mobile_handover_return_for",
					"label": "Handover Return For",
					"fieldtype": "Link",
					"options": "Stock Entry",
					"insert_after": "mobile_handover_task",
					"hidden": 1,
					"read_only": 1,
				},
				{
					"fieldname": "mobile_handover_column_break",
					"fieldtype": "Column Break",
					"insert_after": "mobile_handover_return_for",
				},
				{
					"fieldname": "mobile_pickup_photo",
					"label": "Pickup Photo",
					"fieldtype": "Attach",
					"insert_after": "mobile_handover_column_break",
					"read_only": 1,
					"depends_on": MATERIAL_TRANSFER_CONDITION,
				},
				{
					"fieldname": "mobile_pickup_on",
					"label": "Pickup On",
					"fieldtype": "Datetime",
					"insert_after": "mobile_pickup_photo",
					"read_only": 1,
					"depends_on": MATERIAL_TRANSFER_CONDITION,
				},
				{
					"fieldname": "mobile_pickup_location",
					"label": "Pickup Location",
					"fieldtype": "Geolocation",
					"insert_after": "mobile_pickup_on",
					"read_only": 1,
					"depends_on": MATERIAL_TRANSFER_CONDITION,
				},
				{
					"fieldname": "mobile_pickup_latitude",
					"label": "Pickup Latitude",
					"fieldtype": "Float",
					"insert_after": "mobile_pickup_location",
					"hidden": 1,
					"read_only": 1,
					"depends_on": MATERIAL_TRANSFER_CONDITION,
				},
				{
					"fieldname": "mobile_pickup_longitude",
					"label": "Pickup Longitude",
					"fieldtype": "Float",
					"insert_after": "mobile_pickup_latitude",
					"hidden": 1,
					"read_only": 1,
					"depends_on": MATERIAL_TRANSFER_CONDITION,
				},
				{
					"fieldname": "mobile_pickup_accuracy_meters",
					"label": "Pickup Accuracy Meters",
					"fieldtype": "Float",
					"insert_after": "mobile_pickup_longitude",
					"hidden": 1,
					"read_only": 1,
					"depends_on": MATERIAL_TRANSFER_CONDITION,
				},
				{
					"fieldname": "mobile_delivery_photo",
					"label": "Delivery Photo",
					"fieldtype": "Attach",
					"insert_after": "mobile_pickup_accuracy_meters",
					"read_only": 1,
					"depends_on": MATERIAL_TRANSFER_CONDITION,
				},
				{
					"fieldname": "mobile_delivery_on",
					"label": "Delivery On",
					"fieldtype": "Datetime",
					"insert_after": "mobile_delivery_photo",
					"read_only": 1,
					"depends_on": MATERIAL_TRANSFER_CONDITION,
				},
				{
					"fieldname": "mobile_delivery_location",
					"label": "Delivery Location",
					"fieldtype": "Geolocation",
					"insert_after": "mobile_delivery_on",
					"read_only": 1,
					"depends_on": MATERIAL_TRANSFER_CONDITION,
				},
				{
					"fieldname": "mobile_delivery_latitude",
					"label": "Delivery Latitude",
					"fieldtype": "Float",
					"insert_after": "mobile_delivery_location",
					"hidden": 1,
					"read_only": 1,
					"depends_on": MATERIAL_TRANSFER_CONDITION,
				},
				{
					"fieldname": "mobile_delivery_longitude",
					"label": "Delivery Longitude",
					"fieldtype": "Float",
					"insert_after": "mobile_delivery_latitude",
					"hidden": 1,
					"read_only": 1,
					"depends_on": MATERIAL_TRANSFER_CONDITION,
				},
				{
					"fieldname": "mobile_delivery_accuracy_meters",
					"label": "Delivery Accuracy Meters",
					"fieldtype": "Float",
					"insert_after": "mobile_delivery_longitude",
					"hidden": 1,
					"read_only": 1,
					"depends_on": MATERIAL_TRANSFER_CONDITION,
				},
				{
					"fieldname": "mobile_last_return_stock_entry",
					"label": "Last Return Stock Entry",
					"fieldtype": "Link",
					"options": "Stock Entry",
					"insert_after": "mobile_delivery_accuracy_meters",
					"read_only": 1,
					"depends_on": MATERIAL_TRANSFER_CONDITION,
				},
				{
					"fieldname": "mobile_last_return_photo",
					"label": "Last Return Photo",
					"fieldtype": "Attach",
					"insert_after": "mobile_last_return_stock_entry",
					"read_only": 1,
					"depends_on": MATERIAL_TRANSFER_CONDITION,
				},
				{
					"fieldname": "mobile_last_return_on",
					"label": "Last Return On",
					"fieldtype": "Datetime",
					"insert_after": "mobile_last_return_photo",
					"read_only": 1,
					"depends_on": MATERIAL_TRANSFER_CONDITION,
				},
				{
					"fieldname": "mobile_last_return_location",
					"label": "Last Return Location",
					"fieldtype": "Geolocation",
					"insert_after": "mobile_last_return_on",
					"read_only": 1,
					"depends_on": MATERIAL_TRANSFER_CONDITION,
				},
				{
					"fieldname": "mobile_last_return_latitude",
					"label": "Last Return Latitude",
					"fieldtype": "Float",
					"insert_after": "mobile_last_return_location",
					"hidden": 1,
					"read_only": 1,
					"depends_on": MATERIAL_TRANSFER_CONDITION,
				},
				{
					"fieldname": "mobile_last_return_longitude",
					"label": "Last Return Longitude",
					"fieldtype": "Float",
					"insert_after": "mobile_last_return_latitude",
					"hidden": 1,
					"read_only": 1,
					"depends_on": MATERIAL_TRANSFER_CONDITION,
				},
				{
					"fieldname": "mobile_last_return_accuracy_meters",
					"label": "Last Return Accuracy Meters",
					"fieldtype": "Float",
					"insert_after": "mobile_last_return_longitude",
					"hidden": 1,
					"read_only": 1,
					"depends_on": MATERIAL_TRANSFER_CONDITION,
				},
			],
			"Stock Entry Detail": [
				{
					"fieldname": "mobile_material_handover",
					"label": "Mobile Material Handover",
					"fieldtype": "Link",
					"options": "Mobile Material Transfer Handover",
					"insert_after": "project",
					"hidden": 1,
					"read_only": 1,
				},
				{
					"fieldname": "mobile_original_stock_entry_detail",
					"label": "Original Stock Entry Detail",
					"fieldtype": "Data",
					"insert_after": "mobile_material_handover",
					"hidden": 1,
					"read_only": 1,
				},
			],
		},
		ignore_validate=True,
	)
	ensure_settings_defaults()
	frappe.clear_cache(doctype="Stock Entry")
	frappe.clear_cache(doctype="Stock Entry Detail")


def ensure_settings_defaults():
	if not frappe.db.exists("DocType", "Mobile Material Transfer Handover Settings"):
		return
	defaults = {
		"enabled": 1,
		"auto_create_task_follow_up": 1,
		"require_pickup_photo": 1,
		"require_pickup_location": 1,
		"require_delivery_photo": 1,
		"require_delivery_location": 1,
		"require_return_photo": 1,
		"require_return_location": 1,
		"max_photo_size_kb": 2048,
		"return_allowed_days_after_submit": 1,
	}
	for fieldname, value in defaults.items():
		exists = frappe.db.sql(
			"""
			select value
			from `tabSingles`
			where doctype = %s and field = %s
			limit 1
			""",
			("Mobile Material Transfer Handover Settings", fieldname),
		)
		if not exists:
			frappe.db.set_single_value("Mobile Material Transfer Handover Settings", fieldname, value)
