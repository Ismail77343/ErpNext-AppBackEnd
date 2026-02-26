# 📂 شرح الملفات والمجلدات

## 🔝 الملفات الرئيسية

### `api.py`
- **الغرض**: نقطة الدخول الرئيسية للـ API
- **المحتوى**: استيراد جميع الـ endpoints من Handlers
- **مثال**:
  ```python
  from mobile_api.handlers.auth_handler import login
  from mobile_api.handlers.project_handler import get_projects
  ```

### `API_DOCUMENTATION.md` 📖
- **الغرض**: توثيق كامل للـ API
- **يحتوي على**:
  - قائمة جميع Endpoints
  - معاملات وأمثلة كل endpoint
  - أكواد الأخطاء
  - أمثلة Flutter
  - معايير الأمان

### `ARCHITECTURE.md` 🏗️
- **الغرض**: شرح بنية Clean Architecture
- **يحتوي على**:
  - هيكل المجلدات
  - شرح كل طبقة
  - تدفق البيانات
  - كيفية إضافة endpoints جديدة
  - أمثلة عملية

### `FILE_STRUCTURE.md` 📋
- **الغرض**: شرح ملخص الملفات (هذا الملف)

---

## 📁 المجلدات

### `handlers/` - معالجات الطلبات

| الملف | الوصف |
|------|--------|
| `auth_handler.py` | معالج تسجيل دخول المستخدمين |
| `project_handler.py` | معالج جميع عمليات المشاريع |
| `task_handler.py` | معالج جميع عمليات المهام |
| `material_request_handler.py` | معالج طلبات المواد |

**الخصائص**:
- تحتوي على `@frappe.whitelist()` decorators
- معالجة الأخطاء الأساسية
- تمرير البيانات للـ Services

**مثال**:
```python
@frappe.whitelist()
def get_projects():
    try:
        projects = ProjectService.get_all_projects()
        return projects
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

---

### `services/` - منطق العمل

| الملف | الوصف |
|------|--------|
| `auth_service.py` | خدمة المصادقة والمستخدمين |
| `project_service.py` | خدمة المشاريع وعملياتها |
| `task_service.py` | خدمة المهام والمتابعات |
| `material_request_service.py` | خدمة طلبات المواد |

**الخصائص**:
- تطبيق منطق العمل الرئيسي
- استدعاء Repository Layer للبيانات
- استخدام Utilities للعمليات المساعدة

**مثال**:
```python
class ProjectService:
    @staticmethod
    def get_project_with_tasks(project_name):
        project = ProjectRepository.get_project(project_name)
        tasks = ProjectRepository.get_project_tasks(project_name)
        return {"project": project, "tasks": tasks}
```

---

### `repositories/` - الوصول للبيانات

| الملف | الوصف |
|------|--------|
| `project_repository.py` | جميع عمليات الوصول لبيانات المشاريع |
| `task_repository.py` | جميع عمليات الوصول لبيانات المهام |
| `material_request_repository.py` | جميع عمليات الوصول لطلبات المواد |

**الخصائص**:
- احتواء جميع استدعاءات Frappe
- توفير واجهة نظيفة
- عزل قاعدة البيانات

**مثال**:
```python
class ProjectRepository:
    @staticmethod
    def get_all_projects():
        return frappe.get_list("Project", fields=["name", "status"])
    
    @staticmethod
    def get_project_tasks(project_name):
        return frappe.get_list(
            "Task",
            filters={"project": project_name},
            fields=["name", "subject", "status"]
        )
```

---

### `utils/` - الأدوات المساعدة

| الملف | الوصف |
|------|--------|
| `task_utils.py` | أدوات ومساعدات للمهام |

**الدوال الرئيسية**:
- `validate_follow_up_input()`: التحقق من صحة المدخلات
- `parse_progress()`: تحويل Progress إلى رقم (0-100)
- `generate_summary()`: توليد ملخص التحديث
- `generate_log_follow()`: توليد سجل المتابعات

**مثال**:
```python
class TaskUtils:
    @staticmethod
    def parse_progress(progress):
        if not progress:
            return 0
        try:
            return max(0, min(100, int(progress)))
        except:
            return 0
```

---

## 🔗 العلاقات بين الملفات

```
handlers/auth_handler.py
        ↓
services/auth_service.py
        ↓
repositories/ (إن لزم)
        ↓
