"""
Mobile API - Entry Point
التطبيق الرئيسي لـ Mobile API

يتم استدعاء جميع المعالجات من خلال طبقة Handlers
"""

from mobile_api.handlers.auth_handler import login
from mobile_api.handlers.project_handler import (
    get_projects,
    get_my_projects,
    get_project_details
)
from mobile_api.handlers.task_handler import (
    get_task_details,
    add_follow_up,
    update_task_status
)
from mobile_api.handlers.crm_follow_up_handler import (
    get_crm_doc_details,
    add_crm_follow_up,
)
from mobile_api.handlers.lead_handler import (
    get_leads,
    get_lead_details,
    get_lead_follow_ups,
    get_lead_required_fields,
    create_lead,
    update_lead,
    add_lead_follow_up,
)
from mobile_api.handlers.material_request_handler import (
    create_material_request
)

__all__ = [
    'login',
    'get_projects',
    'get_my_projects',
    'get_project_details',
    'get_task_details',
    'add_follow_up',
    'update_task_status',
    'get_crm_doc_details',
    'add_crm_follow_up',
    'get_leads',
    'get_lead_details',
    'get_lead_follow_ups',
    'get_lead_required_fields',
    'create_lead',
    'update_lead',
    'add_lead_follow_up',
    'create_material_request'
]
