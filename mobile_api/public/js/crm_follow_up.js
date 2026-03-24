const MOBILE_API_FOLLOW_TABLE = "mobile_api_follow_ups";

frappe.ui.form.on("Lead", {
    refresh(frm) {
        setup_mobile_api_follow_up(frm);
    },
});

frappe.ui.form.on("Opportunity", {
    refresh(frm) {
        setup_mobile_api_follow_up(frm);
    },
});

frappe.ui.form.on("Quotation", {
    refresh(frm) {
        setup_mobile_api_follow_up(frm);
    },
});

function setup_mobile_api_follow_up(frm) {
    make_follow_table_read_only(frm);

    if (frm.is_new()) {
        return;
    }

    frm.add_custom_button(__("Add Follow"), () => {
        open_follow_dialog(frm);
    });
}

function make_follow_table_read_only(frm) {
    const field = frm.fields_dict[MOBILE_API_FOLLOW_TABLE];
    if (!field || !field.grid) {
        return;
    }

    frm.set_df_property(MOBILE_API_FOLLOW_TABLE, "read_only", 1);
    field.grid.cannot_add_rows = true;
    field.grid.cannot_delete_rows = true;
    field.grid.only_sortable();
    field.grid.refresh();
}

function open_follow_dialog(frm) {
    const dialog = new frappe.ui.Dialog({
        title: __("Add Follow"),
        fields: [
            {
                fieldtype: "Date",
                fieldname: "follow_up_date",
                label: __("Last Update Date"),
                default: frappe.datetime.get_today(),
                reqd: 1,
            },
            {
                fieldtype: "Date",
                fieldname: "expected_result_date",
                label: __("Next Follow Up Date"),
                reqd: 1,
            },
            {
                fieldtype: "Small Text",
                fieldname: "details",
                label: __("Last Follow Up Report"),
                reqd: 1,
            },
            {
                fieldtype: "Attach",
                fieldname: "attachment",
                label: __("Attachment"),
            },
        ],
        primary_action_label: __("Add"),
        primary_action(values) {
            if (!values.follow_up_date || !values.expected_result_date || !values.details) {
                frappe.msgprint(__("Please complete all required fields."));
                return;
            }

            const row = frm.add_child(MOBILE_API_FOLLOW_TABLE, {
                follow_up_date: values.follow_up_date,
                expected_result_date: values.expected_result_date,
                details: values.details,
                attachment: values.attachment || "",
                registered_on: frappe.datetime.now_datetime(),
            });

            frm.set_value("mobile_api_last_update_date", values.follow_up_date);
            frm.set_value("mobile_api_next_follow_up_date", values.expected_result_date);
            frm.set_value("mobile_api_last_follow_up_report", values.details);
            if ("mobile_api_follow_up_attachment" in frm.doc) {
                frm.set_value("mobile_api_follow_up_attachment", values.attachment || "");
            }

            frm.refresh_field(MOBILE_API_FOLLOW_TABLE);
            frm.dirty();
            dialog.hide();

            frm.save().then(() => {
                frappe.show_alert({
                    message: __("Follow up added"),
                    indicator: "green",
                });
            });
        },
    });

    dialog.show();
}