Frappe Framework / Database
```

### مثال عملي:

```
handlers/task_handler.py::get_task_details()
        ↓
services/task_service.py::TaskService.get_task_with_followers()
        ↓
repositories/task_repository.py::TaskRepository.get_task()
        ↓
frappe.get_doc("Task", task_name)
        ↓
قاعدة البيانات
```

---

## 📊 خريطة الـ API Endpoints

### المصادقة
- `POST /api/resource/mobile_api/login` → `handlers/auth_handler.py`

### المشاريع
- `GET /api/resource/mobile_api/get_projects` → `handlers/project_handler.py`
- `GET /api/resource/mobile_api/get_my_projects` → `handlers/project_handler.py`
- `GET /api/resource/mobile_api/get_project_details` → `handlers/project_handler.py`

### المهام
- `GET /api/resource/mobile_api/get_task_details` → `handlers/task_handler.py`
- `POST /api/resource/mobile_api/add_follow_up` → `handlers/task_handler.py`
- `POST /api/resource/mobile_api/update_task_status` → `handlers/task_handler.py`

### طلبات المواد
- `POST /api/resource/mobile_api/create_material_request` → `handlers/material_request_handler.py`

---

## 🔍 كيفية الملاحة في الكود

### للبحث عن منطق معين:

1. **ابدأ من `api.py`** لمعرفة جميع الـ endpoints
2. **اذهب إلى Handler المناسب** (مثل `task_handler.py`)
3. **اتبع الاستدعاء إلى Service** (مثل `task_service.py`)
4. **انظر إلى Repository** إذا لزم الأمر
5. **استخدم Utils** للعمليات المساعدة

### مثال:
- أريد أن أفهم كيفية إضافة متابعة؟
  - `api.py` → `handlers/task_handler.py::add_follow_up()`
  - حيث يستدعي `services/task_service.py::TaskService.add_follow_up()`
  - التي تستدعي `repositories/task_repository.py` و `utils/task_utils.py`

---

## 🚀 إضافة ملف جديد

### خطوات إضافة خدمة جديدة (مثلاً Leave Request):

1. **إنشاء Handler**:
   ```
   handlers/leave_handler.py
   ```

2. **إنشاء Service**:
   ```
   services/leave_service.py
   ```

3. **إنشاء Repository** (إن لزم):
   ```
   repositories/leave_repository.py
   ```

4. **استيراد في `api.py`**:
   ```python
   from mobile_api.handlers.leave_handler import create_leave_request
   ```

5. **تحديث الوثائق**:
   - `API_DOCUMENTATION.md`
   - `ARCHITECTURE.md`
   - `FILE_STRUCTURE.md`

---

## 📝 معايير الملفات

### اسم الملف
- استخدم snake_case: `auth_handler.py` ✅
- استخدم اسم معبر: `leave_request_service.py` ✅

### محتوى الملف
- ابدأ بـ docstring للفئة
- أضف docstrings لكل دالة
- استخدم Type Hints (اختياري)
- معالجة الأخطاء إلزامية

### الترتيب
```python
import statements
↓
Docstring for module
↓
Class definition
↓
@staticmethod methods
```

---

## ⚠️ الأخطاء الشائعة

❌ **لا تفعل**:
```python
# وضع كل شيء في api.py
# وضع Frappe logic مباشرة في Handler
# عدم التحقق من المدخلات
# عدم حفظ الأخطاء في log
```

✅ **افعل**:
```python
# فصل Concerns
# استخدام Service للمنطق
# التحقق في Utils
# حفظ الأخطاء دائماً
```

---

## 🔗 الملفات الذي قد تحتاج إليها

| الملف | التحديث عند |
|------|-------------|
| `API_DOCUMENTATION.md` | إضافة endpoint جديد |
| `ARCHITECTURE.md` | تغيير البنية |
| `FILE_STRUCTURE.md` | إضافة ملف جديد |
| `handlers/` | إضافة معالج جديد |
| `services/` | إضافة منطق أعمال جديد |
| `repositories/` | إضافة استدعاء database جديد |
| `utils/` | إضافة دوال مساعدة جديدة |

---

💡 **نصيحة**: اقرأ هذه الملفات الثلاثة معاً:
1. `API_DOCUMENTATION.md` - كيف تستخدم API
2. `ARCHITECTURE.md` - كيف يعمل الكود
3. `FILE_STRUCTURE.md` - أين تجد ماذا (هذا الملف)
