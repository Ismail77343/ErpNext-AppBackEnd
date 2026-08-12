# Copyright (c) 2026, ismail and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class MobileHRDeviceVerification(Document):
	def validate(self):
		self._set_employee_user()
		self._set_review_fields()
		self._validate_single_approved_device()

	def _set_employee_user(self):
		if not self.employee:
			frappe.throw("Employee is required.")
		if not self.device_id:
			frappe.throw("Device ID is required.")

		user_id = frappe.db.get_value("Employee", self.employee, "user_id")
		if user_id and not self.user:
			self.user = user_id

	def _set_review_fields(self):
		if self.status in ("Approved", "Rejected", "Revoked") and not self.reviewed_on:
			self.reviewed_by = frappe.session.user
			self.reviewed_on = now_datetime()

	def _validate_single_approved_device(self):
		if self.status != "Approved":
			return

		settings = frappe.get_single("Mobile HR Attendance Settings")
		if settings.get("allow_multiple_verified_devices"):
			return

		existing = frappe.db.exists(
			"Mobile HR Device Verification",
			{
				"employee": self.employee,
				"status": "Approved",
				"name": ["!=", self.name],
			},
		)
		if existing:
			frappe.throw(
				"Another approved mobile device already exists for this employee. Revoke it before approving a new device."
			)
