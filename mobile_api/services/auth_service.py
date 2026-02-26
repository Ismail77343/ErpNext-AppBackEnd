import frappe


class AuthService:
    """
    خدمة المصادقة والمستخدمين
    """

    @staticmethod
    def authenticate(email, password):
        """
        تحقق من بيانات المستخدم وقم بتسجيل الدخول
        Args:
            email (str): بريد المستخدم الإلكتروني
            password (str): كلمة المرور
        Returns:
            dict: بيانات المستخدم أو رسالة خطأ
        """
        try:
            frappe.local.login_manager.authenticate(email, password)
            frappe.local.login_manager.post_login()

            user = frappe.get_doc("User", frappe.session.user)

            return {
                "status": "success",
                "user": user.full_name,
                "email": user.name,
                "roles": frappe.get_roles(user.name)
            }

        except frappe.AuthenticationError:
            frappe.clear_messages()
            frappe.local.response["http_status_code"] = 401
            return {
                "status": "error",
                "message": "بيانات دخول غير صحيحة"
            }
