import frappe


FOLLOW_UP_TABLE_FIELD = "mobile_api_follow_ups"
SUMMARY_FIELD_MAP = {
    "mobile_api_last_update_date": "follow_up_date",
    "mobile_api_next_follow_up_date": "expected_result_date",
    "mobile_api_last_follow_up_report": "details",
    "mobile_api_follow_up_attachment": "attachment",
}


def get_latest_follow_up(doc):
    rows = doc.get(FOLLOW_UP_TABLE_FIELD) or []
    if not rows:
        return None

    return max(
        rows,
        key=lambda row: (
            cstr(row.get("follow_up_date") or ""),
            cstr(row.get("registered_on") or ""),
            cstr(row.get("creation") or ""),
            cstr(row.get("idx") or ""),
        ),
    )


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


def cstr(value):
    return frappe.utils.cstr(value)
