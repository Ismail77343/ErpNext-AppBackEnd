const MOBILE_API_FOLLOW_TABLE = "mobile_api_follow_ups";
const MOBILE_API_SUMMARY_FIELD_MAP = {
    mobile_api_last_update_date: "follow_up_date",
    mobile_api_next_follow_up_date: "expected_result_date",
    mobile_api_last_follow_up_report: "details",
    mobile_api_follow_up_attachment: "attachment",
};

frappe.ui.form.on("Lead", {
    refresh(frm) {
        setup_mobile_api_follow_up(frm);
    },
    mobile_api_follow_ups_remove(frm) {
        sync_mobile_api_follow_up_summary(frm);
    },
});

frappe.ui.form.on("Opportunity", {
    refresh(frm) {
        setup_mobile_api_follow_up(frm);
    },
    mobile_api_follow_ups_remove(frm) {
        sync_mobile_api_follow_up_summary(frm);
    },
});

frappe.ui.form.on("Quotation", {
    refresh(frm) {
        setup_mobile_api_follow_up(frm);
    },
    mobile_api_follow_ups_remove(frm) {
        sync_mobile_api_follow_up_summary(frm);
    },
});

function setup_mobile_api_follow_up(frm) {
    make_follow_table_read_only(frm);
    sync_mobile_api_follow_up_summary(frm, {
        mark_dirty: false,
        skip_dirty_trigger: true,
    });

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

function get_mobile_api_latest_follow_row(frm) {
    const rows = frm.doc[MOBILE_API_FOLLOW_TABLE] || [];
    if (!rows.length) {
        return null;
    }

    const toKey = (row) => ([
        row.follow_up_date || "",
        row.registered_on || "",
        row.modified || "",
        row.creation || "",
        String(row.idx || "")
    ]);

    return [...rows].sort((a, b) => {
        const aKey = toKey(a);
        const bKey = toKey(b);
        for (let i = 0; i < aKey.length; i++) {
            if (aKey[i] < bKey[i]) return 1;
            if (aKey[i] > bKey[i]) return -1;
        }
        return 0;
    })[0];
}

function sync_mobile_api_follow_up_summary(
    frm,
    { mark_dirty = true, skip_dirty_trigger = false } = {}
) {
    const latestRow = get_mobile_api_latest_follow_row(frm);
    const values = {};

    Object.entries(MOBILE_API_SUMMARY_FIELD_MAP).forEach(([targetField, sourceField]) => {
        if (!(targetField in frm.doc)) {
            return;
        }

        values[targetField] = latestRow ? (latestRow[sourceField] || null) : null;
    });

    const hasChanges = Object.entries(values).some(([fieldname, value]) => {
        const current = frm.doc[fieldname] ?? null;
        const next = value ?? null;
        return current !== next;
    });

    if (!hasChanges) {
        return Promise.resolve();
    }

    return frm.set_value(values, null, null, skip_dirty_trigger).then(() => {
        if (mark_dirty) {
            frm.dirty();
        }
    });
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
        async primary_action(values) {
            if (!values.follow_up_date || !values.expected_result_date || !values.details) {
                frappe.msgprint(__("Please complete all required fields."));
                return;
            }

            frm.add_child(MOBILE_API_FOLLOW_TABLE, {
                follow_up_date: values.follow_up_date,
                expected_result_date: values.expected_result_date,
                details: values.details,
                attachment: values.attachment || "",
                followed_by: frappe.session.user_fullname || frappe.session.user,
                registered_on: frappe.datetime.now_datetime(),
            });

            frm.refresh_field(MOBILE_API_FOLLOW_TABLE);
            await sync_mobile_api_follow_up_summary(frm);
            dialog.hide();

            await frm.save();
            frappe.show_alert({
                message: __("Follow up added"),
                indicator: "green",
            });
        },
    });

    dialog.show();
}

frappe.ui.form.on("Mobile CRM Follow Up", {
    follow_up_date(frm) {
        sync_mobile_api_follow_up_summary(frm);
    },
    expected_result_date(frm) {
        sync_mobile_api_follow_up_summary(frm);
    },
    details(frm) {
        sync_mobile_api_follow_up_summary(frm);
    },
    attachment(frm) {
        sync_mobile_api_follow_up_summary(frm);
    },
});
