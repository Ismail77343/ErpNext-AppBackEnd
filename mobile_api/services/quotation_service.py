from mobile_api.documents.quotation_document import QuotationDocument
from mobile_api.repositories.quotation_repository import QuotationRepository


class QuotationService:
    WORKFLOW_SEND_KEYWORDS = ("approve", "review", "submit", "send", "forward")
    WORKFLOW_RETURN_KEYWORDS = ("reject", "return", "back", "revise", "reopen")

    @classmethod
    def resolve_workflow_action(cls, doc, action=None, intent=None):
        actions = QuotationRepository.get_workflow_actions(doc)
        if not actions:
            return None, []

        if action:
            normalized = action.strip().lower()
            for item in actions:
                if (item.get("action") or "").strip().lower() == normalized:
                    return item.get("action"), actions

        keywords = cls.WORKFLOW_SEND_KEYWORDS if intent == "send" else cls.WORKFLOW_RETURN_KEYWORDS
        for item in actions:
            action_name = (item.get("action") or "").strip().lower()
            if any(keyword in action_name for keyword in keywords):
                return item.get("action"), actions

        if intent == "send":
            return actions[0].get("action"), actions
        if intent == "return":
            return actions[-1].get("action"), actions

        return None, actions

    @staticmethod
    def apply_follow_up_filter(items, follow_up_filter=None):
        if not follow_up_filter:
            return items

        filter_map = {
            "overdue": lambda item: item["is_overdue"],
            "today": lambda item: item["is_due_today"],
            "this_week": lambda item: item["is_due_this_week"],
            "month": lambda item: item["is_due_this_month"],
            "never_contacted": lambda item: item["never_contacted"],
            "upcoming": lambda item: (
                item["next_follow_up_date"]
                and not item["is_overdue"]
                and not item["is_due_today"]
            ),
        }
        matcher = filter_map.get(follow_up_filter)
        return [item for item in items if matcher(item)] if matcher else items

    @staticmethod
    def sort_quotations(items, sort_by=None):
        if sort_by == "next_follow_up_date_asc":
            return sorted(
                items,
                key=lambda item: (
                    item["next_follow_up_date"] is None,
                    item["next_follow_up_date"] or "9999-12-31",
                    item["modified"],
                ),
            )
        if sort_by == "overdue_first":
            return sorted(
                items,
                key=lambda item: (
                    not item["is_overdue"],
                    item["next_follow_up_date"] or "9999-12-31",
                    item["modified"],
                ),
            )
        if sort_by == "never_contacted_first":
            return sorted(
                items,
                key=lambda item: (
                    not item["never_contacted"],
                    item["next_follow_up_date"] or "9999-12-31",
                    item["modified"],
                ),
            )
        return items

    @staticmethod
    def build_dashboard_summary(items):
        return {
            "overdue_count": sum(1 for item in items if item["is_overdue"]),
            "today_count": sum(1 for item in items if item["is_due_today"]),
            "this_week_count": sum(1 for item in items if item["is_due_this_week"]),
            "month_count": sum(1 for item in items if item["is_due_this_month"]),
            "never_contacted_count": sum(1 for item in items if item["never_contacted"]),
            "upcoming_count": sum(
                1
                for item in items
                if item["next_follow_up_date"] and not item["is_overdue"] and not item["is_due_today"]
            ),
        }

    @staticmethod
    def get_quotations(limit_start=0, limit_page_length=20, status=None, search=None, follow_up_filter=None, sort_by=None):
        filters = {}
        if status:
            filters["status"] = status

        rows = QuotationRepository.query_quotations(
            filters=filters,
            search=search,
            limit_start=None,
            limit_page_length=None,
        )
        items = [QuotationDocument.to_list_item(row) for row in rows]
        items = QuotationService.apply_follow_up_filter(items, follow_up_filter=follow_up_filter)
        items = QuotationService.sort_quotations(items, sort_by=sort_by)

        start = int(limit_start or 0)
        page_length = int(limit_page_length or 20)
        paginated = items[start:start + page_length]

        return {
            "status": "success",
            "data": paginated,
            "total_count": len(items),
            "limit_start": start,
            "limit_page_length": page_length,
            "filters": {
                "status": status,
                "search": search,
                "follow_up_filter": follow_up_filter,
                "sort_by": sort_by,
            },
        }

    @staticmethod
    def get_quotations_dashboard_summary(status=None, search=None):
        filters = {}
        if status:
            filters["status"] = status

        rows = QuotationRepository.query_quotations(
            filters=filters,
            search=search,
            limit_start=None,
            limit_page_length=None,
        )
        items = [QuotationDocument.to_list_item(row) for row in rows]
        return {
            "status": "success",
            "summary": QuotationService.build_dashboard_summary(items),
            "filters": {"status": status, "search": search},
        }

    @staticmethod
    def get_quotation_details(quotation_name, print_format=None):
        doc = QuotationRepository.get_quotation(quotation_name)
        follow_ups = QuotationRepository.get_follow_ups(doc)
        activity_log = QuotationRepository.get_activity_log(quotation_name)
        actions = QuotationRepository.get_workflow_actions(doc)
        print_formats = QuotationRepository.get_print_formats()

        return {
            "status": "success",
            "data": QuotationDocument.to_detail(
                doc,
                follow_ups=follow_ups,
                activity_log=activity_log,
                available_print_formats=print_formats,
                print_format=print_format,
            ),
            "workflow": {
                "action_count": len(actions),
                "actions": [QuotationDocument.to_workflow_action(item) for item in actions],
            },
        }

    @staticmethod
    def get_quotation_print_data(quotation_name, print_format=None):
        doc = QuotationRepository.get_quotation(quotation_name)
        print_formats = QuotationRepository.get_print_formats()
        return {
            "status": "success",
            "quotation_name": quotation_name,
            "print": QuotationDocument.build_print_data(
                doc,
                print_format=print_format,
                available_print_formats=print_formats,
            ),
        }

    @staticmethod
    def get_quotation_follow_ups(quotation_name):
        doc = QuotationRepository.get_quotation(quotation_name)
        return {
            "status": "success",
            "quotation_name": quotation_name,
            "follow_ups": [
                QuotationDocument.to_follow_up(row)
                for row in QuotationRepository.get_follow_ups(doc)
            ],
        }

    @staticmethod
    def add_follow_up(quotation_name, follow_up_date, expected_result_date, details, attachment=None):
        if not QuotationRepository.quotation_exists(quotation_name):
            return {"status": "error", "message": f"Quotation {quotation_name} غير موجود"}

        if not follow_up_date or not expected_result_date or not details:
            return {
                "status": "error",
                "message": "الحقول المطلوبة هي: follow_up_date, expected_result_date, details",
            }

        doc = QuotationRepository.get_quotation(quotation_name)
        QuotationRepository.add_follow_up(
            doc=doc,
            follow_up_date=follow_up_date,
            expected_result_date=expected_result_date,
            details=details,
            attachment=attachment,
        )
        QuotationRepository.save_quotation(doc)

        return {
            "status": "success",
            "message": "تمت إضافة متابعة عرض السعر بنجاح",
            "quotation_name": quotation_name,
            "data": QuotationDocument.to_detail(
                doc,
                follow_ups=QuotationRepository.get_follow_ups(doc),
                activity_log=QuotationRepository.get_activity_log(quotation_name),
                available_print_formats=QuotationRepository.get_print_formats(),
            ),
        }

    @staticmethod
    def get_workflow_actions(quotation_name):
        doc = QuotationRepository.get_quotation(quotation_name)
        actions = QuotationRepository.get_workflow_actions(doc)
        return {
            "status": "success",
            "quotation_name": quotation_name,
            "workflow_name": QuotationRepository.get_workflow_name(),
            "action_count": len(actions),
            "actions": [QuotationDocument.to_workflow_action(action) for action in actions],
        }

    @staticmethod
    def execute_workflow_action(quotation_name, action):
        if not action:
            return {"status": "error", "message": "action is required"}

        doc = QuotationRepository.get_quotation(quotation_name)
        updated_doc = QuotationRepository.apply_workflow_action(doc, action)
        follow_ups = QuotationRepository.get_follow_ups(updated_doc)
        activity_log = QuotationRepository.get_activity_log(quotation_name)
        actions = QuotationRepository.get_workflow_actions(updated_doc)

        return {
            "status": "success",
            "message": f"Workflow action {action} executed successfully",
            "quotation_name": updated_doc.name,
            "workflow": {
                "action_count": len(actions),
                "actions": [QuotationDocument.to_workflow_action(item) for item in actions],
            },
            "data": QuotationDocument.to_detail(
                updated_doc,
                follow_ups=follow_ups,
                activity_log=activity_log,
                available_print_formats=QuotationRepository.get_print_formats(),
            ),
        }

    @classmethod
    def send_for_approval(cls, quotation_name, action=None):
        doc = QuotationRepository.get_quotation(quotation_name)
        resolved_action, actions = cls.resolve_workflow_action(doc, action=action, intent="send")
        if not resolved_action:
            return {
                "status": "error",
                "message": "لا يوجد Workflow Action مناسب للإرسال للموافقة",
                "available_actions": [QuotationDocument.to_workflow_action(item) for item in actions],
            }
        return cls.execute_workflow_action(quotation_name, resolved_action)

    @classmethod
    def return_workflow(cls, quotation_name, action=None):
        doc = QuotationRepository.get_quotation(quotation_name)
        resolved_action, actions = cls.resolve_workflow_action(doc, action=action, intent="return")
        if not resolved_action:
            return {
                "status": "error",
                "message": "لا يوجد Workflow Action مناسب للإرجاع",
                "available_actions": [QuotationDocument.to_workflow_action(item) for item in actions],
            }
        return cls.execute_workflow_action(quotation_name, resolved_action)
