import frappe
from mobile_api.services.material_request_service import MaterialRequestService


@frappe.whitelist()
def create_material_request(project, items):
    """
    معالج: إنشاء طلب مادة جديد
    
    Args:
        project (str): اسم المشروع
        items (list): قائمة المواد المطلوبة
    
    Returns:
        dict: نتيجة العملية
    """
    try:
        result = MaterialRequestService.create_material_request(project, items)
        return result
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "create_material_request")
        return {"status": "error", "message": str(e)}
