import frappe


FOLLOW_UP_TABLE_FIELD = "mobile_api_follow_ups"
SUPPORTED_DOCTYPES = ("Lead", "Opportunity", "Quotation")
SUMMARY_FIELD_MAP = {
    "mobile_api_last_update_date": "follow_up_date",
    "mobile_api_next_follow_up_date": "expected_result_date",
    "mobile_api_last_follow_up_report": "details",
    "mobile_api_follow_up_attachment": "attachment",
}


def row_sort_key(row):
    return (
        cstr(row.get("follow_up_date") or ""),
        cstr(row.get("registered_on") or ""),
        cstr(row.get("modified") or ""),
        cstr(row.get("creation") or ""),
        cstr(row.get("idx") or ""),
    )


def get_latest_follow_up(doc):
    rows = doc.get(FOLLOW_UP_TABLE_FIELD) or []
    if not rows:
        return None

    return max(rows, key=row_sort_key)


def sync_follow_up_summary(doc, method=None):
    latest_row = get_latest_follow_up(doc)

    if not latest_row:
        for target_field in SUMMARY_FIELD_MAP:
            if hasattr(doc, target_field):
                doc.set(target_field, None)
        return

    for target_field, source_field in SUMMARY_FIELD_MAP.items():
        if hasattr(doc, target_field):
            doc.set(target_field, latest_row.get(source_field))


def backfill_follow_up_summaries():
    for doctype in SUPPORTED_DOCTYPES:
        names = frappe.get_all(doctype, filters={"docstatus": ["!=", 2]}, pluck="name")
        for name in names:
            doc = frappe.get_doc(doctype, name)
            latest_row = get_latest_follow_up(doc)

            updates = {}
            for target_field, source_field in SUMMARY_FIELD_MAP.items():
                new_value = latest_row.get(source_field) if latest_row else None
                if doc.get(target_field) != new_value:
                    updates[target_field] = new_value

            if updates:
                frappe.db.set_value(doctype, name, updates, update_modified=False)

    frappe.db.commit()


def cstr(value):
    return frappe.utils.cstr(value)
