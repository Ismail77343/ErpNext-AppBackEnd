from mobile_api.repositories.lead_repository import LeadRepository
from mobile_api.documents.lead_document import LeadDocument
from mobile_api.utils.lead_utils import LeadUtils


class LeadService:
    @staticmethod
    def get_leads(limit_start=0, limit_page_length=20, status=None, search=None):
        filters = {}
        if status:
            filters["status"] = status

        leads = LeadRepository.get_leads(
            filters=filters,
            search=search,
            limit_start=int(limit_start or 0),
            limit_page_length=int(limit_page_length or 20),
        )

        return {
            "status": "success",
            "data": [LeadDocument.to_list_item(row) for row in leads],
            "limit_start": int(limit_start or 0),
            "limit_page_length": int(limit_page_length or 20),
            "filters": {
                "status": status,
                "search": search,
            },
        }

    @staticmethod
    def get_lead_details(lead_name):
        doc = LeadRepository.get_lead(lead_name)
        follow_ups = LeadRepository.get_follow_ups(doc)
        activity_log = LeadRepository.get_activity_log(lead_name)
        return {
            "status": "success",
            "data": LeadDocument.to_detail(doc, follow_ups=follow_ups, activity_log=activity_log),
        }

    @staticmethod
    def get_lead_follow_ups(lead_name):
        doc = LeadRepository.get_lead(lead_name)
        return {
            "status": "success",
            "lead_name": lead_name,
            "follow_ups": [LeadDocument.to_follow_up(row) for row in LeadRepository.get_follow_ups(doc)],
        }

    @staticmethod
    def get_required_fields(lead_name=None, data=None, **kwargs):
        payload = LeadUtils.parse_payload(data=data, kwargs=kwargs)
        doc = LeadRepository.get_lead(lead_name) if lead_name else LeadRepository.new_lead()
        LeadUtils.apply_payload(doc, payload)

        required_fields = LeadUtils.get_required_fields(doc)
        missing_fields = LeadUtils.get_missing_fields(doc, required_fields)

        return {
            "status": "success",
            "doctype": "Lead",
            "lead_name": doc.name if lead_name else None,
            "default_values": {
                "status": doc.get("status"),
            },
            "required_fields": required_fields,
            "missing_fields": missing_fields,
        }

    @staticmethod
    def create_lead(data=None, **kwargs):
        payload = LeadUtils.parse_payload(data=data, kwargs=kwargs)
        doc = LeadRepository.new_lead()
        LeadUtils.apply_payload(doc, payload)

        required_fields = LeadUtils.get_required_fields(doc)
        missing_fields = LeadUtils.get_missing_fields(doc, required_fields)
        if missing_fields:
            return {
                "status": "error",
                "message": "بعض الحقول الإلزامية غير موجودة",
                "missing_fields": missing_fields,
            }

        LeadRepository.save_lead(doc)
        return {
            "status": "success",
            "message": "تم إنشاء Lead بنجاح",
            "lead_name": doc.name,
            "data": LeadDocument.to_detail(doc),
        }

    @staticmethod
    def update_lead(lead_name, data=None, **kwargs):
        payload = LeadUtils.parse_payload(data=data, kwargs=kwargs)
        doc = LeadRepository.get_lead(lead_name)
        LeadUtils.apply_payload(doc, payload)

        required_fields = LeadUtils.get_required_fields(doc)
        missing_fields = LeadUtils.get_missing_fields(doc, required_fields)
        if missing_fields:
            return {
                "status": "error",
                "message": "بعض الحقول الإلزامية غير موجودة بعد التعديل",
                "missing_fields": missing_fields,
            }

        LeadRepository.save_lead(doc)
        return {
            "status": "success",
            "message": "تم تحديث Lead بنجاح",
            "lead_name": doc.name,
            "data": LeadDocument.to_detail(doc),
        }

    @staticmethod
    def add_follow_up(lead_name, follow_up_date, expected_result_date, details, attachment=None):
        if not LeadRepository.lead_exists(lead_name):
            return {
                "status": "error",
                "message": f"Lead {lead_name} غير موجود",
            }

        if not follow_up_date or not expected_result_date or not details:
            return {
                "status": "error",
                "message": "الحقول المطلوبة هي: follow_up_date, expected_result_date, details",
            }

        doc = LeadRepository.get_lead(lead_name)
        LeadRepository.add_follow_up(
            doc=doc,
            follow_up_date=follow_up_date,
            expected_result_date=expected_result_date,
            details=details,
            attachment=attachment,
        )
        LeadRepository.save_lead(doc)

        return {
            "status": "success",
            "message": "تمت إضافة متابعة الـ Lead بنجاح",
            "lead_name": lead_name,
            "follow_ups": [LeadDocument.to_follow_up(row) for row in LeadRepository.get_follow_ups(doc)],
            "last_update_date": doc.get("mobile_api_last_update_date"),
            "next_follow_up_date": doc.get("mobile_api_next_follow_up_date"),
            "last_follow_up_report": doc.get("mobile_api_last_follow_up_report"),
            "data": LeadDocument.to_detail(
                doc,
                follow_ups=LeadRepository.get_follow_ups(doc),
                activity_log=LeadRepository.get_activity_log(lead_name),
            ),
        }
