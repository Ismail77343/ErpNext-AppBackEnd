# Mobile API - توثيق العمل الكامل

## 📋 نظرة عامة على التطبيق

هذا التطبيق يوفر واجهة برمجية (API) متكاملة للتطبيقات الجوالة، مع تطبيق **Clean Architecture** لضمان كود منظم وقابل للصيانة.

---

## 🏗️ بنية التطبيق

```
mobile_api/
├── api.py                          # نقطة الدخول الرئيسية
├── handlers/                       # طبقة معالجة الطلبات
│   ├── auth_handler.py
│   ├── project_handler.py
│   ├── task_handler.py
│   └── material_request_handler.py
├── services/                       # طبقة منطق العمل
│   ├── auth_service.py
│   ├── project_service.py
│   ├── task_service.py
│   └── material_request_service.py
├── repositories/                   # طبقة الوصول للبيانات
│   ├── project_repository.py
│   ├── task_repository.py
│   └── material_request_repository.py
└── utils/                          # أدوات مساعدة
    └── task_utils.py
```

---

## 🔗 قائمة جميع API Endpoints

### 1️⃣ المصادقة والمستخدمين

#### `POST /api/resource/mobile_api/login`

**الوصف**: تسجيل دخول المستخدم

**نوع الطلب**: POST

**المعاملات** (Parameters):
| المعامل | النوع | إلزامي | الوصف |
|--------|------|--------|-------|
| email | string | ✅ | بريد المستخدم الإلكتروني |
| password | string | ✅ | كلمة المرور |

**مثال على الطلب**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**الرد الناجح** (200):
```json
{
  "status": "success",
  "user": "أحمد علي",
  "email": "user@example.com",
  "roles": ["User", "Employee"]
}
```

**الرد عند الفشل** (401):
```json
{
  "status": "error",
  "message": "بيانات دخول غير صحيحة"
}
```

---

### 2️⃣ المشاريع

#### `GET /api/resource/mobile_api/get_projects`

**الوصف**: الحصول على جميع المشاريع النشطة

**نوع الطلب**: GET

**المعاملات**: بدون معاملات

**الرد الناجح** (200):
```json
[
  {
    "name": "PRJ-001",
    "project_name": "مشروع التطوير",
    "status": "In Progress"
  },
  {
    "name": "PRJ-002",
    "project_name": "مشروع الصيانة",
    "status": "Planning"
  }
]
```

---

#### `GET /api/resource/mobile_api/get_my_projects`

**الوصف**: الحصول على مشاريعي مع دعم التقسيم (Pagination)

**نوع الطلب**: GET

**المعاملات** (Parameters):
| المعامل | النوع | إلزامي | الافتراضي | الوصف |
|--------|------|--------|----------|-------|
| limit_start | integer | ❌ | 0 | رقم الصف الأول |
| limit_page_length | integer | ❌ | 20 | عدد الصفوف في الصفحة |

**مثال على الطلب**:
```
GET /api/resource/mobile_api/get_my_projects?limit_start=0&limit_page_length=10
```

**الرد الناجح** (200):
```json
[
  {
    "name": "PRJ-001",
    "project_name": "مشروع التطوير",
    "status": "In Progress",
    "customer": "شركة النجاح",
    "percent_complete": 45
  },
  {
    "name": "PRJ-002",
    "project_name": "مشروع الصيانة",
    "status": "Planning",
    "customer": "شركة الرائد",
    "percent_complete": 10
  }
]
```

---

#### `GET /api/resource/mobile_api/get_project_details`

**الوصف**: الحصول على تفاصيل المشروع كاملة مع جميع المهام

**نوع الطلب**: GET

**المعاملات** (Parameters):
| المعامل | النوع | إلزامي | الوصف |
|--------|------|--------|-------|
| project_name | string | ✅ | اسم المشروع |

**مثال على الطلب**:
```
GET /api/resource/mobile_api/get_project_details?project_name=PRJ-001
```

