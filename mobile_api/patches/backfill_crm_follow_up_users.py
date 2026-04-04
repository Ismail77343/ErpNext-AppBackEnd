import frappe


def execute():
    if not frappe.db.has_column("Mobile CRM Follow Up", "followed_by"):
        return

    rows = frappe.db.sql(
        """
        select name, owner
        from `tabMobile CRM Follow Up`
        where ifnull(followed_by, '') = ''
        """,
        as_dict=True,
    )

    for row in rows:
        owner = row.get("owner")
        if not owner or owner == "Guest":
            continue

        followed_by = frappe.db.get_value("User", owner, "full_name") or owner
        frappe.db.set_value(
            "Mobile CRM Follow Up",
            row.get("name"),
            "followed_by",
            followed_by,
            update_modified=False,
        )
