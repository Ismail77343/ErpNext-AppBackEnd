import frappe
from frappe.model.workflow import get_transitions, get_workflow_name


class NotificationRepository:
    @staticmethod
    def get_open_workflow_todos(user, limit_start=None, limit_page_length=None):
        return frappe.get_all(
            "ToDo",
            filters={
                "allocated_to": user,
                "status": ["not in", ["Closed", "Cancelled"]],
                "reference_type": ["is", "set"],
                "reference_name": ["is", "set"],
            },
            fields=[
                "name",
                "allocated_to",
                "reference_type",
                "reference_name",
                "description",
                "priority",
                "status",
                "date",
                "modified",
                "owner",
            ],
            order_by="modified desc",
            limit_start=limit_start,
            limit_page_length=limit_page_length,
        )

    @staticmethod
    def get_reference_doc(doctype, docname):
        if not doctype or not docname or not frappe.db.exists(doctype, docname):
            return None
        return frappe.get_doc(doctype, docname)

    @staticmethod
    def get_workflow_actions(doc):
        workflow_name = get_workflow_name(doc.doctype)
        if not workflow_name:
            return []
        return get_transitions(doc)

    @staticmethod
    def has_workflow(doctype):
        return bool(get_workflow_name(doctype))
