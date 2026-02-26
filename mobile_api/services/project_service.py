from mobile_api.repositories.project_repository import ProjectRepository


class ProjectService:
    """
    خدمات المشاريع - منطق العمل
    """

    @staticmethod
    def get_all_projects():
        """
        الحصول على جميع المشاريع غير المكتملة
        Returns:
            list: قائمة المشاريع
        """
        return ProjectRepository.get_all_active_projects()

    @staticmethod
    def get_paginated_projects(limit_start=None, limit_page_length=None):
        """
        الحصول على مشاريع مع تقسيم الصفحات
        Args:
            limit_start (int): رقم الصف الأول
            limit_page_length (int): عدد الصفوف في الصفحة
        Returns:
            list: قائمة المشاريع
        """
        ls, lpl = ProjectService._parse_pagination(limit_start, limit_page_length)
        
        if limit_start is None and limit_page_length is None:
            return ProjectRepository.get_all_projects()
        
        return ProjectRepository.get_paginated_projects(ls, lpl)

    @staticmethod
    def get_project_with_tasks(project_name):
        """
        الحصول على تفاصيل المشروع مع جميع المهام
        Args:
            project_name (str): اسم المشروع
        Returns:
            dict: بيانات المشروع والمهام
        """
        project = ProjectRepository.get_project(project_name)
        tasks = ProjectRepository.get_project_tasks(project_name)
        
        project_data = project.as_dict()
        project_data["tasks"] = tasks
        return project_data

    @staticmethod
    def _parse_pagination(limit_start, limit_page_length):
        """
        تحويل وتحقق من معاملات تقسيم الصفحات
        Args:
            limit_start: رقم الصف الأول
            limit_page_length: عدد الصفوف في الصفحة
        Returns:
            tuple: (limit_start, limit_page_length)
        """
        try:
            ls = int(limit_start) if limit_start is not None else 0
        except (ValueError, TypeError):
            ls = 0
        try:
            lpl = int(limit_page_length) if limit_page_length is not None else 20
        except (ValueError, TypeError):
            lpl = 20
        return ls, lpl
