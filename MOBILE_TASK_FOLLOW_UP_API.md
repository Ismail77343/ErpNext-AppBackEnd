# Mobile Task Follow Up API

## Overview

`Mobile Task Follow Up` is an independent task-follow module inside `mobile_api`.
It does not depend on `tpg_app`.

The mobile app can use it for two workflows:

- A manager creates follow-up tasks for employees or users.
- An assignee sees assigned tasks, adds updates, and receives in-app notifications.

Automatic task creation from `Project Daily Timesheet Batch` is optional and controlled by settings.

If `Task Follow Up` from `tpg_app` is installed and `sync_with_tpg_task_follow_up` is enabled,
records are synchronized both ways:

- Creating or updating `Task Follow Up` in Desk creates or updates `Mobile Task Follow Up`.
- Creating or updating `Mobile Task Follow Up` from the API creates or updates `Task Follow Up`.
- Follow-up rows are synchronized between `child_follow` and `updates`.
- Old Desk records are not backfilled automatically, but they are linked the next time they are edited.

## Settings

Open `Mobile Task Follow Up Settings` in ERPNext:

| Field | Purpose |
|---|---|
| `enabled` | Enables manual creation and updates from the API. |
| `auto_create_from_timesheet_distribution` | Creates follow-up tasks when `Project Daily Timesheet Batch` is submitted. |
| `sync_with_tpg_task_follow_up` | Synchronizes with the desk `Task Follow Up` DocType when it is installed. |
| `notify_assignee_in_app` | Makes unread assigned tasks appear in the notification API. |
| `default_due_days` | Default due date offset when no due date is sent. |

## Authentication

All endpoints require an authenticated Frappe user.

Use the same mobile session/token pattern already used by the rest of `mobile_api`:

```http
Authorization: token {api_key}:{api_secret}
```

## Endpoints

### Create Task Follow Up

```http
POST /api/method/mobile_api.api.create_mobile_task_follow_up
```

Creates one task per assignee.

Request:

```json
{
  "assigned_to_employees": ["EMP-0001", "EMP-0002"],
  "assigned_to_users": ["user@example.com"],
  "subject": "Submit daily work update",
  "details": "Send the completed work notes before end of day.",
  "priority": "Medium",
  "project": "PROJ-0001",
  "task": "TASK-0001",
  "start_date": "2026-08-20",
  "due_date": "2026-08-21"
}
```

`assigned_to_employees` and `assigned_to_users` can be JSON arrays or comma-separated strings.

Success:

```json
{
  "status": "success",
  "message": "Mobile task follow up created successfully.",
  "count": 2,
  "data": [
    {
      "name": "MTFU-2026-00001",
      "subject": "Submit daily work update",
      "assigned_to_user": "employee@example.com",
      "status": "Open",
      "progress": 0
    }
  ]
}
```

### My Assigned Tasks

```http
GET /api/method/mobile_api.api.get_my_mobile_task_follow_ups
```

Returns tasks assigned to the current user.

Optional parameters:

| Parameter | Description |
|---|---|
| `status` | Filter by `Open`, `Working`, `Blocked`, `Overdue`, `Completed`, or `Cancelled`. |
| `only_open` | Send `1` to exclude completed/cancelled tasks. |
| `limit_start` | Pagination start. |
| `limit_page_length` | Page size. |

### Tasks I Assigned

```http
GET /api/method/mobile_api.api.get_assigned_mobile_task_follow_ups
```

Returns tasks created by the current user for other employees/users.

It accepts the same filters as `get_my_mobile_task_follow_ups`.

### Task Details

```http
GET /api/method/mobile_api.api.get_mobile_task_follow_up_details
```

Request:

```json
{
  "name": "MTFU-2026-00001"
}
```

Returns the task with its `updates` table.

### Add Task Update

```http
POST /api/method/mobile_api.api.add_mobile_task_follow_up_update
```

Request:

```json
{
  "name": "MTFU-2026-00001",
  "note": "Work started and first section is done.",
  "progress": 40,
  "status": "Working",
  "attachment": "/files/photo.jpg"
}
```

Allowed for:

- the assignee
- the creator
- System Manager

The assignee can set `Open`, `Working`, `Blocked`, or `Overdue`.
Only the creator or System Manager can set `Completed` or `Cancelled`.

### Close Task

```http
POST /api/method/mobile_api.api.close_mobile_task_follow_up
```

Request:

```json
{
  "name": "MTFU-2026-00001",
  "status": "Completed",
  "note": "Accepted and closed."
}
```

Only `assigned_by` or System Manager can close/cancel.

### In-App Notifications

```http
GET /api/method/mobile_api.api.get_mobile_task_follow_up_notifications
```

Returns unread open tasks assigned to the current user.

Success:

```json
{
  "status": "success",
  "unread_count": 1,
  "data": [
    {
      "id": "MTFU-2026-00001",
      "notification_type": "mobile_task_follow_up",
      "doctype": "Mobile Task Follow Up",
      "document_name": "MTFU-2026-00001",
      "subject": "Submit daily work update",
      "priority": "Medium",
      "status": "Open",
      "progress": 0
    }
  ]
}
```

### Mark As Read

```http
POST /api/method/mobile_api.api.mark_mobile_task_follow_up_read
```

Request:

```json
{
  "name": "MTFU-2026-00001"
}
```

Only the assignee can mark the task as read.

## Timesheet Distribution Integration

When `Mobile Task Follow Up Settings.auto_create_from_timesheet_distribution = 1`,
the backend creates follow-up tasks after `Project Daily Timesheet Batch` is submitted.

For each row:

- `assigned_to_employee` comes from the row employee.
- `assigned_to_user` comes from `Employee.user_id`.
- `assigned_by` is the submitter user.
- `project`, `task`, and `source_timesheet` are copied from the row.
- Duplicate creation is prevented by `source_doctype + source_name + source_row`.

Rows without an active employee or linked user are skipped.

## Frontend Notes

- Show two tabs: `Assigned to Me` and `Assigned by Me`.
- Poll `get_mobile_task_follow_up_notifications` for unread task notifications.
- Call `mark_mobile_task_follow_up_read` when the assignee opens a task.
- Hide close/cancel actions unless `can_close = true` in the details response.
- Upload files through the existing Frappe file upload flow, then pass the file URL as `attachment`.
