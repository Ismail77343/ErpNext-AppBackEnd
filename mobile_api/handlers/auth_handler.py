import frappe
from mobile_api.services.auth_service import AuthService


@frappe.whitelist(allow_guest=True)
def login(email, password):
    """
    معالج تسجيل الدخول
    
    Args:
        email (str): بريد المستخدم الإلكتروني
        password (str): كلمة المرور
    
    Returns:
        dict: بيانات المستخدم أو رسالة خطأ
    """
    try:
        result = AuthService.authenticate(email, password)
        return result
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "login_handler")
        return {
            "status": "error",
            "message": str(e)
        }
