import frappe


STATUS_OPTIONS = "Not Started\nPending Pickup\nPicked Up\nDelivered\nReturn Draft Created\nClosed\nCancelled"


def execute():
	field_name = "Stock Entry-mobile_handover_status"
	if frappe.db.exists("Custom Field", field_name):
		frappe.db.set_value("Custom Field", field_name, "options", STATUS_OPTIONS)
		frappe.clear_cache(doctype="Stock Entry")
