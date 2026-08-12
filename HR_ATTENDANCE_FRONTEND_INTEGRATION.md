# HR Attendance Flutter Mobile Integration

This document explains how a Flutter mobile app should integrate with the HR attendance features added to the `mobile_api` app.

Use this as the implementation reference for the mobile developer.

## Backend Base URL

Replace the host with the real ERPNext site URL.

```text
https://your-erp-domain.com
```

For local testing:

```text
http://192.168.100.107:8000
```

All Frappe RPC endpoints use this pattern:

```text
POST {BASE_URL}/api/method/{METHOD_PATH}
```

Example:

```text
POST https://your-erp-domain.com/api/method/mobile_api.api.get_hr_attendance_context
```

The backend is already prepared with:

- `Mobile HR Attendance Settings`
- `Mobile HR Attendance Location`
- `Mobile HR Attendance Assignment`
- Custom fields on `Employee Checkin`
- Mobile API methods for attendance context and check-in

## Business Goal

Allow employees to check in/out from the mobile app based on allowed attendance locations.

The allowed location can come from:

- Direct employee assignment
- Department assignment
- Branch assignment
- Company assignment
- Project assignment

The same design is generic and can be used on any ERPNext installation.

## Authentication

Use the same authentication method already used by the mobile app.

Common Frappe options:

### Option 1: Token Auth

```http
Authorization: token {api_key}:{api_secret}
Content-Type: application/json
Accept: application/json
```

### Option 2: Session Cookie

Use `/api/method/login`, then store and send the returned cookies with future requests.

```http
Cookie: sid=...
Content-Type: application/json
Accept: application/json
```

The attendance APIs depend on `frappe.session.user`, so the request must be authenticated as the employee user.

## Endpoint Summary

| Purpose | Method | URL |
| --- | --- | --- |
| Get attendance context | `POST` | `/api/method/mobile_api.api.get_hr_attendance_context` |
| Get mobile device verification status | `POST` | `/api/method/mobile_api.api.get_mobile_device_verification_status` |
| Request mobile device verification | `POST` | `/api/method/mobile_api.api.request_mobile_device_verification` |
| Create check-in / check-out | `POST` | `/api/method/mobile_api.api.mobile_employee_checkin` |

Full URLs:

```text
{BASE_URL}/api/method/mobile_api.api.get_hr_attendance_context
{BASE_URL}/api/method/mobile_api.api.get_mobile_device_verification_status
{BASE_URL}/api/method/mobile_api.api.request_mobile_device_verification
{BASE_URL}/api/method/mobile_api.api.mobile_employee_checkin
```

## Main Frontend Screens

### 1. Attendance Home

Show the employee current attendance context.

Recommended UI elements:

- Employee name
- Current date and time
- Last check-in
- Allowed locations
- Primary button:
  - `Check In`
  - `Check Out`
- Current GPS status:
  - Location permission granted
  - Accuracy
  - Distance to selected work location
- Warning messages:
  - Attendance disabled
  - No employee linked to this user
  - No allowed attendance location
  - Outside allowed geofence

### 2. Location Selection

If the employee has more than one allowed location, show a selector.

Each location card should show:

- Location name
- Location type: Company / Branch / Department / Project / Custom
- Radius in meters
- Current distance if GPS is available
- Status:
  - Inside range
  - Outside range
  - GPS required

If there is only one allowed location, select it automatically.

### 3. Check-In Confirmation

Before submitting, show a confirmation dialog:

- Log type: IN / OUT
- Selected location
- Current distance
- GPS accuracy
- Optional notes if enabled in settings

## API Methods

All methods are available through Frappe RPC.

Base format:

```http
POST /api/method/<method_path>
```

Use the normal authenticated mobile session/token used by the app.

## Flutter Recommended Structure

Recommended files in Flutter:

```text
lib/
  features/
    attendance/
      data/
        attendance_api.dart
        attendance_models.dart
      presentation/
        attendance_page.dart
        location_selector.dart
        checkin_confirm_sheet.dart
      state/
        attendance_controller.dart
```

Recommended packages:

```yaml
dependencies:
  dio: ^5.0.0
  geolocator: ^12.0.0
  permission_handler: ^11.0.0
```

Package versions can be adjusted based on the mobile project.

