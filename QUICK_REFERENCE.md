# ⚡ Quick Reference Guide

## 🚀 البدء السريع

### 1. تسجيل الدخول
```bash
curl -X POST http://localhost:8000/api/resource/mobile_api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com", "password":"pass123"}'
```

### 2. الحصول على المشاريع
```bash
curl -X GET "http://localhost:8000/api/resource/mobile_api/get_my_projects?limit_start=0&limit_page_length=10" \
  -H "Authorization: Bearer TOKEN"
```

### 3. الحصول على تفاصيل مشروع
```bash
curl -X GET "http://localhost:8000/api/resource/mobile_api/get_project_details?project_name=PRJ-001" \
  -H "Authorization: Bearer TOKEN"
```

---

## 📋 جميع الـ Endpoints

| الطريقة | الـ URL | الوصف |
|--------|--------|-------|
| POST | `/api/resource/mobile_api/login` | تسجيل دخول |
| GET | `/api/resource/mobile_api/get_projects` | جميع المشاريع |
| GET | `/api/resource/mobile_api/get_my_projects` | مشاريعي (مع Pagination) |
| GET | `/api/resource/mobile_api/get_project_details` | تفاصيل المشروع |
| GET | `/api/resource/mobile_api/get_task_details` | تفاصيل المهمة |
| POST | `/api/resource/mobile_api/add_follow_up` | إضافة متابعة |
| POST | `/api/resource/mobile_api/update_task_status` | تحديث حالة المهمة |
| POST | `/api/resource/mobile_api/create_material_request` | إنشاء طلب مادة |

---

## 🔑 المعاملات الأساسية

### `add_follow_up` - إضافة متابعة
```
task_name* | date_follow* | follow_up* | time_follow | progress | attachment
```

### `update_task_status` - تحديث الحالة
```
task_name* | status*
```

### `get_my_projects` - المشاريع (Pagination)
```
limit_start | limit_page_length (الافتراضي: 20)
```

---

## 🏗️ هيكل المشروع

```
api.py (نقطة الدخول)
├── handlers (المعالجات)
├── services (منطق العمل)
├── repositories (قاعدة البيانات)
└── utils (أدوات مساعدة)
```

---

## 📂 أين تجد ماذا

| أريد أن | ابحث في |
|--------|---------|
| أرى جميع الـ endpoints | `api.py` |
| أفهم كيفية تسجيل دخول | `handlers/auth_handler.py` |
| أضيف منطق جديد | `services/` |
| أستدعي قاعدة البيانات | `repositories/` |
| أستخدم دوال مساعدة | `utils/` |

---

## 💻 أمثلة الكود

### Handler
```python
@frappe.whitelist()
def get_projects():
    try:
        projects = ProjectService.get_all_projects()
        return projects
    except Exception as e:
        return {"status": "error"}
```

### Service
```python
class ProjectService:
    @staticmethod
    def get_all_projects():
        return ProjectRepository.get_all_active_projects()
```

### Repository
```python
class ProjectRepository:
    @staticmethod
    def get_all_active_projects():
        return frappe.get_list("Project", filters={"status": ["!=", "Completed"]})
```

---

## ✅ قائمة تحقق قبل الـ Commit

- [ ] تم اتباع بنية Clean Architecture
- [ ] التحقق من المدخلات
- [ ] معالجة الأخطاء
- [ ] حفظ الأخطاء في Log
- [ ] توثيق الكود (Docstrings)
- [ ] تحديث `API_DOCUMENTATION.md`
- [ ] اختبار الـ Endpoint

---

## 🐛 الأخطاء الشائعة

| الخطأ | الحل |
|------|-----|
| 401 Unauthorized | تحقق من التوكن (Token) |
| 404 Not Found | تحقق من اسم المورد |
| 400 Bad Request | تحقق من المعاملات |
| 500 Server Error | انظر إلى اللوجات |

---

## 🔍 Debugging

### عرض الأخطاء
```bash
# في Terminal
frappe logs live

# في قاعدة البيانات
SELECT * FROM `tabError Log` LIMIT 10;
```

### طباعة في الكود
```python
frappe.log_error(frappe.get_traceback(), "function_name")
```

---

## 📚 الملفات الرئيسية للقراءة

1. 📖 `API_DOCUMENTATION.md` - كل الـ endpoints
2. 🏗️ `ARCHITECTURE.md` - شرح البنية
3. 📂 `FILE_STRUCTURE.md` - شرح الملفات

---

## 🎯 الخطوات السريعة لإضافة Endpoint

1. أنشئ Handler في `handlers/`
2. أنشئ Service في `services/`
3. استدعِ Repository إذا لزم
4. استورد في `api.py`
5. وثّق في `API_DOCUMENTATION.md`

---

## 📞 معلومات سريعة

- **سيرفر المحلي**: http://localhost:8000
- **Base URL**: /api/resource/mobile_api/
- **Authentication**: Token-based
- **Format**: JSON

---

## ⏱️ الأوقات المتوقعة

| المهمة | الوقت |
|------|------|
| إضافة Endpoint جديد | 30 دقيقة |
| إصلاح Bug | 15 دقيقة |
| مراجعة الكود | 20 دقيقة |
| اختبار الـ API | 10 دقائق |

---

## 🔗 الروابط المفيدة

- [Frappe Documentation](https://frappeframework.com/)
- [REST API Best Practices](https://restfulapi.net/)
- [Clean Code](https://www.oreilly.com/library/view/clean-code)

---

**آخر تحديث**: 25 فبراير 2025
