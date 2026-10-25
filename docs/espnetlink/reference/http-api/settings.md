---
title: Settings
---

# Settings

<p class="lead">One generic surface for every settings component: read the document, read its schema, write the whole document back, submit to restart. The components and their keys are in the [settings reference](../settings.md).</p>

## GET /api/settings

The components, with their schema version and whether each one fell back to defaults or waits for a restart.

```json
{ "components": [
  { "name": "log_manager", "version": 1, "degraded": false, "pending_reboot": false },
  { "name": "wifi_manager", "version": 6, "degraded": false, "pending_reboot": true },
  { "name": "lte_upstream_pppos", "version": 1, "degraded": false, "pending_reboot": false }
] }
```

The seventeen components: `log_manager`, `restart_tracker`, `dev_status_manager`, `wifi_manager`, `cmdline_manager`, `ha_webhooks`, `mdns_manager`, `led_manager`, `imu_manager`, `vpn_manager`, `filesystem`, `usb_dev_ethernet`, `lte_upstream_pppos`, `gps`, `wifi_modem`, `usb_cli_console`, `system`.

## GET /api/settings/{name}

The stored document (the values that apply at the next start), secrets blanked, plus the two synthetic flags.

```json
{
  "enabled": true,
  "apn": "internet",
  "apn_user": "",
  "apn_password": "",
  "apn_pin": "",
  "ncm_share": false,
  "cli": true,
  "degraded": false,
  "pending_reboot": false
}
```

`404 {"error":"unknown component"}` for a name that is not registered.

## PUT /api/settings/{name}

The whole document. Keys left out take their schema defaults; a blank secret keeps the stored one. The document is validated against the schema (type, range, enum, length) and the component's own rules, then stored. Nothing applies until the submit.

```json
{ "changed": true }
```

`changed: false` means the stored document was already identical, and the submit will not restart. Errors: `400` with the validator's message (`apn: above maximum length 63`, `sta_password set but sta_ssid is empty`), `404` unknown component.

## GET /api/settings/{name}/schema

The JSON schema the web interface builds its forms from: type, `minimum` and `maximum`, `minLength` and `maxLength`, `enum`, and the `default` of every key.

```json
{ "type": "object", "properties": {
  "enabled": { "type": "boolean", "default": true },
  "apn": { "type": "string", "maxLength": 63, "default": "internet" },
  "apn_pin": { "type": "string", "maxLength": 8, "default": "" },
  "ncm_share": { "type": "boolean", "default": false }
} }
```

## POST /api/settings/submit

Ends a batch of `PUT`s. `{"reboot": true}` and a restart about a second later when any `PUT` changed something; `{"reboot": false}` and nothing else otherwise.

## GET /api/settings/backup

The whole configuration as one document, served as a download named `espnetlink-<device id>-settings.json`. Secrets are **not** blanked here.

```json
{
  "wican_backup": 1,
  "device_id": "14c19f457fed",
  "components": {
    "wifi_manager": { "version": 6, "data": { "mode": "off", "...": "..." } },
    "lte_upstream_pppos": { "version": 1, "data": { "apn": "internet", "...": "..." } }
  }
}
```

## POST /api/settings/backup

Restores a backup document. Every component is checked (and migrated when older) before anything is stored; one failure rejects the whole document.

```json
{ "restored": 17, "skipped": [], "reboot": true }
```

`400 {"error":"backup rejected","errors":{"wifi_manager":"ap_channel: above maximum 13"},"skipped":[]}` on a bad document; `400 {"error":"not a WiCAN settings backup"}` without the `wican_backup` and `components` keys. Body limit 32 KB.

## POST /api/settings/factory_reset

Body `{"confirm": "factory-reset"}`. Deletes every stored settings document and restarts into the defaults: `{"reboot": true}`. Without the exact token: `400 {"error":"confirmation required: {\"confirm\":\"factory-reset\"}"}` and nothing wiped. Files under `/data` are kept.
