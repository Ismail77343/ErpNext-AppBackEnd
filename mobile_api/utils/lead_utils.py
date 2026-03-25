import frappe


class LeadUtils:
    DEFAULT_STATUS = "Lead"
    EXCLUDED_REQUIRED_FIELDS = {"status"}
    EXCLUDED_FORM_FIELDS = {"name"}
    LAYOUT_FIELD_TYPES = {
        "Section Break",
        "Column Break",
        "Tab Break",
        "Fold",
        "HTML",
        "Button",
        "Image",
        "Heading",
        "Table",
        "Table MultiSelect",
    }

    @staticmethod
    def parse_payload(data=None, kwargs=None):
        payload = {}

        if data:
            payload = frappe.parse_json(data) if isinstance(data, str) else dict(data)

        if kwargs:
            for key, value in kwargs.items():
                if key in {"data", "lead_name"}:
                    continue
                payload[key] = value

        return payload

    @classmethod
    def get_writable_fields(cls, meta):
        return {
            field.fieldname: field
            for field in meta.fields
            if field.fieldname
            and field.fieldtype not in cls.LAYOUT_FIELD_TYPES
            and not field.read_only
        }

    @staticmethod
    def get_link_options(link_doctype, current_value=None, limit=20):
        if not link_doctype or not frappe.db.exists("DocType", link_doctype):
            return []

        rows = frappe.get_all(
            link_doctype,
            fields=["name"],
            order_by="modified desc",
            limit_page_length=limit,
        )
        values = [{"label": row["name"], "value": row["name"]} for row in rows]

        if current_value and all(option["value"] != current_value for option in values):
            values.insert(0, {"label": current_value, "value": current_value})

        return values

    @staticmethod
    def get_select_options(raw_options):
        return [
            {"label": option, "value": option}
            for option in (raw_options or "").split("\n")
            if option
        ]

    @staticmethod
    def evaluate_depends_on(expression, doc):
        if not expression:
            return False

        if expression.startswith("eval:"):
            expression = expression[5:]

        try:
            return bool(frappe.safe_eval(expression, None, {"doc": doc.as_dict()}))
        except Exception:
            return False

    @classmethod
    def get_required_fields(cls, doc):
        meta = frappe.get_meta(doc.doctype)
        writable_fields = cls.get_writable_fields(meta)
        required_fields = []

        for fieldname, field in writable_fields.items():
            if fieldname in cls.EXCLUDED_REQUIRED_FIELDS:
                continue

            is_required = bool(field.reqd)

            if not is_required and field.mandatory_depends_on:
                is_required = cls.evaluate_depends_on(field.mandatory_depends_on, doc)

            if is_required:
                required_fields.append({
                    "fieldname": fieldname,
                    "label": field.label or fieldname,
                    "fieldtype": field.fieldtype,
                    "options": field.options  # ✅ مهم
                })

        return required_fields

    @classmethod
    def apply_defaults(cls, doc):
        if doc.doctype == "Lead" and not doc.get("status"):
            doc.set("status", cls.DEFAULT_STATUS)

        return doc

    @classmethod
    def get_form_fields(cls, doc, mode="create"):
        meta = frappe.get_meta(doc.doctype)
        writable_fields = cls.get_writable_fields(meta)
        form_fields = []

        for fieldname, field in writable_fields.items():
            if fieldname in cls.EXCLUDED_FORM_FIELDS:
                continue

            field_data = {
                "fieldname": fieldname,
                "label": field.label or fieldname,
                "fieldtype": field.fieldtype,
                "required": bool(field.reqd),
                "read_only": bool(field.read_only),
                "hidden": bool(field.hidden),
                "value": doc.get(fieldname),
            }

            if field.fieldtype == "Select":
                field_data["options"] = cls.get_select_options(field.options)
            elif field.fieldtype == "Link":
                field_data["options"] = cls.get_link_options(field.options, current_value=doc.get(fieldname))
                field_data["link_doctype"] = field.options
            else:
                field_data["options"] = []

            if mode == "edit" and fieldname == "status":
                field_data["required"] = False

            form_fields.append(field_data)

        return form_fields

    @staticmethod
    def get_missing_fields(doc, required_fields):
        missing = []

        for field in required_fields:
            value = doc.get(field["fieldname"])
            if value in (None, "", []):
                missing.append(field)

        return missing

    @staticmethod
    def apply_payload(doc, payload):
        meta = frappe.get_meta(doc.doctype)
        writable_fields = LeadUtils.get_writable_fields(meta)

        for fieldname, value in payload.items():
            if fieldname in writable_fields:
                doc.set(fieldname, value)

        return LeadUtils.apply_defaults(doc)
