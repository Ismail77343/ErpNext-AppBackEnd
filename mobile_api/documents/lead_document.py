import frappe


class LeadDocument:
    @staticmethod
    def _getdate(value):
        if not value:
            return None

        try:
            return frappe.utils.getdate(value)
        except Exception:
            return None

    @classmethod
    def follow_up_meta(cls, source):
        today = frappe.utils.getdate()
        next_follow_up_date = cls._getdate(source.get("mobile_api_next_follow_up_date"))
        first_day_month = frappe.utils.get_first_day(today)
        last_day_month = frappe.utils.get_last_day(today)
        week_end = frappe.utils.add_days(today, 6 - today.weekday())

        has_follow_up = bool(
            source.get("mobile_api_last_update_date")
            or source.get("mobile_api_next_follow_up_date")
            or source.get("mobile_api_last_follow_up_report")
        )
        never_contacted = not has_follow_up
        is_due_today = bool(next_follow_up_date and next_follow_up_date == today)
        is_overdue = bool(next_follow_up_date and next_follow_up_date < today)
        is_due_this_week = bool(next_follow_up_date and today <= next_follow_up_date <= week_end)
        is_due_this_month = bool(next_follow_up_date and first_day_month <= next_follow_up_date <= last_day_month)

        return {
            "last_update_date": source.get("mobile_api_last_update_date"),
            "next_follow_up_date": source.get("mobile_api_next_follow_up_date"),
            "last_follow_up_report": source.get("mobile_api_last_follow_up_report"),
            "attachment": source.get("mobile_api_follow_up_attachment"),
            "has_follow_up": has_follow_up,
            "is_overdue": is_overdue,
            "is_due_today": is_due_today,
            "is_due_this_week": is_due_this_week,
            "is_due_this_month": is_due_this_month,
            "never_contacted": never_contacted,
        }

    @staticmethod
    def full_name(doc):
        return (
            doc.get("lead_name")
            or " ".join(
                part for part in [
                    doc.get("first_name"),
                    doc.get("middle_name"),
                    doc.get("last_name"),
                ]
                if part
            ).strip()
            or doc.get("company_name")
            or doc.get("name")
        )

    @classmethod
    def to_list_item(cls, row):
        follow_up_meta = cls.follow_up_meta(row)
        return {
            "id": row.get("name"),
            "doctype": "Lead",
            "display_name": row.get("lead_name") or row.get("company_name") or row.get("name"),
            "company_name": row.get("company_name"),
            "status": row.get("status"),
            "source": row.get("source"),
            "owner": row.get("lead_owner"),
            "contact": {
                "email": row.get("email_id"),
                "mobile": row.get("mobile_no"),
            },
            "last_update_date": follow_up_meta["last_update_date"],
            "next_follow_up_date": follow_up_meta["next_follow_up_date"],
            "last_follow_up_report": follow_up_meta["last_follow_up_report"],
            "has_follow_up": follow_up_meta["has_follow_up"],
            "is_overdue": follow_up_meta["is_overdue"],
            "is_due_today": follow_up_meta["is_due_today"],
            "is_due_this_week": follow_up_meta["is_due_this_week"],
            "is_due_this_month": follow_up_meta["is_due_this_month"],
            "never_contacted": follow_up_meta["never_contacted"],
            "follow_up_summary": follow_up_meta,
            "modified": row.get("modified"),
        }

    @staticmethod
    def to_follow_up(row):
        return {
            "id": row.get("name"),
            "follow_up_date": row.get("follow_up_date"),
            "expected_result_date": row.get("expected_result_date"),
            "details": row.get("details"),
            "attachment": row.get("attachment"),
            "registered_on": row.get("registered_on"),
        }

    @staticmethod
    def to_activity(row):
        return {
            "id": row.get("name"),
            "comment_by": row.get("comment_by"),
            "creation": row.get("creation"),
            "content": row.get("content"),
        }

    @classmethod
    def to_detail(cls, doc, follow_ups=None, activity_log=None):
        follow_up_meta = cls.follow_up_meta(doc)
        return {
            "id": doc.name,
            "doctype": "Lead",
            "identity": {
                "name": doc.name,
                "display_name": cls.full_name(doc),
                "lead_name": doc.get("lead_name"),
                "first_name": doc.get("first_name"),
                "middle_name": doc.get("middle_name"),
                "last_name": doc.get("last_name"),
                "company_name": doc.get("company_name"),
            },
            "status": {
                "current": doc.get("status"),
                "source": doc.get("source"),
                "owner": doc.get("lead_owner"),
            },
            "contact": {
                "email": doc.get("email_id"),
                "mobile": doc.get("mobile_no"),
                "whatsapp": doc.get("whatsapp_no"),
                "phone": doc.get("phone"),
            },
            "address": {
                "city": doc.get("city"),
                "country": doc.get("country"),
                "territory": doc.get("territory"),
            },
            "notes": doc.get("notes"),
            "last_update_date": follow_up_meta["last_update_date"],
            "next_follow_up_date": follow_up_meta["next_follow_up_date"],
            "last_follow_up_report": follow_up_meta["last_follow_up_report"],
            "has_follow_up": follow_up_meta["has_follow_up"],
            "is_overdue": follow_up_meta["is_overdue"],
            "is_due_today": follow_up_meta["is_due_today"],
            "is_due_this_week": follow_up_meta["is_due_this_week"],
            "is_due_this_month": follow_up_meta["is_due_this_month"],
            "never_contacted": follow_up_meta["never_contacted"],
            "follow_up_summary": follow_up_meta,
            "follow_ups": [cls.to_follow_up(row) for row in (follow_ups or [])],
            "activity_log": [cls.to_activity(row) for row in (activity_log or [])],
        }
