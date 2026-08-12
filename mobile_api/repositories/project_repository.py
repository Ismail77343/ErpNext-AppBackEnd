import frappe

from mobile_api.utils.access_control import MobileAccessControl


class ProjectRepository:
    """
    طبقة الوصول للبيانات - المشاريع
    """

    @staticmethod
    def _project_fields():
        fields = ["name", "project_name", "status", "customer", "percent_complete", "owner", "_assign"]
        meta = frappe.get_meta("Project")
        if meta.has_field("project_manager"):
            fields.append("project_manager")
        if meta.has_field("sales_person"):
            fields.append("sales_person")
        return fields

    @staticmethod
    def _filter_projects(rows):
        return MobileAccessControl.filter_user_related_rows(
            "Project",
            rows,
            user_fields=["project_manager"],
            sales_person_fields=["sales_person"],
        )

    @staticmethod
    def get_all_active_projects():
        """
        جلب جميع المشاريع التي لم تكتمل بعد
        Returns:
            list: قائمة المشاريع غير المكتملة
        """
        rows = frappe.get_list(
            "Project",
            fields=ProjectRepository._project_fields(),
            filters={"status": ["!=", "Completed"]}
        )
        return ProjectRepository._filter_projects(rows)

    @staticmethod
    def get_all_projects():
        """
        جلب جميع المشاريع بدون تصفية
        Returns:
            list: قائمة بجميع المشاريع
        """
        rows = frappe.get_list("Project", fields=ProjectRepository._project_fields())
        return ProjectRepository._filter_projects(rows)

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
        rows = frappe.get_list("Project", fields=ProjectRepository._project_fields())
        filtered_rows = ProjectRepository._filter_projects(rows)
        limit_start = int(limit_start or 0)
        limit_page_length = int(limit_page_length or 20)
        return filtered_rows[limit_start:limit_start + limit_page_length]

    @staticmethod
    def get_project(project_name):
        """
        جلب وثيقة المشروع الكاملة
        Args:
            project_name (str): اسم المشروع
        Returns:
            Document: وثيقة المشروع
        """
        return MobileAccessControl.ensure_read_access(
            "Project",
            project_name,
            user_fields=["project_manager"],
            sales_person_fields=["sales_person"],
        )

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
