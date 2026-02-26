import frappe


class MaterialRequestRepository:
    """
    طبقة الوصول للبيانات - طلبات المواد
    """

    @staticmethod
    def create_material_request(project, items):
        """
        إنشاء طلب مادة جديد
        Args:
            project (str): اسم المشروع
            items (list): قائمة المواد المطلوبة
        Returns:
            str: اسم الوثيقة الجديدة
        """
        doc = frappe.get_doc({
            "doctype": "Material Request",
            "material_request_type": "Purchase",
            "project": project,
            "items": items
        })
        doc.insert()
        frappe.db.commit()
        return doc.name
