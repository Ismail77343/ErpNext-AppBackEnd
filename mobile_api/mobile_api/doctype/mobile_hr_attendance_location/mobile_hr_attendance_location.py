# Copyright (c) 2026, ismail and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MobileHRAttendanceLocation(Document):
	def validate(self):
		if not self.radius_meters or self.radius_meters <= 0:
			frappe.throw("Radius must be greater than zero.")
		if self.latitude is None or self.longitude is None:
			frappe.throw("Latitude and Longitude are required.")
		if not (-90 <= float(self.latitude) <= 90):
			frappe.throw("Latitude must be between -90 and 90.")
		if not (-180 <= float(self.longitude) <= 180):
			frappe.throw("Longitude must be between -180 and 180.")
