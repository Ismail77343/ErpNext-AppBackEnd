import json

import frappe


class MobileAccessControl:
    """Shared mobile API access checks.

    The mobile app should only show records that are both readable by Frappe
    permissions and directly related to the current user.
    """

    STANDARD_FIELDS = {
        "name",
        "owner",
        "_assign",
        "creation",
        "modified",
        "modified_by",
        "docstatus",
        "idx",
    }

    @staticmethod
    def current_user():
        return frappe.session.user

    @classmethod
    def get_current_employee(cls):
        return frappe.db.get_value("Employee", {"user_id": cls.current_user(), "status": "Active"}, "name")

    @classmethod
    def get_current_sales_persons(cls):
        employee = cls.get_current_employee()
        if not employee:
            return []
        return frappe.get_all("Sales Person", filters={"employee": employee}, pluck="name")

    @classmethod
    def get_user_link_filters(cls, doctype, user_fields=None, sales_person_fields=None):
        user = cls.current_user()
        user_fields = user_fields or []
        sales_person_fields = sales_person_fields or []

        or_filters = [[doctype, "owner", "=", user]]
        for fieldname in user_fields:
            if cls.has_field(doctype, fieldname):
                or_filters.append([doctype, fieldname, "=", user])

        sales_persons = cls.get_current_sales_persons()
        if sales_persons:
            for fieldname in sales_person_fields:
                if cls.has_field(doctype, fieldname):
                    or_filters.append([doctype, fieldname, "in", sales_persons])

        return or_filters

    @staticmethod
    def has_field(doctype, fieldname):
        return fieldname in MobileAccessControl.STANDARD_FIELDS or frappe.get_meta(doctype).has_field(fieldname)

    @classmethod
    def existing_fields(cls, doctype, fields):
        return [fieldname for fieldname in fields if cls.has_field(doctype, fieldname)]

    @classmethod
    def search_or_filters(cls, doctype, fields, value):
        return [[doctype, fieldname, "like", value] for fieldname in cls.existing_fields(doctype, fields)]

    @classmethod
    def filter_user_related_rows(cls, doctype, rows, user_fields=None, sales_person_fields=None):
        user = cls.current_user()
        sales_persons = set(cls.get_current_sales_persons())
        user_fields = user_fields or []
        sales_person_fields = sales_person_fields or []

        filtered = []
        for row in rows:
            if row.get("owner") == user:
                filtered.append(row)
                continue
            if any(row.get(fieldname) == user for fieldname in user_fields):
                filtered.append(row)
                continue
            if sales_persons and any(row.get(fieldname) in sales_persons for fieldname in sales_person_fields):
                filtered.append(row)
                continue
            if cls._is_assigned_to_user(row.get("_assign"), user):
                filtered.append(row)
                continue
            if doctype == "Project" and cls._is_project_user(row.get("name"), user):
                filtered.append(row)
                continue
        return filtered

    @staticmethod
    def _is_assigned_to_user(assign_value, user):
        if not assign_value:
            return False
        try:
            assigned_users = json.loads(assign_value) if isinstance(assign_value, str) else assign_value
        except (TypeError, ValueError):
            return False
        return user in (assigned_users or [])

    @staticmethod
    def _is_project_user(project, user):
        if not project:
            return False
        if frappe.db.exists("DocType", "Project User"):
            return bool(frappe.db.exists("Project User", {"parent": project, "user": user}))
        return False

    @classmethod
    def ensure_read_access(cls, doctype, name, user_fields=None, sales_person_fields=None):
        doc = frappe.get_doc(doctype, name)
        if not doc.has_permission("read"):
            frappe.throw("You do not have permission to access this document.", frappe.PermissionError)

        row = doc.as_dict()
        if not cls.filter_user_related_rows(doctype, [row], user_fields=user_fields, sales_person_fields=sales_person_fields):
            frappe.throw("This document is not assigned to your mobile user.", frappe.PermissionError)
        return doc

    @classmethod
    def ensure_write_access(cls, doctype, name, user_fields=None, sales_person_fields=None):
        doc = cls.ensure_read_access(doctype, name, user_fields=user_fields, sales_person_fields=sales_person_fields)
        if not doc.has_permission("write"):
            frappe.throw("You do not have permission to update this document.", frappe.PermissionError)
        return doc