**الرد الناجح** (200):
```json
{
  "name": "PRJ-001",
  "project_name": "مشروع التطوير",
  "status": "In Progress",
  "customer": "شركة النجاح",
  "percent_complete": 45,
  "description": "مشروع تطوير البرنامج",
  "tasks": [
    {
      "name": "TASK-001",
      "subject": "تصميم الواجهات",
      "status": "In Progress",
      "priority": "High",
      "progress": 60,
      "exp_start_date": "2025-01-01",
      "exp_end_date": "2025-02-15"
    },
    {
      "name": "TASK-002",
      "subject": "التطوير الخلفي",
      "status": "Open",
      "priority": "High",
      "progress": 30,
      "exp_start_date": "2025-01-15",
      "exp_end_date": "2025-03-31"
    }
  ]
}
```

---

### 3️⃣ المهام

#### `GET /api/resource/mobile_api/get_task_details`

**الوصف**: الحصول على تفاصيل المهمة كاملة مع المتابعات والأنشطة

**نوع الطلب**: GET

**المعاملات** (Parameters):
| المعامل | النوع | إلزامي | الوصف |
|--------|------|--------|-------|
| task_name | string | ✅ | اسم المهمة |

**مثال على الطلب**:
```
GET /api/resource/mobile_api/get_task_details?task_name=TASK-001
```

**الرد الناجح** (200):
```json
{
  "name": "TASK-001",
  "subject": "تصميم الواجهات",
  "status": "In Progress",
  "priority": "High",
  "progress": 60,
  "exp_start_date": "2025-01-01",
  "exp_end_date": "2025-02-15",
  "child_follow": [
    {
      "date_follow": "2025-02-20",
      "time_follow": "14:30",
      "date_time_registration": "2025-02-20 14:35:22",
      "follow_up": "تم إكمال التصميمات الأولية",
      "progress": 60,
      "file": ""
    }
  ],
  "activity_log": [
    {
      "name": "COM-001",
      "comment_by": "أحمد علي",
      "creation": "2025-02-20 14:35:22",
      "content": "تم تحديث التصميمات"
    }
  ]
}
```

---

#### `POST /api/resource/mobile_api/add_follow_up`

**الوصف**: إضافة متابعة جديدة للمهمة

**نوع الطلب**: POST

**المعاملات** (Parameters):
| المعامل | النوع | إلزامي | الوصف |
|--------|------|--------|-------|
| task_name | string | ✅ | اسم المهمة |
| date_follow | string | ✅ | تاريخ المتابعة (YYYY-MM-DD) |
| time_follow | string | ❌ | وقت المتابعة (HH:MM) |
| progress | integer | ❌ | نسبة التقدم (0-100) |
| follow_up | string | ✅ | ملاحظات المتابعة |
| attachment | string | ❌ | المرفقات (File ID) |

**مثال على الطلب**:
```json
{
  "task_name": "TASK-001",
  "date_follow": "2025-02-25",
  "time_follow": "15:00",
  "progress": 75,
  "follow_up": "تم إكمال معظم التصميمات، بقي التعديلات النهائية",
  "attachment": ""
}
```

**الرد الناجح** (200):
```json
{
  "status": "success",
  "message": "تم إضافة المتابعة بنجاح",
  "task_name": "TASK-001",
  "progress": 75
}
```

**الرد عند الفشل** (400):
```json
{
  "status": "error",
  "message": "يجب ملء الحقول المطلوبة: task_name, date_follow, follow_up"
}
```

---

#### `POST /api/resource/mobile_api/update_task_status`

**الوصف**: تحديث حالة المهمة

**نوع الطلب**: POST

**المعاملات** (Parameters):
| المعامل | النوع | إلزامي | الوصف |
|--------|------|--------|-------|
| task_name | string | ✅ | اسم المهمة |
| status | string | ✅ | الحالة الجديدة (Open, In Progress, Closed, etc) |

**مثال على الطلب**:
```json
{
  "task_name": "TASK-001",
  "status": "Closed"
}
```

**الرد الناجح** (200):
```json
{
  "status": "success",
  "message": "تم تحديث حالة المهمة إلى Closed",
  "task_name": "TASK-001",
  "current_status": "Closed"
}
```

---

### 4️⃣ طلبات المواد

#### `POST /api/resource/mobile_api/create_material_request`

**الوصف**: إنشاء طلب مادة جديد للمشروع

**نوع الطلب**: POST

