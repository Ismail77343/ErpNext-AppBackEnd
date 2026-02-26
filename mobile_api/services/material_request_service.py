from mobile_api.repositories.material_request_repository import MaterialRequestRepository


class MaterialRequestService:
    """
    خدمات طلبات المواد - منطق العمل
    """

    @staticmethod
    def create_material_request(project, items):
        """
        إنشاء طلب مادة جديد للمشروع
        Args:
            project (str): اسم المشروع
            items (list): قائمة المواد المطلوبة
        Returns:
            dict: نتيجة العملية
        """
        try:
            request_name = MaterialRequestRepository.create_material_request(project, items)
            return {
                "status": "success",
                "message": "تم إنشاء طلب المادة بنجاح",
                "request_name": request_name
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
