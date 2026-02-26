# Mobile API - Clean Architecture Implementation

## 📖 نظرة عامة

تم إعادة تنظيم تطبيق Mobile API بناءً على مبادئ **Clean Architecture** لضمان كود منظم وقابل للصيانة والاختبار.

---

## 🗂️ هيكل المشروع

```
mobile_api/
│
├── api.py                              # Entry Point فقط (استيراد الـ Handlers)
│
├── handlers/                           # الطبقة الأولى: معالجة الطلبات
│   ├── __init__.py
│   ├── auth_handler.py                # معالج المصادقة
│   ├── project_handler.py             # معالج المشاريع
│   ├── task_handler.py                # معالج المهام
│   └── material_request_handler.py    # معالج طلبات المواد
│
├── services/                           # الطبقة الثانية: منطق العمل
│   ├── __init__.py
│   ├── auth_service.py                # خدمة المصادقة
│   ├── project_service.py             # خدمة المشاريع
│   ├── task_service.py                # خدمة المهام
│   └── material_request_service.py    # خدمة طلبات المواد
│
├── repositories/                       # الطبقة الثالثة: الوصول للبيانات
│   ├── __init__.py
│   ├── project_repository.py          # مستودع المشاريع
│   ├── task_repository.py             # مستودع المهام
│   └── material_request_repository.py # مستودع طلبات المواد
│
├── utils/                              # أدوات مساعدة
│   ├── __init__.py
│   └── task_utils.py                  # أدوات المهام
│
├── API_DOCUMENTATION.md               # توثيق الـ API
└── README.md                          # هذا الملف
```

---

## 🏗️ الطبقات الأربع

### 1️⃣ **Handlers Layer** (طبقة المعالجات)

**الوظيفة**: معالجة الطلبات من العميل

**الخصائص**:
- تحتوي على `@frappe.whitelist()` decorators
- تمرر البيانات إلى Service Layer
- تتعامل مع المعاملات الأساسية

**مثال**:
```python
@frappe.whitelist()
def get_projects():
    try:
        projects = ProjectService.get_all_projects()
        return projects
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_projects")
        return {"status": "error", "message": str(e)}
```

---

### 2️⃣ **Services Layer** (طبقة الخدمات)

**الوظيفة**: تطبيق منطق العمل الرئيسي

**الخصائص**:
- تحتوي على كل منطق التطبيق
- تستدعي Repository Layer للبيانات
- تستخدم Utilities للعمليات المساعدة
- لا تحتوي على decorators Frappe

**مثال**:
```python
class TaskService:
    @staticmethod
    def add_follow_up(task_name, date_follow, ...):
        # التحقق من الإدخال
        validation = TaskUtils.validate_follow_up_input(...)
        if validation["status"] == "error":
            return validation
        
        # جلب البيانات
        task = TaskRepository.get_task(task_name)
        
        # معالجة المنطق
        progress_value = TaskUtils.parse_progress(progress)
        TaskRepository.add_follow_up_row(...)
        
        return {"status": "success"}
```

---

### 3️⃣ **Repositories Layer** (طبقة الوصول للبيانات)

**الوظيفة**: التواصل مع قاعدة البيانات

**الخصائص**:
- تحتوي على جميع استدعاءات Frappe للبيانات
- توفر واجهة نظيفة للـ Service Layer
- معزولة عن منطق العمل

**مثال**:
```python
class TaskRepository:
    @staticmethod
    def get_task(task_name):
        return frappe.get_doc("Task", task_name)
    
    @staticmethod
    def add_follow_up_row(task, date_follow, ...):
        if hasattr(task, 'child_follow'):
            task.append('child_follow', {...})
```

---

### 4️⃣ **Utils Layer** (طبقة الأدوات المساعدة)

**الوظيفة**: توفير دوال مساعدة وعودية

**الخصائص**:
- دوال ثابتة (Static Methods)
- قابلة لإعادة الاستخدام
- لا تعتمد على Frappe مباشرة

**مثال**:
```python
class TaskUtils:
    @staticmethod
    def parse_progress(progress):
        if not progress:
            return 0
        try:
            return max(0, min(100, int(progress)))
        except (ValueError, TypeError):
            return 0
```

---

## 🔄 تدفق البيانات

### عند طلب الحصول على المهام:

```
1. Flutter/Mobile App يرسل طلب GET
        ↓
2. get_task_details() في Handler
        ↓
3. TaskService.get_task_with_followers()
        ↓
4. TaskRepository.get_task() + TaskRepository.get_child_follow()
        ↓
5. frappe.get_doc("Task", ...) + frappe.get_list("Comment", ...)
        ↓
6. إرجاع البيانات من Database
        ↓
7. Service تنسق البيانات
        ↓
8. Handler ترجع النتيجة
        ↓
9. JSON Response للعميل
```

