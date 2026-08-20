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
	const defaults = get_map_defaults();
	const start = current || {
		latitude: defaults.center[0],
		longitude: defaults.center[1],
	};
	let selected = { ...start };
	let selected_radius = cint(frm.doc.radius_meters || 150) || 150;
	let map = null;
	let marker = null;
	let circle = null;

	const dialog = new frappe.ui.Dialog({
		title: __("Pick Location"),
		size: "large",
		fields: [
			{
				fieldname: "map_area",
				fieldtype: "HTML",
				options: `
					<div class="mobile-hr-location-picker-map" style="height: 520px; border: 1px solid var(--border-color); border-radius: 6px; background: var(--bg-light-gray);"></div>
					<div class="text-muted small mt-2">${__("Click on the map or drag the marker to set the location.")}</div>
					<div class="mobile-hr-location-map-status text-muted small mt-1"></div>
					<div class="mobile-hr-location-tools" style="display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-top:10px;">
						<button class="btn btn-xs btn-default" data-action="current">${__("Use Current Location")}</button>
						<button class="btn btn-xs btn-default" data-action="existing">${__("Center on Saved Location")}</button>
					</div>`,
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
	show_map_status(dialog, __("Loading map..."));

	load_leaflet()
		.then(() => {
			setTimeout(initialize_map, 200);
		})
		.catch((error) => {
			console.error("Unable to load Leaflet for attendance location picker", error);
			show_map_status(
				dialog,
				__("Map library could not be loaded. Check that Frappe assets are available, then refresh the page."),
				"red"
			);
			frappe.msgprint(__("Map library could not be loaded. Refresh the page and try again."));
		});

	function initialize_map() {
		const wrapper = dialog.$wrapper.find(".mobile-hr-location-picker-map").get(0);
		if (!wrapper || typeof window.L === "undefined") {
			show_map_status(dialog, __("Map library is not loaded. Refresh the page and try again."), "red");
			return;
		}

		const L = window.L;
		const map_defaults = get_map_defaults();

		map = L.map(wrapper, { zoomControl: true }).setView(
			[start.latitude, start.longitude],
			current ? 16 : map_defaults.zoom
		);
		map.attributionControl.setPrefix("");

		const tile_layer = L.tileLayer(map_defaults.tiles, map_defaults.options).addTo(map);
		tile_layer.on("tileerror", () => {
			if (map.__mobile_hr_used_fallback_tiles) return;
			map.__mobile_hr_used_fallback_tiles = true;
			show_map_status(
				dialog,
				__("Configured map tiles did not load. Trying the default OpenStreetMap tiles..."),
				"orange"
			);
			L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
				maxZoom: 19,
				attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
			})
				.on("load", () => show_map_status(dialog, ""))
				.on("tileerror", () => {
					show_map_status(
						dialog,
						__("Map tiles are blocked or unreachable from this browser/network."),
						"red"
					);
				})
				.addTo(map);
		});
		tile_layer.on("load", () => show_map_status(dialog, ""));

		marker = L.marker([start.latitude, start.longitude], {
			draggable: true,
			icon: get_leaflet_marker_icon(L),
		}).addTo(map);
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
			refresh_circle();
			set_dialog_coordinates(dialog, selected, selected_radius);
			if (zoom_to_point) map.setView([selected.latitude, selected.longitude], Math.max(map.getZoom(), 16));
		}

		map.on("click", (event) => apply_point(event.latlng));
		marker.on("dragend", () => apply_point(marker.getLatLng()));

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

		invalidate_map_size(map);
	}

	function refresh_circle() {
		if (!circle) return;
		circle.setLatLng([selected.latitude, selected.longitude]);
		circle.setRadius(selected_radius);
	}
}

function show_map_status(dialog, message, indicator) {
	const $status = dialog.$wrapper.find(".mobile-hr-location-map-status");
	if (!$status.length) return;

	$status
		.toggleClass("text-danger", indicator === "red")
		.toggleClass("text-warning", indicator === "orange")
		.toggleClass("text-muted", !indicator)
		.text(message || "");
}

function invalidate_map_size(map) {
	window.requestAnimationFrame(() => {
		map.invalidateSize();
		setTimeout(() => map.invalidateSize(), 250);
		setTimeout(() => map.invalidateSize(), 750);
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

let mobile_hr_leaflet_loading = null;

function load_leaflet() {
	ensure_stylesheet("/assets/frappe/js/lib/leaflet/leaflet.css");

	if (typeof window.L !== "undefined") {
		return Promise.resolve();
	}

	if (mobile_hr_leaflet_loading) {
		return mobile_hr_leaflet_loading;
	}

	mobile_hr_leaflet_loading = new Promise((resolve, reject) => {
		const existing_script = Array.from(document.querySelectorAll("script[src]")).find((script) =>
			(script.getAttribute("src") || "").includes("/assets/frappe/js/lib/leaflet/leaflet.js")
		);

		const resolve_when_ready = () => {
			setTimeout(() => {
				if (typeof window.L !== "undefined") {
					resolve();
				} else {
					reject(new Error("Leaflet script loaded but window.L is unavailable"));
				}
			}, 100);
		};

		if (existing_script) {
			existing_script.addEventListener("load", resolve_when_ready, { once: true });
			existing_script.addEventListener("error", reject, { once: true });
			setTimeout(resolve_when_ready, 100);
			return;
		}

		const script = document.createElement("script");
		script.src = "/assets/frappe/js/lib/leaflet/leaflet.js";
		script.async = true;
		script.onload = resolve_when_ready;
		script.onerror = () => reject(new Error("Unable to load /assets/frappe/js/lib/leaflet/leaflet.js"));
		document.head.appendChild(script);
	});

	mobile_hr_leaflet_loading.catch(() => {
		mobile_hr_leaflet_loading = null;
	});

	return mobile_hr_leaflet_loading;
}

function ensure_stylesheet(href) {
	const exists = Array.from(document.querySelectorAll("link[rel='stylesheet']")).some((link) =>
		(link.getAttribute("href") || "").includes("leaflet.css")
	);
	if (exists) return;

	const link = document.createElement("link");
	link.rel = "stylesheet";
	link.href = href;
	document.head.appendChild(link);
}

function get_leaflet_marker_icon(L) {
	return L.divIcon({
		className: "mobile-hr-location-marker",
		iconSize: [28, 40],
		iconAnchor: [14, 40],
		popupAnchor: [0, -36],
		html: `
			<div style="
				width: 28px;
				height: 28px;
				background: #1683e8;
				border: 2px solid #ffffff;
				border-radius: 50% 50% 50% 0;
				box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
				transform: rotate(-45deg);
			">
				<div style="
					width: 8px;
					height: 8px;
					margin: 8px;
					background: #ffffff;
					border-radius: 50%;
				"></div>
			</div>`,
	});
}

function get_map_defaults() {
	const defaults = frappe.utils.map_defaults || {};
	return {
		center: defaults.center || [24.7136, 46.6753],
		zoom: defaults.zoom || 10,
		tiles: defaults.tiles || "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
		options: defaults.options || {
			attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
		},
		image_path: defaults.image_path || "/assets/frappe/images/leaflet/",
	};
}