## Get Attendance Context

### Method

```text
mobile_api.api.get_hr_attendance_context
```

### Full URL

```text
POST {BASE_URL}/api/method/mobile_api.api.get_hr_attendance_context
```

### Purpose

Load settings, employee information, allowed locations, and last check-in.

### Request

No required arguments.

Optional:

```json
{
  "project": "PRO-0001",
  "device_id": "stable-device-id",
  "platform": "android"
}
```

Frappe accepts `args` as form data or JSON depending on your client setup. For Flutter/Dio, send JSON:

```json
{
  "project": "PRO-0001",
  "device_id": "stable-device-id",
  "platform": "android"
}
```

Use `project` if the mobile screen is opened from a project context and you want project-based attendance locations.

### Success Response

```json
{
  "enabled": true,
  "settings": {
    "require_geo_location": true,
    "enforce_geofence": true,
    "allow_checkout_outside_geofence": true,
    "default_radius_meters": 100,
    "allow_manual_notes": true,
    "default_log_type": "IN",
    "skip_auto_attendance": false,
    "allow_checkin_without_assignment": false,
    "require_verified_mobile_device": true,
    "allow_multiple_verified_devices": false,
    "device_verification_approver_role": "HR Manager",
    "require_checkin_photo": true,
    "photo_required_for": "IN and OUT",
    "max_photo_size_kb": 2048
  },
  "employee": {
    "name": "EMP-0001",
    "employee_name": "Employee Name",
    "department": "Safety - TPG",
    "branch": "Riyadh",
    "company": "Technical Palace Group"
  },
  "allowed_locations": [
    {
      "name": "MHAL-0001",
      "location_name": "Project Site A",
      "location_type": "Project",
      "company": "Technical Palace Group",
      "branch": null,
      "department": null,
      "project": "PRO-0001",
      "latitude": 24.7136,
      "longitude": 46.6753,
      "radius_meters": 150,
      "address": "Riyadh site"
    }
  ],
  "last_checkin": {
    "name": "EMP-CKIN-0001",
    "time": "2026-08-08 08:01:00",
    "log_type": "IN",
    "attendance_location": "MHAL-0001",
    "geofence_status": "Valid"
  },
  "device_verification_required": true,
  "device_verified": false,
  "device_verification_status": "Not Requested",
  "can_checkin": false,
  "blocking_reason": "DEVICE_NOT_VERIFIED",
  "device_verification": {
    "required": true,
    "verified": false,
    "status": "Not Requested",
    "request_name": null,
    "can_request": true,
    "can_checkin": false,
    "blocking_reason": "DEVICE_NOT_VERIFIED"
  }
}
```

### Frontend Behavior

- If `enabled = false`, hide check-in actions and show: `Attendance from mobile is disabled`.
- If `employee` is missing, show: `No active employee is linked to your user`.
- If `allowed_locations` is empty and check-in without assignment is disabled, show: `No attendance location assigned`.
- If locations exist, request device location permission.

### Flutter Dio Example

```dart
Future<Map<String, dynamic>> getAttendanceContext({
  String? project,
  String? deviceId,
  String? platform,
}) async {
  final response = await dio.post(
    '$baseUrl/api/method/mobile_api.api.get_hr_attendance_context',
    data: {
      if (project != null) 'project': project,
      if (deviceId != null) 'device_id': deviceId,
      if (platform != null) 'platform': platform,
    },
    options: Options(
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'token $apiKey:$apiSecret',
      },
    ),
  );

  return Map<String, dynamic>.from(response.data['message'] ?? {});
}
```

## Mobile Device Verification

### Goal

When `Mobile HR Attendance Settings.require_verified_mobile_device = 1`, the backend will not accept attendance check-in/out unless the current employee has an approved `Mobile HR Device Verification` for the same `device_id`.

The biometric check, such as Face ID or fingerprint, remains local inside Flutter. The server does not receive biometric data. The server only validates the approved `device_id`.

### Device ID Requirements

Flutter should generate or read a stable device identifier and keep using the same value for all attendance calls.

Recommended fields sent by Flutter:

- `device_id`: stable unique identifier for the device/app installation.
- `device_name`: user-friendly device name.
- `platform`: `android` or `ios`.
- `app_version`: current mobile app version.
- `phone_number`: user phone number shown to HR for approval.

