import frappe


class OpportunityUtils:
    DEFAULT_STATUS = "Open"
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
                if key in {"data", "opportunity_name"}:
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
    def get_dynamic_link_options(doc, field):
        link_doctype_field = field.options
        link_doctype = doc.get(link_doctype_field)

        if not link_doctype:
            return []

        return OpportunityUtils.get_link_options(link_doctype, current_value=doc.get(field.fieldname))

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
                required_fields.append(
                    {
                        "fieldname": fieldname,
                        "label": field.label or fieldname,
                        "fieldtype": field.fieldtype,
                        "options": field.options,
                    }
                )

        return required_fields

    @classmethod
    def apply_defaults(cls, doc):
        if doc.doctype == "Opportunity" and not doc.get("status"):
            doc.set("status", cls.DEFAULT_STATUS)
        return doc

    @staticmethod
    def build_content_from_party(doc, party_doc=None):
        display_name = (
            (party_doc.get("customer_name") if party_doc else None)
            or (party_doc.get("lead_name") if party_doc else None)
            or (party_doc.get("company_name") if party_doc else None)
            or doc.get("customer_name")
            or doc.get("party_name")
            or doc.get("name")
        )

        parts = [display_name]

        if doc.get("status"):
            parts.append(f"Status: {doc.get('status')}")

        if doc.get("opportunity_amount"):
            parts.append(f"Amount: {doc.get('opportunity_amount')}")

        if doc.get("expected_closing"):
            parts.append(f"Expected Closing: {doc.get('expected_closing')}")

        return " | ".join(part for part in parts if part)

    @classmethod
    def get_party_address_data(cls, party_doc):
        if not party_doc:
            return {}

        if party_doc.doctype == "Lead":
            return {
                "city": party_doc.get("city"),
                "state": party_doc.get("state"),
                "country": party_doc.get("country"),
                "address_line1": party_doc.get("address_line1"),
                "address_line2": party_doc.get("address_line2"),
            }

        if party_doc.doctype != "Customer":
            return {}

        dynamic_links = frappe.get_all(
            "Dynamic Link",
            filters={
                "link_doctype": "Customer",
                "link_name": party_doc.name,
                "parenttype": "Address",
            },
            fields=["parent"],
            order_by="modified desc",
            limit_page_length=1,
        )
        if not dynamic_links:
            return {}

        address = frappe.get_doc("Address", dynamic_links[0]["parent"])
        return {
            "city": address.get("city"),
            "state": address.get("state"),
            "country": address.get("country"),
            "address_line1": address.get("address_line1"),
            "address_line2": address.get("address_line2"),
        }

    @classmethod
    def sync_from_party(cls, doc, party_doc=None):
        if not party_doc:
            return cls.apply_defaults(doc)

        address_data = cls.get_party_address_data(party_doc)

        if doc.get("opportunity_from") == "Lead":
            display_name = (
                party_doc.get("company_name")
                or party_doc.get("lead_name")
                or party_doc.get("name")
            )
            doc.set("customer_name", display_name)
            doc.set("title", display_name)
            if hasattr(doc, "contact_email"):
                doc.set("contact_email", party_doc.get("email_id"))
            if hasattr(doc, "contact_mobile"):
                doc.set("contact_mobile", party_doc.get("mobile_no"))
            if hasattr(doc, "phone") and party_doc.get("phone"):
                doc.set("phone", party_doc.get("phone"))
            if hasattr(doc, "whatsapp") and party_doc.get("whatsapp_no"):
                doc.set("whatsapp", party_doc.get("whatsapp_no"))
            if hasattr(doc, "territory") and party_doc.get("territory"):
                doc.set("territory", party_doc.get("territory"))
            if hasattr(doc, "source") and party_doc.get("source"):
                doc.set("source", party_doc.get("source"))

        elif doc.get("opportunity_from") == "Customer":
            display_name = party_doc.get("customer_name") or party_doc.get("name")
            doc.set("customer_name", display_name)
            doc.set("title", display_name)
            if hasattr(doc, "contact_email"):
                doc.set("contact_email", party_doc.get("email_id"))
            if hasattr(doc, "contact_mobile"):
                doc.set("contact_mobile", party_doc.get("mobile_no"))
            if hasattr(doc, "territory") and party_doc.get("territory"):
                doc.set("territory", party_doc.get("territory"))

        if hasattr(doc, "city") and address_data.get("city"):
            doc.set("city", address_data.get("city"))
        if hasattr(doc, "state") and address_data.get("state"):
            doc.set("state", address_data.get("state"))
        if hasattr(doc, "country") and address_data.get("country"):
            doc.set("country", address_data.get("country"))
        if hasattr(doc, "address_line1") and address_data.get("address_line1"):
            doc.set("address_line1", address_data.get("address_line1"))
        if hasattr(doc, "address_line2") and address_data.get("address_line2"):
            doc.set("address_line2", address_data.get("address_line2"))
        if hasattr(doc, "address_display"):
            address_lines = [
                address_data.get("address_line1"),
                address_data.get("address_line2"),
                address_data.get("city"),
                address_data.get("state"),
                address_data.get("country"),
            ]
            address_display = ", ".join(line for line in address_lines if line)
            if address_display:
                doc.set("address_display", address_display)

        if hasattr(doc, "content"):
            doc.set("content", cls.build_content_from_party(doc, party_doc))

        return cls.apply_defaults(doc)

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
                "options": [],
            }

            if field.fieldtype == "Select":
                field_data["options"] = cls.get_select_options(field.options)
            elif field.fieldtype == "Link":
                field_data["options"] = cls.get_link_options(field.options, current_value=doc.get(fieldname))
                field_data["link_doctype"] = field.options
            elif field.fieldtype == "Dynamic Link":
                field_data["options"] = cls.get_dynamic_link_options(doc, field)
                field_data["link_doctype_field"] = field.options
                field_data["link_doctype"] = doc.get(field.options)

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
        writable_fields = OpportunityUtils.get_writable_fields(meta)

        for fieldname, value in payload.items():
            if fieldname in writable_fields:
                doc.set(fieldname, value)

        return OpportunityUtils.apply_defaults(doc)
