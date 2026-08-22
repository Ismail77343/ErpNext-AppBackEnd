import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


MATERIAL_TRANSFER_CONDITION = (
	"eval:doc.purpose == 'Material Transfer' || doc.stock_entry_type == 'Material Transfer'"
)


def execute():
	ensure_settings_defaults()
	if not frappe.db.exists("DocType", "Stock Entry"):
		return

	create_custom_fields(
		{
			"Stock Entry": [
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
		},
		ignore_validate=True,
	)
	frappe.clear_cache(doctype="Stock Entry")


def ensure_settings_defaults():
	if not frappe.db.exists("DocType", "Mobile Material Transfer Handover Settings"):
		return
	defaults = {
		"require_pickup_location": 1,
		"require_delivery_location": 1,
		"require_return_location": 1,
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
