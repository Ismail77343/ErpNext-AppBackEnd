from mobile_api.documents.opportunity_document import OpportunityDocument
from mobile_api.repositories.opportunity_repository import OpportunityRepository
from mobile_api.utils.opportunity_utils import OpportunityUtils


class OpportunityService:
    WORKFLOW_SEND_KEYWORDS = ("approve", "review", "submit", "send", "forward")
    WORKFLOW_RETURN_KEYWORDS = ("reject", "return", "back", "revise", "reopen")

    @staticmethod
    def sync_party_data(doc):
        party_doc = OpportunityRepository.get_party_doc(doc.get("opportunity_from"), doc.get("party_name"))
        OpportunityUtils.sync_from_party(doc, party_doc)
        return doc

    @classmethod
    def resolve_workflow_action(cls, doc, action=None, intent=None):
        actions = OpportunityRepository.get_workflow_actions(doc)
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
    def get_opportunity_form(opportunity_name=None):
        mode = "edit" if opportunity_name else "create"
        doc = (
            OpportunityRepository.get_opportunity(opportunity_name)
            if opportunity_name
            else OpportunityRepository.new_opportunity()
        )
        OpportunityUtils.apply_defaults(doc)

        return {
            "status": "success",
            "mode": mode,
            "opportunity_name": opportunity_name,
            "default_values": {"status": doc.get("status")},
            "form_fields": OpportunityUtils.get_form_fields(doc, mode=mode),
        }

    @staticmethod
    def get_workflow_actions(opportunity_name):
        doc = OpportunityRepository.get_opportunity(opportunity_name)
        actions = OpportunityRepository.get_workflow_actions(doc)
        return {
            "status": "success",
            "opportunity_name": opportunity_name,
            "workflow_name": OpportunityRepository.get_workflow_name(),
            "action_count": len(actions),
            "actions": [OpportunityDocument.to_workflow_action(action) for action in actions],
        }

    @staticmethod
    def execute_workflow_action(opportunity_name, action):
        if not action:
            return {"status": "error", "message": "action is required"}

        doc = OpportunityRepository.get_opportunity(opportunity_name)
        updated_doc = OpportunityRepository.apply_workflow_action(doc, action)
        follow_ups = OpportunityRepository.get_follow_ups(updated_doc)
        activity_log = OpportunityRepository.get_activity_log(opportunity_name)
        actions = OpportunityRepository.get_workflow_actions(updated_doc)

        return {
            "status": "success",
            "message": f"Workflow action {action} executed successfully",
            "opportunity_name": updated_doc.name,
            "workflow": {
                "action_count": len(actions),
                "actions": [OpportunityDocument.to_workflow_action(item) for item in actions],
            },
            "data": OpportunityDocument.to_detail(updated_doc, follow_ups=follow_ups, activity_log=activity_log),
        }

    @classmethod
    def send_for_approval(cls, opportunity_name, action=None):
        doc = OpportunityRepository.get_opportunity(opportunity_name)
        resolved_action, actions = cls.resolve_workflow_action(doc, action=action, intent="send")
        if not resolved_action:
            return {
                "status": "error",
                "message": "لا يوجد Workflow Action مناسب للإرسال للموافقة",
                "available_actions": [OpportunityDocument.to_workflow_action(item) for item in actions],
            }
        return cls.execute_workflow_action(opportunity_name, resolved_action)

    @classmethod
    def return_workflow(cls, opportunity_name, action=None):
        doc = OpportunityRepository.get_opportunity(opportunity_name)
        resolved_action, actions = cls.resolve_workflow_action(doc, action=action, intent="return")
        if not resolved_action:
            return {
                "status": "error",
                "message": "لا يوجد Workflow Action مناسب للإرجاع",
                "available_actions": [OpportunityDocument.to_workflow_action(item) for item in actions],
            }
        return cls.execute_workflow_action(opportunity_name, resolved_action)

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
        if not matcher:
            return items
        return [item for item in items if matcher(item)]

    @staticmethod
    def sort_opportunities(items, sort_by=None):
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
    def get_opportunities(
        limit_start=0,
        limit_page_length=20,
        status=None,
        search=None,
        follow_up_filter=None,
        sort_by=None,
    ):
        filters = {}
        if status:
            filters["status"] = status

        rows = OpportunityRepository.query_opportunities(
            filters=filters,
            search=search,
            limit_start=None,
            limit_page_length=None,
        )
        items = [OpportunityDocument.to_list_item(row) for row in rows]
        items = OpportunityService.apply_follow_up_filter(items, follow_up_filter=follow_up_filter)
        items = OpportunityService.sort_opportunities(items, sort_by=sort_by)

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
    def get_opportunities_dashboard_summary(status=None, search=None):
        filters = {}
        if status:
            filters["status"] = status

        rows = OpportunityRepository.query_opportunities(
            filters=filters,
            search=search,
            limit_start=None,
            limit_page_length=None,
        )
        items = [OpportunityDocument.to_list_item(row) for row in rows]
        return {
            "status": "success",
            "summary": OpportunityService.build_dashboard_summary(items),
            "filters": {"status": status, "search": search},
        }

    @staticmethod
    def get_opportunity_details(opportunity_name):
        doc = OpportunityRepository.get_opportunity(opportunity_name)
        follow_ups = OpportunityRepository.get_follow_ups(doc)
        activity_log = OpportunityRepository.get_activity_log(opportunity_name)
        actions = OpportunityRepository.get_workflow_actions(doc)
        return {
            "status": "success",
            "data": OpportunityDocument.to_detail(doc, follow_ups=follow_ups, activity_log=activity_log),
            "form": OpportunityUtils.get_form_fields(doc, mode="edit"),
            "workflow": {
                "action_count": len(actions),
                "actions": [OpportunityDocument.to_workflow_action(item) for item in actions],
            },
        }

    @staticmethod
    def get_opportunity_follow_ups(opportunity_name):
        doc = OpportunityRepository.get_opportunity(opportunity_name)
        return {
            "status": "success",
            "opportunity_name": opportunity_name,
            "follow_ups": [
                OpportunityDocument.to_follow_up(row)
                for row in OpportunityRepository.get_follow_ups(doc)
            ],
        }

    @staticmethod
    def get_required_fields(opportunity_name=None, data=None, **kwargs):
        payload = OpportunityUtils.parse_payload(data=data, kwargs=kwargs)
        doc = (
            OpportunityRepository.get_opportunity(opportunity_name)
            if opportunity_name
            else OpportunityRepository.new_opportunity()
        )
        OpportunityUtils.apply_payload(doc, payload)

        required_fields = OpportunityUtils.get_required_fields(doc)
        missing_fields = OpportunityUtils.get_missing_fields(doc, required_fields)
        return {
            "status": "success",
            "doctype": "Opportunity",
            "opportunity_name": doc.name if opportunity_name else None,
            "default_values": {"status": doc.get("status")},
            "required_fields": required_fields,
            "missing_fields": missing_fields,
            "form_fields": OpportunityUtils.get_form_fields(doc, mode="edit" if opportunity_name else "create"),
        }

    @staticmethod
    def create_opportunity(data=None, **kwargs):
        payload = OpportunityUtils.parse_payload(data=data, kwargs=kwargs)
        doc = OpportunityRepository.new_opportunity()
        OpportunityUtils.apply_payload(doc, payload)
        OpportunityService.sync_party_data(doc)

        required_fields = OpportunityUtils.get_required_fields(doc)
        missing_fields = OpportunityUtils.get_missing_fields(doc, required_fields)
        if missing_fields:
            return {
                "status": "error",
                "message": "بعض الحقول الإلزامية غير موجودة",
                "missing_fields": missing_fields,
            }

        OpportunityRepository.save_opportunity(doc)
        return {
            "status": "success",
            "message": "تم إنشاء Opportunity بنجاح",
            "opportunity_name": doc.name,
            "data": OpportunityDocument.to_detail(doc),
        }

    @staticmethod
    def update_opportunity(opportunity_name, data=None, **kwargs):
        payload = OpportunityUtils.parse_payload(data=data, kwargs=kwargs)
        doc = OpportunityRepository.get_opportunity(opportunity_name)
        OpportunityUtils.apply_payload(doc, payload)
        OpportunityService.sync_party_data(doc)

        required_fields = OpportunityUtils.get_required_fields(doc)
        missing_fields = OpportunityUtils.get_missing_fields(doc, required_fields)
        if missing_fields:
            return {
                "status": "error",
                "message": "بعض الحقول الإلزامية غير موجودة بعد التعديل",
                "missing_fields": missing_fields,
            }

        OpportunityRepository.save_opportunity(doc)
        return {
            "status": "success",
            "message": "تم تحديث Opportunity بنجاح",
            "opportunity_name": doc.name,
            "data": OpportunityDocument.to_detail(doc),
        }

    @staticmethod
    def add_follow_up(opportunity_name, follow_up_date, expected_result_date, details, attachment=None):
        if not OpportunityRepository.opportunity_exists(opportunity_name):
            return {"status": "error", "message": f"Opportunity {opportunity_name} غير موجود"}

        if not follow_up_date or not expected_result_date or not details:
            return {
                "status": "error",
                "message": "الحقول المطلوبة هي: follow_up_date, expected_result_date, details",
            }

        doc = OpportunityRepository.get_opportunity(opportunity_name)
        OpportunityRepository.add_follow_up(
            doc=doc,
            follow_up_date=follow_up_date,
            expected_result_date=expected_result_date,
            details=details,
            attachment=attachment,
        )
        OpportunityRepository.save_opportunity(doc)

        return {
            "status": "success",
            "message": "تمت إضافة متابعة الفرصة بنجاح",
            "opportunity_name": opportunity_name,
            "follow_ups": [
                OpportunityDocument.to_follow_up(row)
                for row in OpportunityRepository.get_follow_ups(doc)
            ],
            "last_update_date": doc.get("mobile_api_last_update_date"),
            "next_follow_up_date": doc.get("mobile_api_next_follow_up_date"),
            "last_follow_up_report": doc.get("mobile_api_last_follow_up_report"),
            "data": OpportunityDocument.to_detail(
                doc,
                follow_ups=OpportunityRepository.get_follow_ups(doc),
                activity_log=OpportunityRepository.get_activity_log(opportunity_name),
            ),
        }
