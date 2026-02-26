import frappe
from mobile_api.services.project_service import ProjectService


@frappe.whitelist()
def get_projects():
    """
    معالج: الحصول على جميع المشاريع النشطة
    
    Returns:
        list: قائمة المشاريع
    """
    try:
        projects = ProjectService.get_all_projects()
        return projects
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_projects")
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_my_projects(limit_start=None, limit_page_length=None):
    """
    معالج: الحصول على مشاريعي مع Pagination
    
    Args:
        limit_start (int, optional): رقم الصف الأول
        limit_page_length (int, optional): عدد الصفوف في الصفحة
    
    Returns:
        list: قائمة المشاريع
    """
    try:
        projects = ProjectService.get_paginated_projects(limit_start, limit_page_length)
        return projects
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_my_projects")
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_project_details(project_name):
    """
    معالج: الحصول على تفاصيل المشروع مع المهام
    
    Args:
        project_name (str): اسم المشروع
    
    Returns:
        dict: بيانات المشروع والمهام
    """
    try:
        project_data = ProjectService.get_project_with_tasks(project_name)
        return project_data
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_project_details")
        return {"status": "error", "message": str(e)}
