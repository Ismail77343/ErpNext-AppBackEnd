import frappe


def mobile_task_follow_up_permission_query(user=None):
	user = user or frappe.session.user
	if not user or user == "Guest":
		return "1=0"
	if "System Manager" in frappe.get_roles(user):
		return ""

	table = "`tabMobile Task Follow Up`"
	escaped_user = frappe.db.escape(user)
	return f"({table}.assigned_to_user = {escaped_user} OR {table}.assigned_by = {escaped_user})"


def mobile_task_follow_up_has_permission(doc, user=None, ptype=None):
	user = user or frappe.session.user
	if not user or user == "Guest":
		return False
	if "System Manager" in frappe.get_roles(user):
		return True

	if isinstance(doc, str):
		doc = frappe.get_doc("Mobile Task Follow Up", doc)

	return doc.assigned_to_user == user or doc.assigned_by == user
