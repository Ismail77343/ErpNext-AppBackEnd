import frappe


class NotificationDocument:
    @staticmethod
    def get_display_name(doc):
        return (
            doc.get("customer_name")
            or doc.get("title")
            or doc.get("lead_name")
            or doc.get("subject")
            or doc.get("name")
        )

    @staticmethod
    def get_detail_endpoint(doctype, docname):
        mapping = {
            "Lead": {
                "method": "mobile_api.api.get_lead_details",
                "param_key": "lead_name",
            },
            "Opportunity": {
                "method": "mobile_api.api.get_opportunity_details",
                "param_key": "opportunity_name",
            },
            "Quotation": {
                "method": "mobile_api.api.get_quotation_details",
                "param_key": "quotation_name",
            },
        }
        meta = mapping.get(doctype)
        if not meta:
            return None

        return {
            "method": meta["method"],
            "param_key": meta["param_key"],
            "param_value": docname,
        }

    @staticmethod
    def get_document_link(doctype, docname):
        base_url = frappe.utils.get_url()
        return {
            "doctype": doctype,
            "docname": docname,
            "route": ["Form", doctype, docname],
            "url": f"{base_url}/app/{frappe.utils.slug(doctype)}/{docname}",
        }

    @staticmethod
    def to_workflow_action(row):
        return {
            "action": row.get("action"),
            "allowed": row.get("allowed"),
            "next_state": row.get("next_state"),
            "state": row.get("state"),
        }

    @classmethod
    def to_item(cls, todo, doc, actions):
        doctype = todo.get("reference_type")
        docname = todo.get("reference_name")
        return {
            "id": todo.get("name"),
            "notification_type": "workflow_action",
            "allocated_to": todo.get("allocated_to"),
            "doctype": doctype,
            "document_name": docname,
            "display_name": cls.get_display_name(doc),
            "workflow_state": doc.get("workflow_state"),
            "status": doc.get("status"),
            "priority": todo.get("priority"),
            "todo_status": todo.get("status"),
            "due_date": todo.get("date"),
            "modified": todo.get("modified"),
            "message": todo.get("description") or f"Workflow action pending for {doctype} {docname}",
            "detail_endpoint": cls.get_detail_endpoint(doctype, docname),
            "document_link": cls.get_document_link(doctype, docname),
            "action_count": len(actions),
            "actions": [cls.to_workflow_action(item) for item in actions],
        }
