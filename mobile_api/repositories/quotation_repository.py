import frappe
from frappe.model.workflow import apply_workflow, get_transitions, get_workflow_name

from mobile_api.repositories.crm_follow_up_repository import CRMFollowUpRepository


class QuotationRepository:
    LIST_FIELDS = [
        "name",
        "customer_name",
        "party_name",
        "status",
        "workflow_state",
        "contact_email",
        "contact_mobile",
        "transaction_date",
        "valid_till",
        "currency",
        "grand_total",
        "opportunity",
        "order_type",
        "mobile_api_last_update_date",
        "mobile_api_next_follow_up_date",
        "mobile_api_last_follow_up_report",
        "modified",
    ]

    @staticmethod
    def get_quotation(quotation_name):
        return frappe.get_doc("Quotation", quotation_name)

    @classmethod
    def query_quotations(cls, filters=None, search=None, limit_start=None, limit_page_length=None):
        quotation_filters = filters or {}
        or_filters = []

        if search:
            like_value = f"%{search}%"
            or_filters = [
                ["Quotation", "name", "like", like_value],
                ["Quotation", "customer_name", "like", like_value],
                ["Quotation", "party_name", "like", like_value],
                ["Quotation", "contact_mobile", "like", like_value],
                ["Quotation", "contact_email", "like", like_value],
            ]

        return frappe.get_all(
            "Quotation",
            filters=quotation_filters,
            or_filters=or_filters or None,
            fields=cls.LIST_FIELDS,
            order_by="modified desc",
            limit_start=limit_start,
            limit_page_length=limit_page_length,
        )

    @staticmethod
    def quotation_exists(quotation_name):
        return bool(frappe.db.exists("Quotation", quotation_name))

    @staticmethod
    def get_follow_ups(doc):
        return CRMFollowUpRepository.get_follow_ups(doc)

    @staticmethod
    def get_activity_log(quotation_name):
        return CRMFollowUpRepository.get_activity_log("Quotation", quotation_name)

    @staticmethod
    def add_follow_up(doc, follow_up_date, expected_result_date, details, attachment=None):
        CRMFollowUpRepository.append_follow_up(
            doc=doc,
            follow_up_date=follow_up_date,
            expected_result_date=expected_result_date,
            details=details,
            attachment=attachment,
        )

    @staticmethod
    def save_quotation(doc):
        doc.save()
        frappe.db.commit()
        return doc

    @staticmethod
    def get_workflow_actions(doc):
        workflow_name = get_workflow_name(doc.doctype)
        if not workflow_name:
            return []
        return get_transitions(doc)

    @staticmethod
    def get_workflow_name():
        return get_workflow_name("Quotation")

    @staticmethod
    def apply_workflow_action(doc, action):
        updated_doc = apply_workflow(doc.as_dict(), action)
        frappe.db.commit()
        return updated_doc

    @staticmethod
    def get_print_formats():
        rows = frappe.get_all(
            "Print Format",
            filters={"doc_type": "Quotation", "disabled": 0},
            pluck="name",
            order_by="name asc",
        )
        return rows or []
