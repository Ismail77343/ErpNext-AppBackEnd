import frappe

from mobile_api.utils.crm_follow_up_utils import FOLLOW_UP_TABLE_FIELD, sync_follow_up_summary


class CRMFollowUpRepository:
    ALLOWED_DOCTYPES = {"Lead", "Opportunity", "Quotation"}

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
    def save_document(doc):
        doc.save()
        frappe.db.commit()
