import frappe

from mobile_api.repositories.crm_follow_up_repository import CRMFollowUpRepository


class LeadRepository:
    LIST_FIELDS = [
        "name",
        "lead_name",
        "company_name",
        "status",
        "source",
        "lead_owner",
        "email_id",
        "mobile_no",
        "mobile_api_last_update_date",
        "mobile_api_next_follow_up_date",
        "mobile_api_last_follow_up_report",
        "modified",
    ]

    @staticmethod
    def new_lead():
        return frappe.new_doc("Lead")

    @staticmethod
    def get_lead(lead_name):
        return frappe.get_doc("Lead", lead_name)

    @classmethod
    def get_leads(cls, filters=None, search=None, limit_start=0, limit_page_length=20):
        lead_filters = filters or {}

        if search:
            lead_filters["name"] = ["like", f"%{search}%"]

        return frappe.get_list(
            "Lead",
            filters=lead_filters,
            fields=cls.LIST_FIELDS,
            order_by="modified desc",
            limit_start=limit_start,
            limit_page_length=limit_page_length,
        )

    @staticmethod
    def lead_exists(lead_name):
        return bool(frappe.db.exists("Lead", lead_name))

    @staticmethod
    def get_follow_ups(doc):
        return CRMFollowUpRepository.get_follow_ups(doc)

    @staticmethod
    def get_activity_log(lead_name):
        return CRMFollowUpRepository.get_activity_log("Lead", lead_name)

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
    def save_lead(doc):
        doc.save()
        frappe.db.commit()
        return doc
