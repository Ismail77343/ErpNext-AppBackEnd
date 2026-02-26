import frappe


class ProjectRepository:
    """
    طبقة الوصول للبيانات - المشاريع
    """

    @staticmethod
    def get_all_active_projects():
        """
        جلب جميع المشاريع التي لم تكتمل بعد
        Returns:
            list: قائمة المشاريع غير المكتملة
        """
        return frappe.get_list(
            "Project",
            fields=["name", "project_name", "status"],
            filters={"status": ["!=", "Completed"]}
        )

    @staticmethod
    def get_all_projects():
        """
        جلب جميع المشاريع بدون تصفية
        Returns:
            list: قائمة بجميع المشاريع
        """
        fields = ["name", "project_name", "status", "customer", "percent_complete"]
        return frappe.get_list("Project", fields=fields)

    @staticmethod
    def get_paginated_projects(limit_start, limit_page_length):
        """
        جلب المشاريع مع تقسيم الصفحات
        Args:
            limit_start (int): رقم الصف الذي سيبدأ منه
            limit_page_length (int): عدد الصفوف في كل صفحة
        Returns:
            list: قائمة المشاريع المطلوبة
        """
        fields = ["name", "project_name", "status", "customer", "percent_complete"]
        return frappe.get_list(
            "Project",
            fields=fields,
            limit_start=limit_start,
            limit_page_length=limit_page_length,
        )

    @staticmethod
    def get_project(project_name):
        """
        جلب وثيقة المشروع الكاملة
        Args:
            project_name (str): اسم المشروع
        Returns:
            Document: وثيقة المشروع
        """
        return frappe.get_doc("Project", project_name)

    @staticmethod
    def get_project_tasks(project_name):
        """
        جلب جميع مهام المشروع المحددة
        Args:
            project_name (str): اسم المشروع
        Returns:
            list: قائمة المهام
        """
        return frappe.get_list(
            "Task",
            filters={"project": project_name},
            fields=[
                "name", "subject", "status", "priority",
                "progress", "exp_start_date", "exp_end_date"
            ],
            order_by="exp_end_date asc"
        )
