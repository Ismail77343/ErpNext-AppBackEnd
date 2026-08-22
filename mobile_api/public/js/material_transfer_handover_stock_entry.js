frappe.ui.form.on("Stock Entry", {
	setup(frm) {
		setup_material_transfer_handover(frm);
	},
	onload(frm) {
		setup_material_transfer_handover(frm);
	},
	refresh(frm) {
		setup_material_transfer_handover(frm);
	},
	stock_entry_type(frm) {
		setup_material_transfer_handover(frm);
	},
	purpose(frm) {
		setup_material_transfer_handover(frm);
	},
	mobile_no_receiver_required(frm) {
		if (frm.doc.mobile_no_receiver_required && frm.doc.mobile_handover_receiver_user) {
			frm.set_value("mobile_handover_receiver_user", null);
		}
		setup_material_transfer_handover(frm);
	},
});

function setup_material_transfer_handover(frm) {
	const is_material_transfer = is_material_transfer_stock_entry(frm);
	const receiver_required = is_material_transfer && !cint(frm.doc.mobile_no_receiver_required);

	toggle_handover_field(frm, "mobile_material_handover_section", is_material_transfer);
	toggle_handover_field(frm, "mobile_no_receiver_required", is_material_transfer);
	toggle_handover_field(frm, "mobile_handover_receiver_user", receiver_required);
	toggle_handover_field(frm, "mobile_material_handover", is_material_transfer);
	toggle_handover_field(frm, "mobile_handover_status", is_material_transfer);
	toggle_handover_field(frm, "mobile_handover_task", is_material_transfer);
	toggle_handover_field(frm, "mobile_pickup_photo", is_material_transfer);
	toggle_handover_field(frm, "mobile_pickup_on", is_material_transfer);
	toggle_handover_field(frm, "mobile_pickup_location", is_material_transfer);
	toggle_handover_field(frm, "mobile_pickup_latitude", is_material_transfer);
	toggle_handover_field(frm, "mobile_pickup_longitude", is_material_transfer);
	toggle_handover_field(frm, "mobile_pickup_accuracy_meters", is_material_transfer);
	toggle_handover_field(frm, "mobile_delivery_photo", is_material_transfer);
	toggle_handover_field(frm, "mobile_delivery_on", is_material_transfer);
	toggle_handover_field(frm, "mobile_delivery_location", is_material_transfer);
	toggle_handover_field(frm, "mobile_delivery_latitude", is_material_transfer);
	toggle_handover_field(frm, "mobile_delivery_longitude", is_material_transfer);
	toggle_handover_field(frm, "mobile_delivery_accuracy_meters", is_material_transfer);
	toggle_handover_field(frm, "mobile_last_return_stock_entry", is_material_transfer);
	toggle_handover_field(frm, "mobile_last_return_photo", is_material_transfer);
	toggle_handover_field(frm, "mobile_last_return_on", is_material_transfer);
	toggle_handover_field(frm, "mobile_last_return_location", is_material_transfer);
	toggle_handover_field(frm, "mobile_last_return_latitude", is_material_transfer);
	toggle_handover_field(frm, "mobile_last_return_longitude", is_material_transfer);
	toggle_handover_field(frm, "mobile_last_return_accuracy_meters", is_material_transfer);

	frm.toggle_reqd("mobile_handover_receiver_user", receiver_required);

	if (!is_material_transfer) {
		frm.toggle_display("mobile_handover_column_break", false);
		return;
	}
	frm.toggle_display("mobile_handover_column_break", true);
}

function is_material_transfer_stock_entry(frm) {
	return frm.doc.purpose === "Material Transfer" || frm.doc.stock_entry_type === "Material Transfer";
}

function toggle_handover_field(frm, fieldname, show) {
	if (frm.fields_dict[fieldname]) {
		frm.toggle_display(fieldname, show);
	}
}
