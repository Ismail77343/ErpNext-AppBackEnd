# Material Transfer Handover API

`Material Transfer Handover` is the mobile workflow for documenting Material Transfer pickup,
delivery, and return drafts.

The stock team creates and submits a `Stock Entry` with `purpose = Material Transfer`.
If `No Receiver Required` is not checked, `Receiver User` is required before submit.
On submit, `mobile_api` creates a `Mobile Material Transfer Handover` and optionally a
`Mobile Task Follow Up` for the receiver.

## Desk Fields

`mobile_api` adds these fields to `Stock Entry`:

| Field | Purpose |
| --- | --- |
| `mobile_handover_receiver_user` | User who must document pickup and delivery in the app. |
| `mobile_no_receiver_required` | Allows submitting without receiver and without mobile handover. |
| `mobile_material_handover` | Link to the generated handover record. |
| `mobile_handover_status` | Current handover state. |
| `mobile_handover_task` | Linked `Mobile Task Follow Up`. |
| `mobile_pickup_photo`, `mobile_pickup_on`, `mobile_pickup_location` | Pickup evidence from the app. |
| `mobile_delivery_photo`, `mobile_delivery_on`, `mobile_delivery_location` | Delivery evidence from the app. |
| `mobile_last_return_stock_entry`, `mobile_last_return_photo`, `mobile_last_return_on`, `mobile_last_return_location` | Latest return draft created from the app. |

Latitude, longitude, and GPS accuracy are also stored in hidden/read-only fields:
`mobile_pickup_latitude`, `mobile_pickup_longitude`, `mobile_pickup_accuracy_meters`,
`mobile_delivery_latitude`, `mobile_delivery_longitude`, `mobile_delivery_accuracy_meters`,
`mobile_last_return_latitude`, `mobile_last_return_longitude`, and
`mobile_last_return_accuracy_meters`.

Return Stock Entries are created as Draft and use the same handover link. They also store
`mobile_handover_return_for` internally to point to the original transfer.

## Settings

Open `Mobile Material Transfer Handover Settings`:

| Field | Default | Description |
| --- | --- | --- |
| `enabled` | `1` | Enables the Stock Entry validation and mobile workflow. |
| `auto_create_task_follow_up` | `1` | Creates a `Mobile Task Follow Up` on Stock Entry submit. |
| `require_pickup_photo` | `1` | Pickup confirmation must include a photo. |
| `require_pickup_location` | `1` | Pickup confirmation must include GPS latitude and longitude. |
| `require_delivery_photo` | `1` | Delivery confirmation must include a photo. |
| `require_delivery_location` | `1` | Delivery confirmation must include GPS latitude and longitude. |
| `require_return_photo` | `1` | Return draft creation must include a photo. |
| `require_return_location` | `1` | Return draft creation must include GPS latitude and longitude. |
| `max_photo_size_kb` | `2048` | Maximum JPEG/PNG photo size. |
| `return_allowed_days_after_submit` | `1` | Allows return until the submit date plus this many days. |

## Endpoints

All endpoints return:

```json
{"status": "success", "data": {}}
```

or:

```json
{"status": "error", "message": "...", "code": "..."}
```

### List My Handovers

`mobile_api.api.get_my_material_transfer_handovers`

Request:

```json
{
  "status": "Pending Pickup",
  "limit_start": 0,
  "limit_page_length": 20
}
```

`status` is optional. Values:
`Pending Pickup`, `Picked Up`, `Delivered`, `Return Draft Created`, `Closed`, `Cancelled`.

### Handover Details

`mobile_api.api.get_material_transfer_handover_details`

Request:

```json
{"name": "MMTH-2026-00001"}
```

Response `data` includes:

- handover fields
- `items`: original Stock Entry items
- `return_options.items`: each item with `returned_qty`, `remaining_qty`, and `returnable`
- `can_confirm_pickup`, `can_confirm_delivery`, `can_create_return`
- pickup, delivery, and return GPS fields when they have been captured
- `logs`: each event includes `latitude`, `longitude`, `accuracy_meters`, and `location`

### Confirm Pickup

`mobile_api.api.confirm_material_transfer_pickup`

Request:

