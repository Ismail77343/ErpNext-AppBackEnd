import frappe
from frappe.utils import cint, now


TPG_DOCTYPE = "Task Follow Up"
TPG_CHILD_DOCTYPE = "Child Follow"
MOBILE_DOCTYPE = "Mobile Task Follow Up"
MOBILE_CHILD_DOCTYPE = "Mobile Task Follow Up Update"
CLOSED_STATUSES = {"Completed", "Cancelled"}


def sync_mobile_from_tpg(doc, method=None):
	if not _can_sync():
		return
	if getattr(frappe.flags, "mobile_task_follow_up_syncing", False):
		return

	frappe.flags.mobile_task_follow_up_syncing = True
	try:
		_sync_mobile_from_tpg(doc)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Sync Task Follow Up to Mobile Task Follow Up")
	finally:
		frappe.flags.mobile_task_follow_up_syncing = False


def sync_tpg_from_mobile(doc, method=None):
	if not _can_sync():
		return
	if getattr(frappe.flags, "mobile_task_follow_up_syncing", False):
		return

	frappe.flags.mobile_task_follow_up_syncing = True
	try:
		_sync_tpg_from_mobile(doc)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Sync Mobile Task Follow Up to Task Follow Up")
	finally:
		frappe.flags.mobile_task_follow_up_syncing = False


def cancel_mobile_from_tpg(doc, method=None):
	if not _can_sync():
		return
	if getattr(frappe.flags, "mobile_task_follow_up_syncing", False):
		return

	frappe.flags.mobile_task_follow_up_syncing = True
	try:
		mobile_name = _get_mobile_name_from_tpg(doc)
		if not mobile_name:
			return
		mobile = frappe.get_doc(MOBILE_DOCTYPE, mobile_name)
		mobile.status = "Cancelled"
		mobile.closed_by = frappe.session.user
		mobile.closed_on = now()
		mobile.save(ignore_permissions=True)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Cancel Mobile Task Follow Up from Task Follow Up")
	finally:
		frappe.flags.mobile_task_follow_up_syncing = False


def _sync_mobile_from_tpg(tpg_doc):
	if not tpg_doc.get("assigned_to"):
		return

	mobile_name = _get_mobile_name_from_tpg(tpg_doc)
	values = _map_tpg_to_mobile_values(tpg_doc)

	if mobile_name:
		mobile = frappe.get_doc(MOBILE_DOCTYPE, mobile_name)
		for fieldname, value in values.items():
			if mobile.meta.has_field(fieldname):
				mobile.set(fieldname, value)
	else:
		mobile = frappe.get_doc({"doctype": MOBILE_DOCTYPE, **values})

	_sync_mobile_updates_from_tpg(tpg_doc, mobile)
	mobile.save(ignore_permissions=True)

	if tpg_doc.meta.has_field("mobile_task_follow_up") and tpg_doc.get("mobile_task_follow_up") != mobile.name:
		frappe.db.set_value(tpg_doc.doctype, tpg_doc.name, "mobile_task_follow_up", mobile.name, update_modified=False)

	_link_tpg_child_rows_from_mobile(mobile)


def _sync_tpg_from_mobile(mobile_doc):
	if not mobile_doc.get("assigned_to_user"):
		return

	tpg_name = _get_tpg_name_from_mobile(mobile_doc)
	values = _map_mobile_to_tpg_values(mobile_doc)

	if tpg_name:
		tpg_doc = frappe.get_doc(TPG_DOCTYPE, tpg_name)
		tpg_doc.flags.ignore_validate_update_after_submit = True
		for fieldname, value in values.items():
			if tpg_doc.meta.has_field(fieldname):
				tpg_doc.set(fieldname, value)
	else:
		tpg_doc = frappe.get_doc({"doctype": TPG_DOCTYPE, **values})

	_sync_tpg_child_follow_from_mobile(mobile_doc, tpg_doc)
	_set_tpg_log_fields(tpg_doc)
	tpg_doc.save(ignore_permissions=True)

	if mobile_doc.meta.has_field("tpg_task_follow_up") and mobile_doc.get("tpg_task_follow_up") != tpg_doc.name:
		frappe.db.set_value(mobile_doc.doctype, mobile_doc.name, "tpg_task_follow_up", tpg_doc.name, update_modified=False)
	if tpg_doc.meta.has_field("mobile_task_follow_up") and tpg_doc.get("mobile_task_follow_up") != mobile_doc.name:
		frappe.db.set_value(tpg_doc.doctype, tpg_doc.name, "mobile_task_follow_up", mobile_doc.name, update_modified=False)

	_link_mobile_update_rows_from_tpg(tpg_doc)


