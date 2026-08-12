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
        if ProjectRepository._can_view_all_projects():
            return rows
        return MobileAccessControl.filter_user_related_rows(
            "Project",
            rows,
            user_fields=["project_manager"],
            sales_person_fields=["sales_person"],
        )

    @staticmethod
    def _can_view_all_projects():
        if frappe.session.user == "Administrator":
            return True
        roles = set(frappe.get_roles(frappe.session.user))
        return bool(roles.intersection({"System Manager", "Projects Manager", "Project Manager"}))

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
        limit_start = int(limit_start or 0)
        limit_page_length = int(limit_page_length or 20)
        if ProjectRepository._can_view_all_projects():
            return frappe.get_list(
                "Project",
                fields=ProjectRepository._project_fields(),
                limit_start=limit_start,
                limit_page_length=limit_page_length,
            )

        rows = frappe.get_list("Project", fields=ProjectRepository._project_fields())
        filtered_rows = ProjectRepository._filter_projects(rows)
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
        if not frappe.has_permission("Project", "read", project_name):
            frappe.throw("Not permitted to read this Project", frappe.PermissionError)
        if not ProjectRepository._can_view_all_projects():
            row = frappe.db.get_value(
                "Project",
                project_name,
                ProjectRepository._project_fields(),
                as_dict=True,
            )
            if not ProjectRepository._filter_projects([row] if row else []):
                frappe.throw("Not permitted to read this Project", frappe.PermissionError)
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
