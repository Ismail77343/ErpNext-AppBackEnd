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
from mobile_api.handlers.mobile_task_follow_up_handler import (
    create_mobile_task_follow_up,
    get_my_mobile_task_follow_ups,
    get_assigned_mobile_task_follow_ups,
    get_mobile_task_follow_up_details,
    add_mobile_task_follow_up_update,
    close_mobile_task_follow_up,
    get_mobile_task_follow_up_notifications,
    mark_mobile_task_follow_up_read,
)
from mobile_api.handlers.crm_follow_up_handler import (
    get_crm_doc_details,
    add_crm_follow_up,
)
from mobile_api.handlers.lead_handler import (
    get_lead_form,
    get_leads,
    get_leads_dashboard_summary,
    get_lead_details,
    get_lead_follow_ups,
    get_lead_required_fields,
    create_lead,
    update_lead,
    add_lead_follow_up,
)
from mobile_api.handlers.opportunity_handler import (
    get_opportunity_workflow_actions,
    execute_opportunity_workflow_action,
    send_opportunity_for_approval,
    return_opportunity_workflow,
    get_opportunity_form,
    get_opportunities,
    get_opportunities_dashboard_summary,
    get_opportunity_details,
    get_opportunity_follow_ups,
    get_opportunity_required_fields,
    create_opportunity,
    update_opportunity,
    add_opportunity_follow_up,
)
from mobile_api.handlers.quotation_handler import (
    get_quotations,
    get_quotations_dashboard_summary,
    get_quotation_details,
    get_quotation_print_data,
    get_quotation_follow_ups,
    add_quotation_follow_up,
    get_quotation_workflow_actions,
    execute_quotation_workflow_action,
    send_quotation_for_approval,
    return_quotation_workflow,
)
from mobile_api.handlers.notification_handler import (
    get_workflow_notifications,
    get_workflow_notifications_summary,
)
from mobile_api.handlers.material_request_handler import (
    create_material_request
)
from mobile_api.handlers.material_transfer_handover_handler import (
    get_my_material_transfer_handovers,
    get_material_transfer_handover_details,
    confirm_material_transfer_pickup,
    confirm_material_transfer_delivery,
    get_material_transfer_return_options,
    create_material_transfer_return,
)
from mobile_api.handlers.hr_attendance_handler import (
    get_hr_attendance_context,
    get_mobile_device_verification_status,
    mobile_employee_checkin,
    request_mobile_device_verification,
)

__all__ = [
    'login',
    'get_projects',
    'get_my_projects',
    'get_project_details',
    'get_task_details',
    'add_follow_up',
    'update_task_status',
    'create_mobile_task_follow_up',
    'get_my_mobile_task_follow_ups',
    'get_assigned_mobile_task_follow_ups',
    'get_mobile_task_follow_up_details',
    'add_mobile_task_follow_up_update',
    'close_mobile_task_follow_up',
    'get_mobile_task_follow_up_notifications',
    'mark_mobile_task_follow_up_read',
    'get_crm_doc_details',
    'add_crm_follow_up',
    'get_lead_form',
    'get_leads',
    'get_leads_dashboard_summary',
    'get_lead_details',
    'get_lead_follow_ups',
    'get_lead_required_fields',
    'create_lead',
    'update_lead',
    'add_lead_follow_up',
    'get_opportunity_workflow_actions',
    'execute_opportunity_workflow_action',
    'send_opportunity_for_approval',
    'return_opportunity_workflow',
    'get_opportunity_form',
    'get_opportunities',
    'get_opportunities_dashboard_summary',
    'get_opportunity_details',
    'get_opportunity_follow_ups',
    'get_opportunity_required_fields',
    'create_opportunity',
    'update_opportunity',
    'add_opportunity_follow_up',
    'get_quotations',
    'get_quotations_dashboard_summary',
    'get_quotation_details',
    'get_quotation_print_data',
    'get_quotation_follow_ups',
    'add_quotation_follow_up',
    'get_quotation_workflow_actions',
    'execute_quotation_workflow_action',
    'send_quotation_for_approval',
    'return_quotation_workflow',
    'get_workflow_notifications',
    'get_workflow_notifications_summary',
    'create_material_request',
    'get_my_material_transfer_handovers',
    'get_material_transfer_handover_details',
    'confirm_material_transfer_pickup',
    'confirm_material_transfer_delivery',
    'get_material_transfer_return_options',
    'create_material_transfer_return',
    'get_hr_attendance_context',
    'get_mobile_device_verification_status',
    'mobile_employee_checkin',
    'request_mobile_device_verification',
]
