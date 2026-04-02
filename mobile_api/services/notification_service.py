import frappe

from mobile_api.documents.notification_document import NotificationDocument
from mobile_api.repositories.notification_repository import NotificationRepository


class NotificationService:
    @staticmethod
    def get_workflow_notifications(limit_start=0, limit_page_length=20):
        user = frappe.session.user
        if not user or user == "Guest":
            return {"status": "error", "message": "User is not authenticated"}

        todos = NotificationRepository.get_open_workflow_todos(user, limit_start=None, limit_page_length=None)
        items = []

        for todo in todos:
            doctype = todo.get("reference_type")
            docname = todo.get("reference_name")

            if not NotificationRepository.has_workflow(doctype):
                continue

            doc = NotificationRepository.get_reference_doc(doctype, docname)
            if not doc:
                continue

            actions = NotificationRepository.get_workflow_actions(doc)
            if not actions:
                continue

            items.append(NotificationDocument.to_item(todo, doc, actions))

        start = int(limit_start or 0)
        page_length = int(limit_page_length or 20)
        paginated = items[start:start + page_length]

        return {
            "status": "success",
            "user": user,
            "data": paginated,
            "total_count": len(items),
            "unread_count": len(items),
            "limit_start": start,
            "limit_page_length": page_length,
        }

    @staticmethod
    def get_workflow_notifications_summary():
        result = NotificationService.get_workflow_notifications(limit_start=0, limit_page_length=1000)
        if result.get("status") != "success":
            return result

        data = result.get("data") or []
        summary = {
            "total_count": result.get("total_count", 0),
            "unread_count": result.get("unread_count", 0),
            "opportunity_count": sum(1 for item in data if item.get("doctype") == "Opportunity"),
            "quotation_count": sum(1 for item in data if item.get("doctype") == "Quotation"),
            "lead_count": sum(1 for item in data if item.get("doctype") == "Lead"),
            "other_count": sum(
                1
                for item in data
                if item.get("doctype") not in {"Opportunity", "Quotation", "Lead"}
            ),
        }

        return {
            "status": "success",
            "user": result.get("user"),
            "summary": summary,
        }
