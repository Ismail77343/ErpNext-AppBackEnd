import frappe
from mobile_api.services.task_service import TaskService


@frappe.whitelist()
def get_task_details(task_name):
    """
    معالج: الحصول على تفاصيل المهمة
    
    Args:
        task_name (str): اسم المهمة
    
    Returns:
        dict: بيانات المهمة الكاملة
    """
    try:
        task_data = TaskService.get_task_with_followers(task_name)
        return task_data
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_task_details")
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def add_follow_up(task_name, date_follow, time_follow=None, progress=None, follow_up=None, attachment=None):
    """
    معالج: إضافة متابعة للمهمة
    
    Args:
        task_name (str): اسم المهمة
        date_follow (str): تاريخ المتابعة
        time_follow (str, optional): وقت المتابعة
        progress (int, optional): نسبة التقدم (0-100)
        follow_up (str): ملاحظات المتابعة
        attachment (str, optional): المرفقات
    
    Returns:
        dict: نتيجة العملية
    """
    try:
        result = TaskService.add_follow_up(
            task_name, date_follow, time_follow, progress, follow_up, attachment
        )
        return result
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "add_follow_up")
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def update_task_status(task_name, status):
    """
    معالج: تحديث حالة المهمة
    
    Args:
        task_name (str): اسم المهمة
        status (str): الحالة الجديدة
    
    Returns:
        dict: نتيجة العملية
    """
    try:
        result = TaskService.update_status(task_name, status)
        return result
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "update_task_status")
        return {"status": "error", "message": str(e)}
