import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


VALID_STATUSES = {
	"Pending Pickup",
	"Picked Up",
	"Delivered",
	"Return Draft Created",
	"Closed",
	"Cancelled",
}


class MobileMaterialTransferHandover(Document):
	def validate(self):
		if self.status not in VALID_STATUSES:
			frappe.throw(_("Invalid Material Transfer Handover status: {0}").format(self.status))
		if self.stock_entry and not frappe.db.exists("Stock Entry", self.stock_entry):
			frappe.throw(_("Stock Entry {0} was not found.").format(frappe.bold(self.stock_entry)))
		if self.receiver_user and not frappe.db.exists("User", self.receiver_user):
			frappe.throw(_("Receiver User {0} was not found.").format(frappe.bold(self.receiver_user)))
		if self.return_allowed_until and self.submitted_on:
			if getdate(self.return_allowed_until) < getdate(self.submitted_on):
				frappe.throw(_("Return Allowed Until cannot be before Submitted On."))