---

## ✅ مزايا Clean Architecture

| المزايا | الشرح |
|-------|--------|
| **Separation of Concerns** | كل طبقة لديها مسؤولية واحدة محددة |
| **Testability** | يمكن اختبار كل طبقة بشكل منفصل |
| **Maintainability** | يسهل البحث عن الأخطاء وتصحيحها |
| **Scalability** | يمكن إضافة ميزات جديدة بسهولة |
| **Reusability** | إعادة استخدام الكود في أماكن أخرى |
| **Flexibility** | يمكن تغيير التفاصيل دون التأثير على الطبقات الأخرى |

---

## 🚀 كيفية إضافة Endpoint جديد

### مثال: إضافة Endpoint لحذف مهمة

**1. إنشاء Handler** (`handlers/task_handler.py`):
```python
@frappe.whitelist()
def delete_task(task_name):
    try:
        result = TaskService.delete_task(task_name)
        return result
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "delete_task")
        return {"status": "error", "message": str(e)}
```

**2. إضافة Service** (`services/task_service.py`):
```python
@staticmethod
def delete_task(task_name):
    if not TaskRepository.task_exists(task_name):
        return {
            "status": "error",
            "message": f"المهمة {task_name} غير موجودة"
        }
    
    task = TaskRepository.get_task(task_name)
    task.delete()
    frappe.db.commit()
    
    return {
        "status": "success",
        "message": "تم حذف المهمة بنجاح"
    }
```

**3. إضافة Repository Method** (`repositories/task_repository.py`):
```python
@staticmethod
def delete_task(task):
    task.delete()
```

**4. استيراد في `api.py`**:
```python
from mobile_api.handlers.task_handler import (
    ...
    delete_task
)

__all__ = [
    ...
    'delete_task'
]
```

**5. تحديث التوثيق** (`API_DOCUMENTATION.md`)

---

## 📊 أمثلة على الاستخدام

### مثال 1: الحصول على المشروع والمهام

```python
# في Mobile App
response = get_project_details(project_name="PRJ-001")

# التدفق الداخلي:
# 1. Handler: get_project_details() يستدعي ProjectService
# 2. Service: تجمع بيانات المشروع والمهام
# 3. Repository: تستدعي Frappe للبيانات
# 4. Database: ترد البيانات
# 5. النتيجة: مشروع كامل مع المهام
```

### مثال 2: إضافة متابعة

```python
# في Mobile App
response = add_follow_up(
    task_name="TASK-001",
    date_follow="2025-02-25",
    progress=80,
    follow_up="تم إكمال 80% من المهمة"
)

# التدفق الداخلي:
# 1. Handler: يتحقق من الطلب
# 2. Service: تتحقق والتخطيط
# 3. Utils: تحول Progress إلى رقم صحيح
# 4. Repository: تضيف الصف وتحفظ
# 5. النتيجة: رسالة نجاح
```

---

## 🧪 اختبار الـ API

### استخدام cURL

```bash
# تسجيل الدخول
curl -X POST http://localhost:8000/api/resource/mobile_api/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password"
  }'

# الحصول على المشاريع
curl -X GET "http://localhost:8000/api/resource/mobile_api/get_my_projects?limit_start=0&limit_page_length=10" \
  -H "Authorization: Bearer TOKEN"
```

### استخدام Postman

1. استيراد URLs من `API_DOCUMENTATION.md`
2. تعيين المتغيرات (base_url, token)
3. اختبار كل endpoint

---

## 📝 معايير الكود

- ✅ كل function لديها docstring
- ✅ استخدام Type Hints (اختياري لـ Python)
- ✅ معالجة الأخطاء في كل مكان
- ✅ تسجيل الأخطاء في Frappe
- ✅ فصل الاهتمامات

---

## 🔍 Debugging

### كيفية تتبع الأخطاء

1. **في Frappe Console**:
   ```
   frappe logs live
   ```

2. **في الكود**:
   ```python
   frappe.log_error(frappe.get_traceback(), "function_name")
   ```

3. **في قاعدة البيانات**:
   ```sql
   SELECT * FROM `tabError Log` 
   WHERE name LIKE '%function_name%'
   ORDER BY creation DESC;
   ```

---

## 📚 المراجع

- [Clean Architecture Book](https://www.oreilly.com/library/view/clean-architecture/9780134494272/)
- [Frappe Documentation](https://frappeframework.com/)
- [RESTful API Best Practices](https://restfulapi.net/)

---

## 🤝 المساهمة

عند إضافة ميزات جديدة:

1. اتبع نفس البنية (Handler → Service → Repository)
2. أضف التوثيق
3. اختبر الـ Endpoint
4. حدّث `API_DOCUMENTATION.md`

---

## 📧 التواصل

للمزيد من الاستفسارات، يرجى التواصل مع فريق التطوير.