```json
{
  "name": "MMTH-2026-00001",
  "photo_base64": "data:image/jpeg;base64,/9j/...",
  "photo_filename": "pickup.jpg",
  "latitude": 24.7135517,
  "longitude": 46.6752957,
  "accuracy_meters": 12.5,
  "notes": "Received from main store"
}
```

The receiver only can confirm pickup. The handover moves from `Pending Pickup` to `Picked Up`.
The photo is saved as a private `File` attached to the original `Stock Entry`.
If `require_pickup_location` is enabled, `latitude` and `longitude` are required.

### Confirm Delivery

`mobile_api.api.confirm_material_transfer_delivery`

Request:

```json
{
  "name": "MMTH-2026-00001",
  "photo_base64": "data:image/jpeg;base64,/9j/...",
  "photo_filename": "delivery.jpg",
  "latitude": 24.7141201,
  "longitude": 46.6760182,
  "accuracy_meters": 9.8,
  "notes": "Delivered to site WIP warehouse"
}
```

The receiver only can confirm delivery. The handover moves from `Picked Up` to `Delivered`.
The linked task follow-up is completed automatically for this workflow.
If `require_delivery_location` is enabled, `latitude` and `longitude` are required.

### Get Return Options

`mobile_api.api.get_material_transfer_return_options`

Request:

```json
{"name": "MMTH-2026-00001"}
```

Use this before showing the return screen. Only rows with `remaining_qty > 0` should be selectable.

### Create Return Draft

`mobile_api.api.create_material_transfer_return`

Request:

```json
{
  "name": "MMTH-2026-00001",
  "items": [
    {"stock_entry_detail": "abc123", "qty": 2}
  ],
  "photo_base64": "data:image/png;base64,iVBORw0KGgo...",
  "photo_filename": "return.png",
  "latitude": 24.7139902,
  "longitude": 46.6758744,
  "accuracy_meters": 15,
  "notes": "Unused material returned"
}
```

Behavior:

- Allowed only after delivery and within the configured return window.
- Creates a Draft `Stock Entry` with `purpose = Material Transfer`.
- Reverses the warehouses: original `to_warehouse` becomes return source, original `from_warehouse` becomes return target.
- Allows partial returns and prevents returning more than the remaining quantity.
- Saves return GPS location on the handover and the return Draft `Stock Entry`.
- The stock manager reviews the Draft in ERPNext and submits it.

If `require_return_location` is enabled, `latitude` and `longitude` are required.

### GPS Validation

- `latitude` must be between `-90` and `90`.
- `longitude` must be between `-180` and `180`.
- `accuracy_meters` is optional. If sent, it must be zero or greater.
- The backend stores the point as Frappe `Geolocation` for Desk map display and also stores numeric latitude/longitude for API use.
- The backend does not currently validate distance from a warehouse or project location.

Location-related error codes:

| Code | Meaning |
| --- | --- |
| `PICKUP_LOCATION_REQUIRED` | Pickup GPS is required by settings. |
| `DELIVERY_LOCATION_REQUIRED` | Delivery GPS is required by settings. |
| `RETURN_LOCATION_REQUIRED` | Return GPS is required by settings. |
| `INVALID_LOCATION` | Latitude/longitude is incomplete or not numeric. |
| `INVALID_LATITUDE` | Latitude is outside the allowed range. |
| `INVALID_LONGITUDE` | Longitude is outside the allowed range. |
| `INVALID_ACCURACY` | Accuracy is negative. |

## Frontend Flow

1. Call `get_my_material_transfer_handovers`.
2. If status is `Pending Pickup`, show a pickup action requiring camera photo and GPS.
3. If status is `Picked Up`, show a delivery action requiring camera photo and GPS.
4. If status is `Delivered` or `Return Draft Created`, call `get_material_transfer_return_options`.
5. Show return rows with editable quantities up to `remaining_qty`.
6. Call `create_material_transfer_return` with selected rows, photo, and GPS; show the returned Draft Stock Entry name to the user.

The app should request GPS permission before calling pickup, delivery, or return endpoints.
If the API returns one of the `*_LOCATION_REQUIRED` errors, show a clear message asking the user
to enable location access and retry.

## Permissions

- Receiver user can list and update their assigned handovers.
- `Stock Manager` and `System Manager` can view and monitor all handovers.
- Only the receiver can confirm pickup, delivery, and create return drafts from the app.
