frappe.ui.form.on("Mobile HR Attendance Location", {
	refresh(frm) {
		add_location_actions(frm);
		sync_preview_from_coordinates(frm);
	},

	latitude(frm) {
		if (frm.__mobile_hr_syncing_location) return;
		sync_preview_from_coordinates(frm);
	},

	longitude(frm) {
		if (frm.__mobile_hr_syncing_location) return;
		sync_preview_from_coordinates(frm);
	},

	radius_meters(frm) {
		if (frm.__mobile_hr_syncing_location) return;
		sync_preview_from_coordinates(frm);
	},

	location_preview(frm) {
		if (frm.__mobile_hr_syncing_location) return;

		const point = get_point_from_geolocation(frm.doc.location_preview);
		if (!point) return;

		set_location_values(frm, {
			latitude: point.latitude,
			longitude: point.longitude,
		});
	},
});

function add_location_actions(frm) {
	frm.add_custom_button(__("Pick on Map"), () => show_location_picker(frm), __("Location"));
	frm.add_custom_button(__("Use Current Location"), () => use_current_location(frm), __("Location"));

	if (has_coordinates(frm.doc)) {
		frm.add_custom_button(__("Open in Google Maps"), () => open_in_google_maps(frm.doc), __("Location"));
	}

	const message = has_coordinates(frm.doc)
		? __("Attendance geofence is centered at {0}, {1} with {2}m radius.", [
				format_float(frm.doc.latitude, 8),
				format_float(frm.doc.longitude, 8),
				cint(frm.doc.radius_meters || 0),
		  ])
		: __("Pick the attendance point from the map or use the current device location.");

	frm.dashboard.clear_comment();
	frm.dashboard.add_comment(message, has_coordinates(frm.doc) ? "green" : "orange", true);
}

function show_location_picker(frm) {
	const current = get_doc_point(frm.doc) || get_point_from_geolocation(frm.doc.location_preview);
	const defaults = frappe.utils.map_defaults || {};
	const start = current || {
		latitude: (defaults.center || [24.7136, 46.6753])[0],
		longitude: (defaults.center || [24.7136, 46.6753])[1],
	};
	let selected = { ...start };
	let selected_radius = cint(frm.doc.radius_meters || 150) || 150;
	let map = null;
	let marker = null;
	let circle = null;
	let map_setup_attempts = 0;

	const dialog = new frappe.ui.Dialog({
		title: __("Pick Location"),
		size: "large",
		fields: [
			{
				fieldname: "location_map",
				fieldtype: "Geolocation",
				label: __("Location Map"),
				description: __("Click on the map or drag the marker to set the attendance location."),
			},
			{
				fieldname: "radius_meters",
				fieldtype: "Int",
				label: __("Allowed Radius (Meters)"),
				default: selected_radius,
				reqd: 1,
				change() {
					selected_radius = cint(dialog.get_value("radius_meters") || 0) || 1;
					refresh_circle();
					set_dialog_coordinates(dialog, selected, selected_radius);
				},
			},
			{
				fieldname: "coordinates",
				fieldtype: "Data",
				label: __("Selected Coordinates"),
				read_only: 1,
			},
			{
				fieldname: "map_tools",
				fieldtype: "HTML",
				options: `<div class="mobile-hr-location-tools" style="display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-top:4px;">
					<button class="btn btn-xs btn-default" data-action="current">${__("Use Current Location")}</button>
					<button class="btn btn-xs btn-default" data-action="existing">${__("Center on Saved Location")}</button>
				</div>`,
			},
		],
		primary_action_label: __("Apply Location"),
		primary_action() {
			selected_radius = cint(dialog.get_value("radius_meters") || 0) || 1;
			set_location_values(frm, {
				latitude: selected.latitude,
				longitude: selected.longitude,
				radius_meters: selected_radius,
				location_preview: make_marker_geolocation(selected.latitude, selected.longitude),
			}).then(() => dialog.hide());
		},
	});

	dialog.show();
	dialog.set_value("radius_meters", selected_radius);
	set_dialog_coordinates(dialog, selected, selected_radius);
	setTimeout(initialize_map, 100);

	function initialize_map() {
		const control = dialog.fields_dict.location_map;
		if ((!control || !control.map || typeof window.L === "undefined") && map_setup_attempts < 30) {
			map_setup_attempts += 1;
			setTimeout(initialize_map, 100);
			return;
		}
		if (!control || !control.map || typeof window.L === "undefined") {
			frappe.msgprint(__("The map could not be initialized. Refresh the page and try again."));
			return;
		}
		if (control.__mobile_hr_picker_ready) return;
		control.__mobile_hr_picker_ready = true;

		const L = window.L;
		map = control.map;
		if (control.draw_control) map.removeControl(control.draw_control);
		if (control.editableLayers) control.clear_editable_layers();
		dialog.$wrapper.find(".map-wrapper > div").css({
			"min-height": "410px",
			cursor: "crosshair",
		});
		map.setView([start.latitude, start.longitude], current ? 16 : defaults.zoom || 10);

		marker = L.marker([start.latitude, start.longitude], {
			draggable: true,
			icon: make_picker_marker_icon(L),
		}).addTo(map);
		marker.bindTooltip(__("Selected attendance location"), {
			direction: "top",
			offset: [0, -34],
		});
		circle = L.circle([start.latitude, start.longitude], {
			radius: selected_radius,
			color: "#1f8ef1",
			weight: 2,
			fillColor: "#1f8ef1",
			fillOpacity: 0.12,
		}).addTo(map);

		function apply_point(latlng, zoom_to_point = false) {
			selected = {
				latitude: flt(latlng.lat, 8),
				longitude: flt(latlng.lng, 8),
			};
			marker.setLatLng([selected.latitude, selected.longitude]);
			marker.openTooltip();
			refresh_circle();
			set_dialog_coordinates(dialog, selected, selected_radius);
			if (zoom_to_point) map.setView([selected.latitude, selected.longitude], Math.max(map.getZoom(), 16));
		}

		map.on("click", (event) => apply_point(event.latlng));
		marker.on("dragend", () => apply_point(marker.getLatLng()));
		marker.openTooltip();

		dialog.$wrapper.find('[data-action="existing"]').on("click", () => {
			if (!has_coordinates(frm.doc)) {
				frappe.show_alert({ message: __("No saved coordinates yet."), indicator: "orange" });
				return;
			}
			apply_point({ lat: frm.doc.latitude, lng: frm.doc.longitude }, true);
		});

		dialog.$wrapper.find('[data-action="current"]').on("click", () => {
			read_browser_location((point) => apply_point({ lat: point.latitude, lng: point.longitude }, true));
		});

		window.requestAnimationFrame(() => {
			map.invalidateSize();
			setTimeout(() => map.invalidateSize(), 250);
			setTimeout(() => map.invalidateSize(), 750);
		});
	}

	function refresh_circle() {
		if (!circle) return;
		circle.setLatLng([selected.latitude, selected.longitude]);
		circle.setRadius(selected_radius);
	}
}