def _can_sync():
	if not frappe.db.exists("DocType", MOBILE_DOCTYPE):
		return False
	if not frappe.db.exists("DocType", TPG_DOCTYPE):
		return False
	if not frappe.db.exists("DocType", "Mobile Task Follow Up Settings"):
		return False
	setting = frappe.db.sql(
		"""
		select value
		from `tabSingles`
		where doctype = %s and field = %s
		limit 1
		""",
		("Mobile Task Follow Up Settings", "sync_with_tpg_task_follow_up"),
	)
	setting = setting[0][0] if setting else None
	if setting in (None, ""):
		return True
	return bool(cint(setting))


def _get_mobile_name_from_tpg(tpg_doc):
	if tpg_doc.meta.has_field("mobile_task_follow_up") and tpg_doc.get("mobile_task_follow_up"):
		if frappe.db.exists(MOBILE_DOCTYPE, tpg_doc.get("mobile_task_follow_up")):
			return tpg_doc.get("mobile_task_follow_up")

	return frappe.db.get_value(MOBILE_DOCTYPE, {"tpg_task_follow_up": tpg_doc.name}, "name")


def _get_tpg_name_from_mobile(mobile_doc):
	if mobile_doc.meta.has_field("tpg_task_follow_up") and mobile_doc.get("tpg_task_follow_up"):
		if frappe.db.exists(TPG_DOCTYPE, mobile_doc.get("tpg_task_follow_up")):
			return mobile_doc.get("tpg_task_follow_up")

	return frappe.db.get_value(TPG_DOCTYPE, {"mobile_task_follow_up": mobile_doc.name}, "name")


def _map_tpg_to_mobile_values(tpg_doc):
	assigned_to_user = tpg_doc.get("assigned_to")
	employee = _employee_for_user(assigned_to_user)
	status = "Cancelled" if tpg_doc.docstatus == 2 else (tpg_doc.get("status_task") or "Open")

	values = {
		"subject": tpg_doc.get("subject"),
		"details": tpg_doc.get("details") or "",
		"priority": tpg_doc.get("priority") or "Medium",
		"status": status,
		"progress": cint(tpg_doc.get("progress") or 0),
		"assigned_to_employee": employee,
		"assigned_to_user": assigned_to_user,
		"assigned_by": tpg_doc.get("assigned_by") or frappe.session.user,
		"read_by_assignee": cint(tpg_doc.get("read") or 0),
		"start_date": tpg_doc.get("start_date"),
		"due_date": tpg_doc.get("end_date"),
		"source_doctype": tpg_doc.get("ref_doctype"),
		"source_name": tpg_doc.get("ref_name"),
		"tpg_task_follow_up": tpg_doc.name,
	}

	if status in CLOSED_STATUSES:
		values["closed_by"] = tpg_doc.get("assigned_by") or frappe.session.user
		values["closed_on"] = now()
	else:
		values["closed_by"] = None
		values["closed_on"] = None

	return values


def _map_mobile_to_tpg_values(mobile_doc):
	return {
		"subject": mobile_doc.get("subject"),
		"details": mobile_doc.get("details") or "",
		"priority": mobile_doc.get("priority") or "Medium",
		"assigned_to": mobile_doc.get("assigned_to_user"),
		"assigned_by": mobile_doc.get("assigned_by") or frappe.session.user,
		"status_task": mobile_doc.get("status") or "Open",
		"progress": cint(mobile_doc.get("progress") or 0),
		"start_date": mobile_doc.get("start_date"),
		"end_date": mobile_doc.get("due_date"),
		"read": cint(mobile_doc.get("read_by_assignee") or 0),
		"ref_doctype": mobile_doc.get("source_doctype"),
		"ref_name": mobile_doc.get("source_name"),
		"mobile_task_follow_up": mobile_doc.name,
	}


