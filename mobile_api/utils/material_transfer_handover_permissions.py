import frappe


def material_transfer_handover_permission_query(user=None):
	user = user or frappe.session.user
	if not user or user == "Guest":
		return "1=0"
	if {"System Manager", "Stock Manager"} & set(frappe.get_roles(user)):
		return ""
	return f"`tabMobile Material Transfer Handover`.`receiver_user` = {frappe.db.escape(user)}"


def material_transfer_handover_has_permission(doc, ptype=None, user=None):
	user = user or frappe.session.user
	if not user or user == "Guest":
		return False
	if {"System Manager", "Stock Manager"} & set(frappe.get_roles(user)):
		return True
	return doc.receiver_user == user
