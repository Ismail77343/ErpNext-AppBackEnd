from urllib.parse import urlencode

import frappe


class QuotationDocument:
    @classmethod
    def build_content(cls, source):
        parts = [cls.display_name(source)]

        if source.get("workflow_state"):
            parts.append(f"Workflow: {source.get('workflow_state')}")
        elif source.get("status"):
            parts.append(f"Status: {source.get('status')}")

        if source.get("grand_total"):
            parts.append(f"Total: {source.get('grand_total')} {source.get('currency') or ''}".strip())

        if source.get("mobile_api_next_follow_up_date"):
            parts.append(f"Next Follow Up: {source.get('mobile_api_next_follow_up_date')}")

        return " | ".join(part for part in parts if part)

    @staticmethod
    def display_name(source):
        return (
            source.get("customer_name")
            or source.get("party_name")
            or source.get("name")
        )

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

        return {
            "last_update_date": source.get("mobile_api_last_update_date"),
            "next_follow_up_date": source.get("mobile_api_next_follow_up_date"),
            "last_follow_up_report": source.get("mobile_api_last_follow_up_report"),
            "attachment": source.get("mobile_api_follow_up_attachment"),
            "has_follow_up": has_follow_up,
            "is_overdue": bool(next_follow_up_date and next_follow_up_date < today),
            "is_due_today": bool(next_follow_up_date and next_follow_up_date == today),
            "is_due_this_week": bool(next_follow_up_date and today <= next_follow_up_date <= week_end),
            "is_due_this_month": bool(next_follow_up_date and first_day_month <= next_follow_up_date <= last_day_month),
            "never_contacted": never_contacted,
        }

    @staticmethod
    def to_workflow_action(row):
        return {
            "action": row.get("action"),
            "allowed": row.get("allowed"),
            "next_state": row.get("next_state"),
            "state": row.get("state"),
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

    @staticmethod
    def to_item(row):
        return {
            "item_code": row.get("item_code"),
            "item_name": row.get("item_name"),
            "description": row.get("description"),
            "qty": row.get("qty"),
            "uom": row.get("uom"),
            "rate": row.get("rate"),
            "amount": row.get("amount"),
        }

    @classmethod
    def build_print_data(cls, doc, print_format=None, available_print_formats=None):
        default_print_format = print_format or frappe.get_meta("Quotation").default_print_format or "Standard"
        available = list(available_print_formats or [])
        if default_print_format not in available:
            available.insert(0, default_print_format)

        base_url = frappe.utils.get_url()
        common_params = {
            "doctype": "Quotation",
            "name": doc.name,
            "format": default_print_format,
            "no_letterhead": 0,
        }
        print_url = f"{base_url}/printview?{urlencode({**common_params, 'trigger_print': 0})}"
        pdf_url = f"{base_url}/api/method/frappe.utils.print_format.download_pdf?{urlencode(common_params)}"

        return {
            "default_print_format": default_print_format,
            "available_print_formats": available,
            "print_url": print_url,
            "pdf_url": pdf_url,
        }

    @classmethod
    def to_list_item(cls, row):
        follow_up_meta = cls.follow_up_meta(row)
        return {
            "id": row.get("name"),
            "doctype": "Quotation",
            "display_name": cls.display_name(row),
            "content": cls.build_content(row),
            "customer_name": row.get("customer_name"),
            "party_name": row.get("party_name"),
            "status": row.get("status"),
            "workflow_state": row.get("workflow_state"),
            "opportunity": row.get("opportunity"),
            "order_type": row.get("order_type"),
            "contact": {
                "email": row.get("contact_email"),
                "mobile": row.get("contact_mobile"),
            },
            "transaction_date": row.get("transaction_date"),
            "valid_till": row.get("valid_till"),
            "currency": row.get("currency"),
            "grand_total": row.get("grand_total"),
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

    @classmethod
    def to_detail(cls, doc, follow_ups=None, activity_log=None, available_print_formats=None, print_format=None):
        follow_up_meta = cls.follow_up_meta(doc)
        return {
            "id": doc.name,
            "doctype": "Quotation",
            "content": cls.build_content(doc),
            "identity": {
                "name": doc.name,
                "display_name": cls.display_name(doc),
                "customer_name": doc.get("customer_name"),
                "party_name": doc.get("party_name"),
                "opportunity": doc.get("opportunity"),
                "order_type": doc.get("order_type"),
            },
            "status": {
                "current": doc.get("status"),
                "workflow_state": doc.get("workflow_state"),
                "quotation_to": doc.get("quotation_to"),
                "owner": doc.get("owner"),
            },
            "dates": {
                "transaction_date": doc.get("transaction_date"),
                "valid_till": doc.get("valid_till"),
            },
            "value": {
                "currency": doc.get("currency"),
                "grand_total": doc.get("grand_total"),
                "net_total": doc.get("net_total"),
                "total_qty": doc.get("total_qty"),
            },
            "contact": {
                "contact_person": doc.get("contact_person"),
                "email": doc.get("contact_email"),
                "mobile": doc.get("contact_mobile"),
                "phone": doc.get("contact_phone"),
            },
            "print": cls.build_print_data(
                doc,
                print_format=print_format,
                available_print_formats=available_print_formats,
            ),
            "items": [cls.to_item(row) for row in (doc.get("items") or [])],
            "terms_and_conditions": doc.get("tc_name"),
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