If the device identifier changes, HR approval is required again.

### Get Device Verification Status

```text
POST {BASE_URL}/api/method/mobile_api.api.get_mobile_device_verification_status
```

Request:

```json
{
  "device_id": "stable-device-id",
  "platform": "android"
}
```

Success response:

```json
{
  "status": "success",
  "required": true,
  "verified": false,
  "verification_status": "Not Requested",
  "request_name": null,
  "can_request": true,
  "can_checkin": false,
  "blocking_reason": "DEVICE_NOT_VERIFIED"
}
```

### Request Mobile Device Verification

```text
POST {BASE_URL}/api/method/mobile_api.api.request_mobile_device_verification
```

Request:

```json
{
  "device_id": "stable-device-id",
  "device_name": "iPhone 15 Pro",
  "platform": "ios",
  "app_version": "1.4.0",
  "phone_number": "+9665XXXXXXXX"
}
```

Success response:

```json
{
  "status": "success",
  "request_name": "MHDV-2026-00001",
  "verification_status": "Pending Approval",
  "verified": false,
  "can_checkin": false,
  "message": "Mobile device verification request created and is pending HR approval."
}
```

HR approves the request from ERPNext in `Mobile HR Device Verification`. After approval, Flutter should call `get_hr_attendance_context` again with the same `device_id`.

### Flutter Verification Flow

1. Read authenticated employee session.
2. Read stable `device_id`.
3. Call `get_hr_attendance_context` with `device_id` and `platform`.
4. If `can_checkin = false` and `blocking_reason = DEVICE_NOT_VERIFIED`, show `Request Mobile Verification`.
5. Call `request_mobile_device_verification`.
6. Show pending approval state until HR approves.
7. After approval, call context again.
8. Run local Face ID / fingerprint check in Flutter.
9. Call `mobile_employee_checkin` with the same `device_id`.

### Device Verification Error Codes

| Code | Meaning | Recommended Flutter UI |
| --- | --- | --- |
| `DEVICE_ID_REQUIRED` | Backend requires a device ID but the request did not send one. | Rebuild request with device ID. |
| `DEVICE_NOT_VERIFIED` | No approved verification exists for this employee/device. | Show request verification button. |
| `PENDING_APPROVAL` | Request exists but HR has not approved it yet. | Show pending approval message. |
| `DEVICE_REJECTED` | HR rejected the request. | Allow sending a new request if appropriate. |
| `DEVICE_REVOKED` | Previously approved device was revoked. | Block attendance and show request verification. |

## Create Employee Check-In

### Method

```text
mobile_api.api.mobile_employee_checkin
```

### Full URL

```text
POST {BASE_URL}/api/method/mobile_api.api.mobile_employee_checkin
```

### Purpose

Create `Employee Checkin` after validating settings, employee, GPS, allowed location, and geofence.

### Request

```json
{
  "log_type": "IN",
  "latitude": 24.7136,
  "longitude": 46.6753,
  "attendance_location": "MHAL-0001",
  "device_id": "mobile-device-id",
  "accuracy": 12,
  "notes": "Started shift",
  "project": "PRO-0001",
  "photo_base64": "/9j/4AAQSkZJRgABAQ...",
  "photo_filename": "checkin_2026_08_12.jpg",
  "photo_mime_type": "image/jpeg"
}
```

### Arguments

| Field | Required | Description |
| --- | --- | --- |
| `log_type` | Optional | `IN` or `OUT`. If empty, backend uses default from settings. |
| `latitude` | Required if GPS enabled | Current device latitude. |
| `longitude` | Required if GPS enabled | Current device longitude. |
| `attendance_location` | Optional | Selected `Mobile HR Attendance Location`. If empty, backend chooses nearest allowed location. |
| `device_id` | Required if mobile device verification is enabled | Stable mobile device identifier approved by HR. |
| `accuracy` | Optional | GPS accuracy in meters. |
| `notes` | Optional | User note, if enabled in settings. |
| `project` | Optional | Project context for project-based assignments. |
| `photo_base64` | Required when photo setting applies | Base64 image content. Data URL format is also accepted. |
| `photo_filename` | Optional | Suggested file name, for example `checkin_2026_08_12.jpg`. |
| `photo_mime_type` | Recommended with photo | Must be `image/jpeg` or `image/png`. |

