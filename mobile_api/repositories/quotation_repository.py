import frappe
from frappe.model.workflow import apply_workflow, get_transitions, get_workflow_name

from mobile_api.repositories.crm_follow_up_repository import CRMFollowUpRepository
from mobile_api.utils.access_control import MobileAccessControl


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
        "sales_person",
        "owner",
        "_assign",
        "modified",
    ]
    SALES_PERSON_FIELDS = ["sales_person"]

    @staticmethod
    def get_quotation(quotation_name):
        return MobileAccessControl.ensure_read_access(
            "Quotation",
            quotation_name,
            sales_person_fields=QuotationRepository.SALES_PERSON_FIELDS,
        )

    @classmethod
    def list_fields(cls):
        return MobileAccessControl.existing_fields("Quotation", cls.LIST_FIELDS)

    @classmethod
    def query_quotations(cls, filters=None, search=None, limit_start=None, limit_page_length=None):
        quotation_filters = filters or {}
        or_filters = []

        if search:
            like_value = f"%{search}%"
            or_filters = MobileAccessControl.search_or_filters(
                "Quotation",
                ["name", "customer_name", "party_name", "contact_mobile", "contact_email"],
                like_value,
            )

        rows = frappe.get_list(
            "Quotation",
            filters=quotation_filters,
            or_filters=or_filters or None,
            fields=cls.list_fields(),
            order_by="modified desc",
            limit_start=limit_start,
            limit_page_length=limit_page_length,
        )
        return MobileAccessControl.filter_user_related_rows(
            "Quotation",
            rows,
            sales_person_fields=cls.SALES_PERSON_FIELDS,
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
        if not doc.is_new():
            MobileAccessControl.ensure_write_access(
                "Quotation",
                doc.name,
                sales_person_fields=QuotationRepository.SALES_PERSON_FIELDS,
            )
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
