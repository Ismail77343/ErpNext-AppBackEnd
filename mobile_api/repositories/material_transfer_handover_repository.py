import frappe


class MaterialTransferHandoverRepository:
	DOCTYPE = "Mobile Material Transfer Handover"
	SETTINGS_DOCTYPE = "Mobile Material Transfer Handover Settings"

	@classmethod
	def get_settings(cls):
		if not frappe.db.exists("DocType", cls.SETTINGS_DOCTYPE):
			return frappe._dict(
				enabled=0,
				auto_create_task_follow_up=0,
				require_pickup_photo=1,
				require_pickup_location=1,
				require_delivery_photo=1,
				require_delivery_location=1,
				require_return_photo=1,
				require_return_location=1,
				max_photo_size_kb=2048,
				return_allowed_days_after_submit=1,
			)
		return frappe.get_cached_doc(cls.SETTINGS_DOCTYPE)

	@classmethod
	def get_doc(cls, name):
		return frappe.get_doc(cls.DOCTYPE, name)

	@classmethod
	def exists(cls, name):
		return bool(frappe.db.exists(cls.DOCTYPE, name))

	@classmethod
	def find_by_stock_entry(cls, stock_entry):
		if not stock_entry:
			return None
		return frappe.db.get_value(cls.DOCTYPE, {"stock_entry": stock_entry}, "name")

	@classmethod
	def insert(cls, values):
		doc = frappe.get_doc({"doctype": cls.DOCTYPE, **values})
		doc.insert(ignore_permissions=True)
		return doc

	@classmethod
	def save(cls, doc):
		doc.save(ignore_permissions=True)
		return doc

	@classmethod
	def get_list(cls, filters, limit_start=0, limit_page_length=20):
		return frappe.get_all(
			cls.DOCTYPE,
			filters=filters,
			fields=cls.list_fields(),
			order_by="modified desc",
			limit_start=int(limit_start or 0),
			limit_page_length=int(limit_page_length or 20),
		)

	@classmethod
	def count(cls, filters):
		return frappe.db.count(cls.DOCTYPE, filters=filters)

	@classmethod
	def list_fields(cls):
		return [
			"name",
			"stock_entry",
			"company",
			"posting_date",
			"submitted_on",
			"status",
			"receiver_user",
			"receiver_employee",
			"from_warehouse",
			"to_warehouse",
			"pickup_on",
			"pickup_photo",
			"pickup_latitude",
			"pickup_longitude",
			"pickup_accuracy_meters",
			"delivery_on",
			"delivery_photo",
			"delivery_latitude",
			"delivery_longitude",
			"delivery_accuracy_meters",
			"return_allowed_until",
			"last_return_stock_entry",
			"last_return_on",
			"last_return_latitude",
			"last_return_longitude",
			"last_return_accuracy_meters",
			"return_count",
			"task_follow_up",
			"creation",
			"modified",
		]

	@staticmethod
	def commit():
		frappe.db.commit()