### Attendance Photo Rules

The app should read these values from `get_hr_attendance_context.settings` before showing the check-in/out button:

- `require_checkin_photo`
- `photo_required_for`
- `max_photo_size_kb`

Supported values for `photo_required_for`:

- `IN and OUT`
- `IN Only`
- `OUT Only`
- `Optional`

If a photo is required for the selected `log_type`, Flutter should open the camera, capture a fresh photo, compress/resize it, and send it in the same `mobile_employee_checkin` request.

Only JPEG and PNG are accepted. Recommended mobile behavior is to upload JPEG under the configured `max_photo_size_kb`.

### Success Response

```json
{
  "status": "success",
  "message": "Check-in created",
  "checkin": {
    "name": "EMP-CKIN-0002",
    "employee": "EMP-0001",
    "employee_name": "Employee Name",
    "time": "2026-08-08 08:10:00",
    "log_type": "IN",
    "attendance_location": "MHAL-0001",
    "distance_meters": 18.4,
    "geofence_status": "Valid",
    "photo_required": true,
    "photo_uploaded": true,
    "photo_url": "/private/files/checkin_2026_08_12-ab12cd.jpg"
  }
}
```

### Flutter Dio Example

```dart
Future<Map<String, dynamic>> createMobileCheckin({
  required String logType,
  required double latitude,
  required double longitude,
  String? attendanceLocation,
  String? deviceId,
  double? accuracy,
  String? notes,
  String? project,
  String? photoBase64,
  String? photoFilename,
  String? photoMimeType,
}) async {
  final response = await dio.post(
    '$baseUrl/api/method/mobile_api.api.mobile_employee_checkin',
    data: {
      'log_type': logType,
      'latitude': latitude,
      'longitude': longitude,
      if (attendanceLocation != null) 'attendance_location': attendanceLocation,
      if (deviceId != null) 'device_id': deviceId,
      if (accuracy != null) 'accuracy': accuracy,
      if (notes != null && notes.isNotEmpty) 'notes': notes,
      if (project != null) 'project': project,
      if (photoBase64 != null) 'photo_base64': photoBase64,
      if (photoFilename != null) 'photo_filename': photoFilename,
      if (photoMimeType != null) 'photo_mime_type': photoMimeType,
    },
    options: Options(
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'token $apiKey:$apiSecret',
      },
    ),
  );

  return Map<String, dynamic>.from(response.data['message'] ?? {});
}
```

### Flutter Geolocation Example

```dart
Future<Position> getCurrentGpsPosition() async {
  final serviceEnabled = await Geolocator.isLocationServiceEnabled();
  if (!serviceEnabled) {
    throw Exception('Location service is disabled');
  }

  LocationPermission permission = await Geolocator.checkPermission();
  if (permission == LocationPermission.denied) {
    permission = await Geolocator.requestPermission();
  }

  if (permission == LocationPermission.denied ||
      permission == LocationPermission.deniedForever) {
    throw Exception('Location permission is required');
  }

  return Geolocator.getCurrentPosition(
    desiredAccuracy: LocationAccuracy.high,
  );
}
```

### Full Check-In Flow Example

```dart
Future<void> handleCheckin({
  required String logType,
  String? selectedLocationName,
  required String deviceId,
  required String platform,
  String? project,
}) async {
  final context = await getAttendanceContext(
    project: project,
    deviceId: deviceId,
    platform: platform,
  );

  if (context['enabled'] != true) {
    throw Exception('Mobile attendance is disabled');
  }

  if (context['can_checkin'] == false) {
    final reason = context['blocking_reason']?.toString();
    if (reason == 'DEVICE_NOT_VERIFIED') {
      throw Exception('Please request mobile device verification');
    }
    if (reason == 'PENDING_APPROVAL') {
      throw Exception('Mobile device verification is pending HR approval');
    }
    throw Exception(reason ?? 'Mobile attendance is blocked');
  }

  final settings = Map<String, dynamic>.from(context['settings'] ?? {});
  final requireGps = settings['require_geo_location'] == true;

  Position? position;
  if (requireGps) {
    position = await getCurrentGpsPosition();
  }

  final result = await createMobileCheckin(
    logType: logType,
    latitude: position?.latitude ?? 0,
    longitude: position?.longitude ?? 0,
    attendanceLocation: selectedLocationName,
    deviceId: deviceId,
    accuracy: position?.accuracy,
    project: project,
  );

  if (result['status'] != 'success') {
    throw Exception(result['message'] ?? 'Unable to create check-in');
  }
}
```