function make_picker_marker_icon(L) {
	return L.divIcon({
		className: "mobile-hr-picker-marker-wrapper",
		iconSize: [32, 44],
		iconAnchor: [16, 44],
		popupAnchor: [0, -42],
		html: `<div style="
			width:30px;
			height:30px;
			background:#1683e8;
			border:3px solid #fff;
			border-radius:50% 50% 50% 0;
			box-shadow:0 2px 10px rgba(0,0,0,.45);
			transform:rotate(-45deg);
		"><span style="
			display:block;
			width:9px;
			height:9px;
			margin:8px;
			background:#fff;
			border-radius:50%;
		"></span></div>`,
	});
}

function use_current_location(frm) {
	read_browser_location((point) => {
		set_location_values(frm, {
			latitude: point.latitude,
			longitude: point.longitude,
			location_preview: make_marker_geolocation(point.latitude, point.longitude),
		});
	});
}

function read_browser_location(callback) {
	if (!navigator.geolocation) {
		frappe.msgprint(__("Geolocation is not supported by this browser."));
		return;
	}

	frappe.show_alert({ message: __("Reading current location..."), indicator: "blue" });
	navigator.geolocation.getCurrentPosition(
		(position) => {
			callback({
				latitude: flt(position.coords.latitude, 8),
				longitude: flt(position.coords.longitude, 8),
			});
		},
		(error) => {
			frappe.msgprint(
				__("Unable to read current location. Allow location permission or use HTTPS, then try again. {0}", [
					error && error.message ? error.message : "",
				])
			);
		},
		{ enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
	);
}

function open_in_google_maps(doc) {
	if (!has_coordinates(doc)) return;
	window.open(`https://www.google.com/maps?q=${flt(doc.latitude, 8)},${flt(doc.longitude, 8)}`, "_blank");
}

function get_point_from_geolocation(value) {
	if (!value) return null;

	let data;
	try {
		data = typeof value === "string" ? JSON.parse(value) : value;
	} catch (error) {
		return null;
	}

	const features = data.features || [];
	for (const feature of features) {
		const geometry = feature.geometry || {};
		const coordinates = geometry.coordinates || [];
		if (geometry.type === "Point" && coordinates.length >= 2) {
			return {
				latitude: flt(coordinates[1], 8),
				longitude: flt(coordinates[0], 8),
			};
		}
	}
	return null;
}

function make_marker_geolocation(latitude, longitude) {
	latitude = flt(latitude, 8);
	longitude = flt(longitude, 8);
	if (!latitude && !longitude) return "";

	return JSON.stringify({
		type: "FeatureCollection",
		features: [
			{
				type: "Feature",
				properties: { point_type: "marker" },
				geometry: { type: "Point", coordinates: [longitude, latitude] },
			},
		],
	});
}

function get_doc_point(doc) {
	if (!has_coordinates(doc)) return null;
	return {
		latitude: flt(doc.latitude, 8),
		longitude: flt(doc.longitude, 8),
	};
}

function has_coordinates(doc) {
	return Boolean(doc && (flt(doc.latitude || 0) || flt(doc.longitude || 0)));
}

function set_dialog_coordinates(dialog, point, radius) {
	dialog.set_value(
		"coordinates",
		`${__("Latitude")}: ${format_float(point.latitude, 8)}, ${__("Longitude")}: ${format_float(point.longitude, 8)} · ${__(
			"Radius"
		)}: ${cint(radius)}m`
	);
}

function sync_preview_from_coordinates(frm) {
	if (!has_coordinates(frm.doc)) return;
	set_location_values(frm, {
		location_preview: make_marker_geolocation(frm.doc.latitude, frm.doc.longitude),
	});
}

async function set_location_values(frm, values) {
	frm.__mobile_hr_syncing_location = true;
	try {
		for (const [fieldname, value] of Object.entries(values)) {
			if (frm.doc[fieldname] !== value) {
				await frm.set_value(fieldname, value);
			}
		}
	} finally {
		frm.__mobile_hr_syncing_location = false;
	}
}
