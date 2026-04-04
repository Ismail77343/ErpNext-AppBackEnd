import frappe


class OpportunityDocument:
    @classmethod
    def build_content(cls, source):
        parts = [cls.display_name(source)]

        if source.get("workflow_state"):
            parts.append(f"Workflow: {source.get('workflow_state')}")
        elif source.get("status"):
            parts.append(f"Status: {source.get('status')}")

        if source.get("opportunity_amount"):
            parts.append(f"Amount: {source.get('opportunity_amount')}")

        if source.get("mobile_api_next_follow_up_date"):
            parts.append(f"Next Follow Up: {source.get('mobile_api_next_follow_up_date')}")

        return " | ".join(part for part in parts if part)

    @staticmethod
    def to_workflow_action(row):
        return {
            "action": row.get("action"),
            "allowed": row.get("allowed"),
            "next_state": row.get("next_state"),
            "state": row.get("state"),
        }

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
    def display_name(source):
        return (
            source.get("customer_name")
            or source.get("title")
            or source.get("party_name")
            or source.get("name")
        )

    @classmethod
    def to_list_item(cls, row):
        follow_up_meta = cls.follow_up_meta(row)
        return {
            "id": row.get("name"),
            "doctype": "Opportunity",
            "display_name": cls.display_name(row),
            "content": cls.build_content(row),
            "party_name": row.get("party_name"),
            "customer_name": row.get("customer_name"),
            "status": row.get("status"),
            "workflow_state": row.get("workflow_state"),
            "opportunity_from": row.get("opportunity_from"),
            "opportunity_owner": row.get("opportunity_owner"),
            "contact": {
                "email": row.get("contact_email"),
                "mobile": row.get("contact_mobile"),
                "phone": row.get("phone"),
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
            "followed_by": row.get("followed_by"),
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
            "doctype": "Opportunity",
            "content": doc.get("content") or cls.build_content(doc),
            "identity": {
                "name": doc.name,
                "display_name": cls.display_name(doc),
                "party_name": doc.get("party_name"),
                "customer_name": doc.get("customer_name"),
                "title": doc.get("title"),
            },
            "status": {
                "current": doc.get("status"),
                "workflow_state": doc.get("workflow_state"),
                "opportunity_from": doc.get("opportunity_from"),
                "owner": doc.get("opportunity_owner"),
                "source": doc.get("source"),
                "sales_stage": doc.get("sales_stage"),
            },
            "value": {
                "currency": doc.get("currency"),
                "opportunity_amount": doc.get("opportunity_amount"),
                "expected_closing": doc.get("expected_closing"),
                "probability": doc.get("probability"),
            },
            "contact": {
                "contact_person": doc.get("contact_person"),
                "email": doc.get("contact_email"),
                "mobile": doc.get("contact_mobile"),
                "whatsapp": doc.get("whatsapp"),
                "phone": doc.get("phone"),
            },
            "address": {
                "address_line1": doc.get("address_line1"),
                "address_line2": doc.get("address_line2"),
                "address_display": doc.get("address_display"),
                "city": doc.get("city"),
                "state": doc.get("state"),
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