### Expected Error Cases

The frontend should show backend messages clearly.

Common cases:

- Mobile attendance is disabled.
- No active employee is linked to the current user.
- Location is required.
- No attendance location is assigned.
- Selected location is not allowed for this employee.
- Employee is outside the allowed attendance range.
- Invalid log type.
- Device ID is required.
- Mobile device is not verified.
- Mobile device verification is pending HR approval.
- Attendance photo is required.
- Attendance photo is too large.
- Attendance photo type is unsupported.
- Attendance photo base64 data is invalid.

Photo-related backend `error_code` values:

| Error Code | Meaning | Frontend Action |
| --- | --- | --- |
| `CHECKIN_PHOTO_REQUIRED` | Photo is required for this IN/OUT action. | Open camera and retry with `photo_base64`. |
| `UNSUPPORTED_CHECKIN_PHOTO_TYPE` | File is not JPEG/PNG. | Convert/compress to JPEG or PNG. |
| `CHECKIN_PHOTO_TOO_LARGE` | File exceeds `max_photo_size_kb`. | Resize/compress and retry. |
| `INVALID_CHECKIN_PHOTO` | Base64 is invalid or empty. | Re-capture image and retry. |

### Checkout Outside Geofence

If `allow_checkout_outside_geofence = true`, the backend allows `OUT` check-ins outside the assigned geofence.

Backend behavior:

- `log_type = IN` outside geofence is still rejected when `enforce_geofence = true`.
- `log_type = OUT` outside geofence is accepted.
- The created `Employee Checkin` is marked:
  - `mobile_api_geofence_status = Outside`
  - `skip_auto_attendance = 1`

Frontend behavior:

- For `OUT`, show a warning if the employee is outside the assigned location.
- Do not block the user on frontend if settings allow checkout outside geofence.
- After success, show a message like: `Checkout recorded outside assigned location and skipped from auto attendance`.
- The backend remains the final source of truth.

## Error Response Format

Frappe errors can come in different formats depending on whether the exception was handled or thrown.

The mobile app should handle:

```json
{
  "exception": "...",
  "_server_messages": "[\"message\"]"
}
```

or:

```json
{
  "message": {
    "status": "error",
    "message": "Error text"
  }
}
```

Recommended frontend behavior:

- Prefer `response.data.message.message` if available.
- Else parse `_server_messages`.
- Else show a generic error.

Example:

```dart
String extractFrappeError(dynamic data) {
  if (data is Map) {
    final message = data['message'];
    if (message is Map && message['message'] != null) {
      return message['message'].toString();
    }

    if (data['_server_messages'] != null) {
      return data['_server_messages'].toString();
    }

    if (data['exception'] != null) {
      return data['exception'].toString();
    }
  }

  return 'Unexpected error';
}
```

## Geolocation Handling

Recommended frontend flow:

1. Load attendance context.
2. If GPS is required, ask for location permission.
3. Read current GPS coordinates.
4. Calculate approximate distance on frontend for display only.
5. Send coordinates to backend.
6. Treat backend validation as final source of truth.

Do not rely only on frontend distance validation. The backend already validates the final geofence.

## Troubleshooting

### `mobile_api.api has no attribute ...`

If Flutter receives an error like:

```text
mobile_api.api has no attribute get_hr_attendance_context
```

or:

```text
mobile_api.api has no attribute get_mobile_device_verification_status
```

the Python worker is likely still running an old loaded version of `mobile_api.api`.

Run on the server:

```bash
bench --site tpg.com clear-cache
bench restart
```

`clear-cache` alone refreshes metadata/cache, but it does not always reload Python web workers. A restart is required after adding new whitelisted functions.

## Suggested Frontend State Model