**المعاملات** (Parameters):
| المعامل | النوع | إلزامي | الوصف |
|--------|------|--------|-------|
| project | string | ✅ | اسم المشروع |
| items | array | ✅ | قائمة المواد المطلوبة |

**مثال على الطلب**:
```json
{
  "project": "PRJ-001",
  "items": [
    {
      "item_code": "ITEM-001",
      "qty": 10,
      "uom": "Unit"
    },
    {
      "item_code": "ITEM-002",
      "qty": 5,
      "uom": "Set"
    }
  ]
}
```

**الرد الناجح** (200):
```json
{
  "status": "success",
  "message": "تم إنشاء طلب المادة بنجاح",
  "request_name": "MR-2025-00001"
}
```

**الرد عند الفشل** (400):
```json
{
  "status": "error",
  "message": "المشروع غير موجود"
}
```

---

## 📱 أمثلة على الاستخدام من Flutter

### مثال 1: تسجيل الدخول

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<Map<String, dynamic>> login(String email, String password) async {
  final response = await http.post(
    Uri.parse('http://your-domain/api/resource/mobile_api/login'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'email': email,
      'password': password,
    }),
  );
  
  if (response.statusCode == 200) {
    return jsonDecode(response.body);
  } else {
    throw Exception('فشل تسجيل الدخول');
  }
}
```

### مثال 2: الحصول على المشاريع

```dart
Future<List<dynamic>> getMyProjects({int page = 0, int pageSize = 10}) async {
  final response = await http.get(
    Uri.parse(
      'http://your-domain/api/resource/mobile_api/get_my_projects'
      '?limit_start=${page * pageSize}&limit_page_length=$pageSize'
    ),
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $authToken',
    },
  );
  
  if (response.statusCode == 200) {
    return jsonDecode(response.body);
  } else {
    throw Exception('فشل جلب المشاريع');
  }
}
```

### مثال 3: إضافة متابعة

```dart
Future<Map<String, dynamic>> addFollowUp({
  required String taskName,
  required String dateFollow,
  required String followUp,
  int progress = 0,
  String? timeFollow,
}) async {
  final response = await http.post(
    Uri.parse('http://your-domain/api/resource/mobile_api/add_follow_up'),
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $authToken',
    },
    body: jsonEncode({
      'task_name': taskName,
      'date_follow': dateFollow,
      'time_follow': timeFollow,
      'progress': progress,
      'follow_up': followUp,
    }),
  );
  
  if (response.statusCode == 200) {
    return jsonDecode(response.body);
  } else {
    throw Exception('فشل إضافة المتابعة');
  }
}
```

---

## 🛡️ معايير الأمان

1. **المصادقة**: يتم استخدام نظام مصادقة Frappe
2. **التفويض**: يتم فحص صلاحيات المستخدم على كل endpoint
3. **معالجة الأخطاء**: يتم تسجيل جميع الأخطاء للمراجعة

---

## 📊 أكواد الحالة HTTP

| الكود | الوصف |
|------|-------|
| 200 | نجاح العملية |
| 400 | خطأ في المعاملات |
| 401 | المستخدم غير مصرح |
| 404 | المورد غير موجود |
| 500 | خطأ في الخادم |

---

## 🔄 تدفق البيانات (Flow)

```
Request من Client
    ↓
Handler (معالج الطلب)
    ↓
Service (منطق العمل)
    ↓
Repository (الوصول للبيانات)
    ↓
Database (قاعدة البيانات)
    ↓
Response للعميل
```

---

## ⚙️ كيفية إضافة Endpoint جديد

1. **إنشاء Handler** في `handlers/`
2. **إنشاء Service** في `services/`
3. **إنشاء Repository** (إذا لزم الأمر) في `repositories/`
4. **استيراد في `api.py`**

---

## 📝 ملاحظات مهمة

- جميع الطلبات يجب أن تحتوي على `Content-Type: application/json`
- جميع التواريخ بصيغة `YYYY-MM-DD`
- جميع الأوقات بصيغة `HH:MM`
- نسبة التقدم يجب أن تكون بين 0 و 100

---

## 📧 التواصل والدعم

للمزيد من المعلومات، يرجى التواصل مع فريق التطوير.
