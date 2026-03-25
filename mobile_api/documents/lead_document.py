class LeadDocument:
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
            "follow_up_summary": {
                "last_update_date": row.get("mobile_api_last_update_date"),
                "next_follow_up_date": row.get("mobile_api_next_follow_up_date"),
                "last_follow_up_report": row.get("mobile_api_last_follow_up_report"),
            },
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
            "follow_up_summary": {
                "last_update_date": doc.get("mobile_api_last_update_date"),
                "next_follow_up_date": doc.get("mobile_api_next_follow_up_date"),
                "last_follow_up_report": doc.get("mobile_api_last_follow_up_report"),
                "attachment": doc.get("mobile_api_follow_up_attachment"),
            },
            "follow_ups": [cls.to_follow_up(row) for row in (follow_ups or [])],
            "activity_log": [cls.to_activity(row) for row in (activity_log or [])],
        }