def _sync_mobile_updates_from_tpg(tpg_doc, mobile_doc):
	if not mobile_doc.meta.has_field("updates"):
		return

	existing_by_tpg_child = {
		row.get("tpg_child_follow"): row
		for row in (mobile_doc.get("updates") or [])
		if row.get("tpg_child_follow")
	}

	for row in tpg_doc.get("child_follow") or []:
		update = None
		if row.get("mobile_task_follow_up_update"):
			update = next((item for item in mobile_doc.get("updates") or [] if item.name == row.get("mobile_task_follow_up_update")), None)
		if not update:
			update = existing_by_tpg_child.get(row.name)
		if not update:
			update = mobile_doc.append("updates", {})

		update.update_date = row.get("date_follow")
		update.update_time = row.get("time_follow")
		update.note = row.get("follow_up")
		update.progress = cint(row.get("progress") or 0)
		update.status = tpg_doc.get("status_task") or mobile_doc.get("status") or "Open"
		update.attachment = row.get("file") or ""
		update.updated_by = tpg_doc.get("assigned_to") or tpg_doc.get("assigned_by") or frappe.session.user
		update.tpg_child_follow = row.name


def _sync_tpg_child_follow_from_mobile(mobile_doc, tpg_doc):
	if not tpg_doc.meta.has_field("child_follow"):
		return

	existing_by_mobile_update = {
		row.get("mobile_task_follow_up_update"): row
		for row in (tpg_doc.get("child_follow") or [])
		if row.get("mobile_task_follow_up_update")
	}

	for row in mobile_doc.get("updates") or []:
		child = None
		if row.get("tpg_child_follow"):
			child = next((item for item in tpg_doc.get("child_follow") or [] if item.name == row.get("tpg_child_follow")), None)
		if not child:
			child = existing_by_mobile_update.get(row.name)
		if not child:
			child = tpg_doc.append("child_follow", {})

		child.date_follow = row.get("update_date")
		child.time_follow = row.get("update_time")
		child.follow_up = row.get("note")
		child.progress = cint(row.get("progress") or 0)
		child.file = row.get("attachment") or ""
		child.date_time_registration = row.get("creation") or now()
		if child.meta.has_field("mobile_task_follow_up_update"):
			child.mobile_task_follow_up_update = row.name


def _link_tpg_child_rows_from_mobile(mobile_doc):
	if not frappe.db.exists("DocType", TPG_CHILD_DOCTYPE):
		return
	if not frappe.get_meta(TPG_CHILD_DOCTYPE).has_field("mobile_task_follow_up_update"):
		return

	for row in mobile_doc.get("updates") or []:
		if row.get("tpg_child_follow"):
			frappe.db.set_value(
				TPG_CHILD_DOCTYPE,
				row.get("tpg_child_follow"),
				"mobile_task_follow_up_update",
				row.name,
				update_modified=False,
			)


def _link_mobile_update_rows_from_tpg(tpg_doc):
	if not frappe.get_meta(MOBILE_CHILD_DOCTYPE).has_field("tpg_child_follow"):
		return

	for row in tpg_doc.get("child_follow") or []:
		if row.get("mobile_task_follow_up_update"):
			frappe.db.set_value(
				MOBILE_CHILD_DOCTYPE,
				row.get("mobile_task_follow_up_update"),
				"tpg_child_follow",
				row.name,
				update_modified=False,
			)


def _set_tpg_log_fields(tpg_doc):
	rows = list(tpg_doc.get("child_follow") or [])
	if not rows:
		return

	latest = rows[-1]
	summary = "{0} | {1}% | {2} {3} - {4}".format(
		tpg_doc.get("status_task") or "Open",
		cint(tpg_doc.get("progress") or 0),
		latest.get("date_follow") or "",
		latest.get("time_follow") or "",
		latest.get("follow_up") or "",
	).strip()

	if tpg_doc.meta.has_field("last_update_summary"):
		tpg_doc.last_update_summary = summary

	if not tpg_doc.meta.has_field("log_follow"):
		return

	lines = []
	for idx, row in enumerate(reversed(rows), 1):
		dt = "{0} {1}".format(row.get("date_follow") or "", row.get("time_follow") or "").strip()
		reg = " | Registered: {0}".format(row.get("date_time_registration")) if row.get("date_time_registration") else ""
		progress = " | {0}%".format(row.get("progress")) if row.get("progress") is not None else ""
		note = (row.get("follow_up") or "").replace("\n", " ")
		lines.append("{0}) {1}{2}{3}\n   - {4}".format(idx, dt, reg, progress, note))

	tpg_doc.log_follow = "\n\n".join(lines)


def _employee_for_user(user):
	if not user:
		return None
	return frappe.db.get_value("Employee", {"user_id": user, "status": "Active"}, "name")
