# Lead API Documentation

## Clean Architecture

جزء `Lead` في `mobile_api` أصبح مقسمًا كالتالي:

```text
mobile_api/
├── handlers/lead_handler.py
├── services/lead_service.py
├── repositories/lead_repository.py
├── documents/lead_document.py
└── utils/lead_utils.py
```

- `handler`: يستقبل الطلب ويرجع response مناسب.
- `service`: منطق العمل.
- `repository`: التعامل مع قاعدة البيانات.
- `document`: بناء شكل response الخاص بالـ Lead.
- `utils`: التحقق من الحقول الإلزامية ومعالجة payload.

Frontend plain text document:

- `LEAD_DOCUMENT_API.txt`

## Endpoints

### 1. Get Leads List

`GET /api/method/mobile_api.api.get_leads`

المعاملات الاختيارية:
- `limit_start`
- `limit_page_length`
- `status`
- `search`

مثال:

`GET /api/method/mobile_api.api.get_leads?limit_start=0&limit_page_length=20&status=Lead&search=CRM`

يرجع قائمة الـ Leads مرتبة حسب آخر تعديل.

### 2. Get Lead Details

`GET /api/method/mobile_api.api.get_lead_details?lead_name=CRM-LEAD-.2026.-00001`

يرجع بيانات الـ Lead مع المتابعات وسجل النشاط.

### 3. Get Lead Required Fields

`POST /api/method/mobile_api.api.get_lead_required_fields`

مثال:

```json
{
  "data": {
    "source": "Existing Customer",
    "first_name": "Ali"
  }
}
```

يرجع:
- `required_fields`
- `missing_fields`

بحسب الـ Customize Form الحالي.

### 4. Create Lead

`POST /api/method/mobile_api.api.create_lead`

مثال:

```json
{
  "data": {
    "first_name": "Ali",
    "mobile_no": "0500000000",
    "email_id": "ali@test.com"
  }
}
```

### 5. Update Lead

`POST /api/method/mobile_api.api.update_lead`

مثال:

```json
{
  "lead_name": "CRM-LEAD-.2026.-00001",
  "data": {
    "status": "Opportunity",
    "company_name": "Test Company"
  }
}
```

### 6. Add Lead Follow Up

`POST /api/method/mobile_api.api.add_lead_follow_up`

مثال:

```json
{
  "lead_name": "CRM-LEAD-.2026.-00001",
  "follow_up_date": "2026-03-24",
  "expected_result_date": "2026-03-30",
  "details": "تم الاتصال بالعميل وينتظر العرض",
  "attachment": "/files/lead-follow.pdf"
}
```

يضيف صفًا في جدول `mobile_api_follow_ups` ويحدّث:
- `mobile_api_last_update_date`
- `mobile_api_next_follow_up_date`
- `mobile_api_last_follow_up_report`

### 7. Get Lead Follow Ups

`GET /api/method/mobile_api.api.get_lead_follow_ups?lead_name=CRM-LEAD-.2026.-00001`

يرجع فقط قائمة المتابعات الخاصة بالـ Lead.