```dart
class AttendanceState {
  final bool loading;
  final bool submitting;
  final bool enabled;
  final Map<String, dynamic>? employee;
  final Map<String, dynamic>? settings;
  final List<Map<String, dynamic>> allowedLocations;
  final Map<String, dynamic>? selectedLocation;
  final Position? currentPosition;
  final Map<String, dynamic>? lastCheckin;
  final String? gpsError;

  const AttendanceState({
    this.loading = false,
    this.submitting = false,
    this.enabled = false,
    this.employee,
    this.settings,
    this.allowedLocations = const [],
    this.selectedLocation,
    this.currentPosition,
    this.lastCheckin,
    this.gpsError,
  });
}
```

## Suggested Frontend Actions

### Load Context

```dart
final context = await attendanceApi.getAttendanceContext(project: project);
```

### Submit Check-In

```dart
final result = await attendanceApi.createMobileCheckin(
  logType: 'IN',
  latitude: position.latitude,
  longitude: position.longitude,
  attendanceLocation: selectedLocation['name'],
  accuracy: position.accuracy,
  notes: notes,
  project: project,
);
```

## Recommended UI Rules

- Disable the check-in button while GPS is loading.
- Disable the check-in button while submitting.
- Show the selected location before submission.
- Show distance and allowed radius.
- If `IN` is outside geofence, show a warning before submission and let backend provide the final rejection.
- If `OUT` is outside geofence and settings allow it, show a warning but allow submission.
- Refresh attendance context after successful check-in.
- Show last check-in prominently.

## Admin Setup Flow

The ERPNext admin / HR manager should configure:

1. Open `Mobile HR Attendance Settings`.
2. Enable mobile attendance.
3. Set GPS and geofence rules.
4. Create `Mobile HR Attendance Location` records.
5. Create `Mobile HR Attendance Assignment` records:
   - Employee
   - Department
   - Branch
   - Company
   - Project

## Data Stored on Employee Checkin

The backend stores extra data on `Employee Checkin`:

- `mobile_api_attendance_location`
- `mobile_api_checkin_source`
- `mobile_api_project`
- `mobile_api_geofence_status`
- `mobile_api_distance_meters`
- `mobile_api_latitude`
- `mobile_api_longitude`
- `mobile_api_location_accuracy`
- `mobile_api_device_id`
- `mobile_api_photo`
- `mobile_api_photo_uploaded`
- `mobile_api_photo_file`
- `mobile_api_notes`

These fields are read-only in ERPNext and should be treated as audit fields.

## Security Notes

- The frontend must not decide whether a user is allowed to check in.
- The backend validates:
  - current user
  - linked active employee
  - enabled settings
  - allowed location assignments
  - geofence distance
- The frontend should always send real GPS coordinates from the device when GPS is required.

## Troubleshooting

### `mobile_api.api has no attribute get_hr_attendance_context`

This means the running Python web worker has not loaded the latest `mobile_api.api` module, or the app code deployed on the server is older than this document.

Backend checklist:

```bash
bench --site tpg.com execute frappe.get_attr --args '["mobile_api.api.get_hr_attendance_context"]'
bench --site tpg.com execute frappe.get_attr --args '["mobile_api.api.mobile_employee_checkin"]'
bench --site tpg.com clear-cache
bench restart
```

Important:

- `bench --site tpg.com clear-cache` clears Frappe cache, but it does not reload already-running Python web workers.
- `bench restart` or restarting supervisor/gunicorn is required after adding new Python methods.
- The official Flutter endpoint remains:

```text
POST {BASE_URL}/api/method/mobile_api.api.get_hr_attendance_context
```

Do not change the Flutter endpoint to the handler path unless the backend team explicitly exposes a new public path.

### `project` argument

`project` is optional. Send it only when the attendance screen is opened from a project context.

```json
{
  "project": "PRO-0001"
}
```

If no project is sent, the backend returns locations assigned directly to the employee, department, branch, company, or all active locations if allowed in settings.

## Implementation Checklist

- Add HR Attendance section in the mobile app.
- Call `get_hr_attendance_context` on screen load.
- Request GPS permission if required.
- Show allowed locations.
- Add Check In / Check Out buttons.
- Call `mobile_employee_checkin`.
- Show success/error messages.
- Refresh context after each successful check-in.
- Test:
  - employee with direct assignment
  - department assignment
  - project assignment
  - outside geofence
  - GPS disabled
  - employee without assignment
  - mobile attendance disabled
