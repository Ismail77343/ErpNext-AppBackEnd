import frappe
from frappe.model.workflow import apply_workflow, get_transitions, get_workflow_name

from mobile_api.repositories.crm_follow_up_repository import CRMFollowUpRepository
from mobile_api.utils.access_control import MobileAccessControl


class OpportunityRepository:
    LIST_FIELDS = [
        "name",
        "title",
        "party_name",
        "customer_name",
        "status",
        "workflow_state",
        "opportunity_from",
        "opportunity_owner",
        "source",
        "contact_email",
        "contact_mobile",
        "phone",
        "currency",
        "opportunity_amount",
        "expected_closing",
        "mobile_api_last_update_date",
        "mobile_api_next_follow_up_date",
        "mobile_api_last_follow_up_report",
        "sales_person",
        "owner",
        "_assign",
        "modified",
    ]
    USER_FIELDS = ["opportunity_owner"]
    SALES_PERSON_FIELDS = ["sales_person"]

    @staticmethod
    def new_opportunity():
        return frappe.new_doc("Opportunity")

    @staticmethod
    def get_opportunity(opportunity_name):
        return MobileAccessControl.ensure_read_access(
            "Opportunity",
            opportunity_name,
            user_fields=OpportunityRepository.USER_FIELDS,
            sales_person_fields=OpportunityRepository.SALES_PERSON_FIELDS,
        )

    @classmethod
    def list_fields(cls):
        return MobileAccessControl.existing_fields("Opportunity", cls.LIST_FIELDS)

    @staticmethod
    def get_party_doc(party_type, party_name):
        if not party_type or not party_name:
            return None
        if party_type not in {"Lead", "Customer"}:
            return None
        if not frappe.db.exists(party_type, party_name):
            return None
        return frappe.get_doc(party_type, party_name)

    @classmethod
    def query_opportunities(cls, filters=None, search=None, limit_start=None, limit_page_length=None):
        opportunity_filters = filters or {}
        or_filters = []

        if search:
            like_value = f"%{search}%"
            or_filters = MobileAccessControl.search_or_filters(
                "Opportunity",
                ["name", "title", "party_name", "customer_name", "contact_mobile", "contact_email"],
                like_value,
            )

        rows = frappe.get_list(
            "Opportunity",
            filters=opportunity_filters,
            or_filters=or_filters or None,
            fields=cls.list_fields(),
            order_by="modified desc",
            limit_start=limit_start,
            limit_page_length=limit_page_length,
        )
        return MobileAccessControl.filter_user_related_rows(
            "Opportunity",
            rows,
            user_fields=cls.USER_FIELDS,
            sales_person_fields=cls.SALES_PERSON_FIELDS,
        )

    @classmethod
    def get_opportunities(cls, filters=None, search=None, limit_start=0, limit_page_length=20):
        return cls.query_opportunities(
            filters=filters,
            search=search,
            limit_start=limit_start,
            limit_page_length=limit_page_length,
        )

    @staticmethod
    def opportunity_exists(opportunity_name):
        return bool(frappe.db.exists("Opportunity", opportunity_name))

    @staticmethod
    def get_follow_ups(doc):
        return CRMFollowUpRepository.get_follow_ups(doc)

    @staticmethod
    def get_activity_log(opportunity_name):
        return CRMFollowUpRepository.get_activity_log("Opportunity", opportunity_name)

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
    def save_opportunity(doc):
        if not doc.is_new():
            MobileAccessControl.ensure_write_access(
                "Opportunity",
                doc.name,
                user_fields=OpportunityRepository.USER_FIELDS,
                sales_person_fields=OpportunityRepository.SALES_PERSON_FIELDS,
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
        return get_workflow_name("Opportunity")

    @staticmethod
    def apply_workflow_action(doc, action):
        updated_doc = apply_workflow(doc.as_dict(), action)
        frappe.db.commit()
        return updated_doc
