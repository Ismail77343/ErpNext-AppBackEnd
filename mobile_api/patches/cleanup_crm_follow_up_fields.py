import frappe


OLD_CUSTOM_FIELDS = [
    "Lead-mobile_api_last_follow_up_date",
    "Lead-mobile_api_expected_result_date",
    "Lead-mobile_api_follow_up_details",
    "Opportunity-mobile_api_last_follow_up_date",
    "Opportunity-mobile_api_expected_result_date",
    "Opportunity-mobile_api_follow_up_details",
    "Quotation-mobile_api_last_follow_up_date",
    "Quotation-mobile_api_expected_result_date",
    "Quotation-mobile_api_follow_up_details",
]


def execute():
    for custom_field_name in OLD_CUSTOM_FIELDS:
        if frappe.db.exists("Custom Field", custom_field_name):
            frappe.delete_doc("Custom Field", custom_field_name, force=1)
