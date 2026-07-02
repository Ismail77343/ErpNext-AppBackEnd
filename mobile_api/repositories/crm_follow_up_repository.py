import frappe

from mobile_api.utils.crm_follow_up_utils import FOLLOW_UP_TABLE_FIELD, sync_follow_up_summary


class CRMFollowUpRepository:
    ALLOWED_DOCTYPES = {"Lead", "Opportunity", "Quotation", "Sales Invoice"}

    @classmethod
    def validate_doctype(cls, doctype):
        if doctype not in cls.ALLOWED_DOCTYPES:
            frappe.throw(f"DocType غير مدعوم: {doctype}")

    @classmethod
    def get_document(cls, doctype, docname):
        cls.validate_doctype(doctype)
        return frappe.get_doc(doctype, docname)

    @classmethod
    def document_exists(cls, doctype, docname):
        cls.validate_doctype(doctype)
        return bool(frappe.db.exists(doctype, docname))

    @staticmethod
    def get_follow_ups(doc):
        rows = doc.get(FOLLOW_UP_TABLE_FIELD) or []
        return [row.as_dict() for row in rows]

    @staticmethod
    def get_activity_log(doctype, docname):
        return frappe.get_list(
            "Comment",
            filters={"reference_doctype": doctype, "reference_name": docname},
            fields=["name", "comment_by", "creation", "content"],
            order_by="creation desc",
        )

    @staticmethod
    def get_follow_up_user():
        user = frappe.session.user
        if not user or user == "Guest":
            return None

        return frappe.db.get_value("User", user, "full_name") or user

    @staticmethod
    def append_follow_up(doc, follow_up_date, expected_result_date, details, attachment=None):
        if not hasattr(doc, FOLLOW_UP_TABLE_FIELD):
            frappe.throw("حقول المتابعة غير موجودة بعد. نفذ bench migrate أولاً.")

        doc.append(
            FOLLOW_UP_TABLE_FIELD,
            {
                "follow_up_date": follow_up_date,
                "expected_result_date": expected_result_date,
                "details": details,
                "attachment": attachment or "",
                "followed_by": CRMFollowUpRepository.get_follow_up_user(),
                "registered_on": frappe.utils.now(),
            },
        )
        sync_follow_up_summary(doc)

    @staticmethod
    def insert_submitted_sales_invoice_follow_up(
        doc, follow_up_date, expected_result_date, details, attachment=None
    ):
        if doc.doctype != "Sales Invoice" or doc.docstatus != 1:
            frappe.throw("هذه العملية مخصصة لفواتير المبيعات المقدمة فقط.")

        doc.check_permission("write")

        next_idx = (frappe.db.count("Mobile CRM Follow Up", {"parent": doc.name}) or 0) + 1
        row = frappe.get_doc(
            {
                "doctype": "Mobile CRM Follow Up",
                "parent": doc.name,
                "parenttype": doc.doctype,
                "parentfield": FOLLOW_UP_TABLE_FIELD,
                "idx": next_idx,
                "follow_up_date": follow_up_date,
                "expected_result_date": expected_result_date,
                "details": details,
                "attachment": attachment or "",
                "followed_by": CRMFollowUpRepository.get_follow_up_user(),
                "registered_on": frappe.utils.now(),
            }
        )
        row.insert(ignore_permissions=True)

        frappe.db.set_value(
            doc.doctype,
            doc.name,
            {
                "mobile_api_last_update_date": follow_up_date,
                "mobile_api_next_follow_up_date": expected_result_date,
                "mobile_api_last_follow_up_report": details,
                "mobile_api_follow_up_attachment": attachment or "",
                "last_follow": details,
            },
            update_modified=False,
        )
        frappe.db.commit()
        return row

    @staticmethod
    def save_document(doc):
        doc.save()
        frappe.db.commit()
