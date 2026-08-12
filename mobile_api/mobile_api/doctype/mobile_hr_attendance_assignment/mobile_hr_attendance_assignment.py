# Copyright (c) 2026, ismail and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


ASSIGNMENT_FIELD_BY_BASIS = {
	"Employee": "employee",
	"Department": "department",
	"Project": "project",
	"Branch": "branch",
	"Company": "company",
}


class MobileHRAttendanceAssignment(Document):
	def validate(self):
		fieldname = ASSIGNMENT_FIELD_BY_BASIS.get(self.assignment_basis)
		if not fieldname:
			frappe.throw("Invalid assignment basis.")
		if not self.get(fieldname):
			frappe.throw(f"{self.assignment_basis} is required for this assignment.")
		if self.valid_from and self.valid_to and self.valid_from > self.valid_to:
			frappe.throw("Valid From cannot be after Valid To.")
