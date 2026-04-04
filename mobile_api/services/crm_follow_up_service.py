from mobile_api.repositories.crm_follow_up_repository import CRMFollowUpRepository


class CRMFollowUpService:
    @staticmethod
    def get_document_with_follow_up(doctype, docname):
        doc = CRMFollowUpRepository.get_document(doctype, docname)
        doc_data = doc.as_dict()
        doc_data["mobile_api_follow_ups"] = CRMFollowUpRepository.get_follow_ups(doc)
        doc_data["activity_log"] = CRMFollowUpRepository.get_activity_log(doctype, docname)
        return doc_data

    @staticmethod
    def add_follow_up(doctype, docname, follow_up_date, expected_result_date, details, attachment=None):
        validation = CRMFollowUpService.validate_input(
            doctype, docname, follow_up_date, expected_result_date, details
        )
        if validation:
            return validation

        if not CRMFollowUpRepository.document_exists(doctype, docname):
            return {
                "status": "error",
                "message": f"المستند {doctype} / {docname} غير موجود",
            }

        doc = CRMFollowUpRepository.get_document(doctype, docname)
        CRMFollowUpRepository.append_follow_up(
            doc,
            follow_up_date=follow_up_date,
            expected_result_date=expected_result_date,
            details=details,
            attachment=attachment,
        )
        CRMFollowUpRepository.save_document(doc)

        return {
            "status": "success",
            "message": "تمت إضافة المتابعة بنجاح",
            "doctype": doctype,
            "docname": docname,
            "follow_up_date": follow_up_date,
            "expected_result_date": expected_result_date,
            "followed_by": CRMFollowUpRepository.get_follow_up_user(),
        }

    @staticmethod
    def validate_input(doctype, docname, follow_up_date, expected_result_date, details):
        if not doctype or not docname:
            return {"status": "error", "message": "يجب إرسال doctype و docname"}

        if not follow_up_date or not expected_result_date or not details:
            return {
                "status": "error",
                "message": "الحقول المطلوبة هي: follow_up_date, expected_result_date, details",
            }

        return None
