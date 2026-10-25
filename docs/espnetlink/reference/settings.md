---
title: Settings reference
---

# Settings reference

<p class="lead">Every settings component of firmware 1.23.1 with its keys, ranges and defaults: what the web interface's forms are built from, and what `GET /api/settings/<name>` returns. Each component is a card on one of the pages, and all of them are on ==All Settings==.</p>

Every key applies at the next start. The ==Cli== key of a component says whether its console commands are registered. Secrets read back blank.

## Cellular (`lte_upstream_pppos`), version 1

On the ==Cellular== page as ==Modem Settings==. [Cellular](../connectivity/cellular.md).

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `enabled` | bool | `true` | Start the LTE uplink |
| `apn` | string, 63 | `internet` | The access point name |
| `apn_user` | string, 32 | `""` | APN username |
| `apn_password` | string, 32 | `""` | APN password (secret) |
| `apn_pin` | string, 8 | `""` | The SIM PIN (secret); a refused PIN is not retried until it changes |
| `ncm_share` | bool | `false` | Share the LTE link over the USB cable (router, DNS, address translation) |
| `cli` | bool | `true` | The `lte` command |

## USB Ethernet (`usb_dev_ethernet`), version 1

On the ==Cellular== page. [USB](../connectivity/usb.md).

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `class` | `ncm`, `rndis` | `rndis` | The USB network adapter's class |

## Wifi Modem (`wifi_modem`), version 2

Under ==All Settings==. [USB](../connectivity/usb.md), [WiFi](../connectivity/wifi.md).

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `usb_mode` | `auto`, `ncm`, `console` | `auto` | What the USB connector presents, and whether a host may cut the data lines |
| `ap_share` | bool | `true` | Clients of the access point get the LTE link |
| `ap_password_provisioned` | bool | `false` | Set by the firmware once the per-device password was generated; leave it |
| `cli` | bool | `true` | The `wifi_modem` command |

## GPS (`gps`), version 1

On the ==GPS== page as ==Receiver Settings==. [Position and assisted GPS](../gps/position.md).

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `enabled` | bool | `true` | Reserved |
| `passthru` | bool | `false` | NMEA passthrough on the USB console at start |
| `uart0_out` | bool | `false` | Copy the NMEA stream onto the UART |
| `agnss_enabled` | bool | `false` | Assisted GPS |
| `agnss_cache_s` | 10 to 86400 | `120` | Position cache interval, seconds |
| `epoc_constellation` | `gps`, `gps_galileo`, `gps_bds` | `gps_galileo` | Constellations the orbit prediction covers |
| `static_nav_threshold` | 0 to 20 | `5` | Speed below which the position is held, in tenths of a metre per second; 0 off |
| `aic_enabled` | bool | `true` | Active interference cancellation in the receiver |
| `cli` | bool | `true` | The `gps` and `agnss` commands |

## Wi-Fi (`wifi_manager`), version 6

On the ==Settings== page as ==WiFi / Access Point== and ==Station==. [WiFi](../connectivity/wifi.md).

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `mode` | `off`, `sta`, `ap`, `apsta` | `off` | The radio |
| `sta_ssid`, `sta_password` | string, 32 and 64 | `""` | The main network (the password is a secret) |
| `sta_trusted` | bool | `true` | Admin pages allowed through this network |
| `hostname` | string, 32 | `""` | The name on the router |
| `sta_auto_reconnect` | bool | `true` | Reconnect by itself |
| `sta_max_retry` | -1 to 1000 | `-1` | Tries before a one-minute pause; -1 forever |
| `sta_ip_mode` | `dhcp`, `static` | `dhcp` | Addressing of the main network |
| `sta_static_ip`, `sta_static_netmask`, `sta_static_gw` | IPv4 | `""`, `255.255.255.0`, `""` | The static address (required when static), mask, gateway (optional) |
| `sta_dns` | IPv4 | `""` | A DNS server to use instead of the network's, both modes |
| `fallback1_ssid` to `fallback5_ssid`, `_password`, `_trusted` | as above | `""`, `""`, `true` | The backup networks, in priority order |
| `fallback1_ip_mode` to `fallback5_ip_mode`, `_static_ip`, `_static_netmask`, `_static_gw` | as above | `dhcp`, `""`, `255.255.255.0`, `""` | Their addressing |
| `sta_roam_interval_s` | 0 to 86400 | `300` | While on a backup network, how often to look for a better one; 0 never |
| `ap_ssid` | string, 32 | `""` | The access point's name; empty derives `ESPNetLink_<id>` |
| `ap_password` | string, 8 to 64 | `12345678` | The access point's password (secret); replaced by a generated one at the first start |
| `ap_auth` | `auto`, `open`, `wpa2`, `wpa2wpa3`, `wpa3` | `auto` | `auto`: WPA2 with a password, open without |
| `ap_ip` | IPv4 | `192.168.80.1` | The access point's address; the DHCP range follows it |
| `ap_channel` | 1 to 13 | `6` | |
| `ap_bandwidth` | `ht20`, `ht40` | `ht20` | |
| `ap_hidden` | bool | `false` | Do not announce the name |
| `ap_max_connections` | 1 to 10 | `4` | |
| `ap_auto_disable` | bool | `false` | Access point off while the station is connected |
| `power_save` | `none`, `min`, `max` | `none` | |
| `wifi_ram_profile` | `full`, `lean`, `custom` | `full` | The radio's memory profile; `custom` uses the three counts below |
| `wifi_static_rx`, `wifi_static_tx`, `wifi_cache_tx` | 2 to 25, 1 to 64, 0 to 128 | `10`, `8`, `32` | Buffer counts for the custom profile |
| `cli` | bool | `true` | The `wifi` command |

## mDNS (`mdns_manager`), version 1

On the ==Settings== page as ==Network Discovery==.

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `enabled` | bool | `true` | Announce `espnetlink_<id>.local` and the `_meatpi._tcp` service |

## Home Assistant (`ha_webhooks`), version 2

On the ==Settings== page. [Home Assistant](../send-data/home-assistant.md).

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `enabled` | bool | `false` | The push runs |
| `url`, `url2` | string, 191 | `""` | The webhook URLs, the second as the fallback |
| `interval_s` | 1 to 3600 | `60` | Seconds between pushes |
| `data_mode` | `changed`, `full` | `changed` | Only changed values, or everything |
| `gzip` | bool | `false` | Compress the push |
| `manual_override` | bool | `false` | Keep the typed URL against the integration's registration |
| `cert_set` | string, 31 | `""` | A certificate set for a private CA |
| `cli` | bool | `true` | The `webhook` command |

## VPN (`vpn_manager`), version 1

On the ==VPN== page. [VPN](../connectivity/vpn.md).

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `enabled` | bool | `false` | |
| `type` | `wireguard`, `tailscale` | `wireguard` | |
| `ts_auth_key` | string, 95 | `""` | Tailscale auth key (secret) |
| `ts_device_name` | string, 47 | `""` | Tailscale node name |
| `ts_control_url` | string, 63 | `""` | Headscale URL; empty for Tailscale |
| `private_key` | string, 63 | `""` | WireGuard private key (secret) |
| `peer_public_key` | string, 63 | `""` | The server's public key |
| `preshared_key` | string, 63 | `""` | Optional (secret) |
| `address` | string, 31 | `""` | The tunnel address, with an optional `/cidr` |
| `allowed_ip`, `allowed_ip_mask` | string, 31 | `0.0.0.0` | The range through the tunnel; `0.0.0.0` derives the dongle's own /32 |
| `endpoint` | string, 63 | `""` | The server |
| `port` | 1 to 65535 | `51820` | |
| `keepalive_s` | 0 to 3600 | `25` | |
| `default_route` | bool | `false` | All traffic through the tunnel |
| `dns` | IPv4 | `""` | A DNS server while the tunnel is up |
| `cli` | bool | `true` | The `vpn` command |

## Motion (`imu_manager`), version 3

On the ==Advanced== page. [Sleep and wake](../power/sleep-and-wake.md).

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `enabled` | bool | `true` | |
| `smd` | bool | `true` | Significant motion detection (the activity state) |
| `wom` | bool | `true` | Wake on motion (bumps, the `sleep 4` wake source) |
| `smd_sensitivity` | 0 to 4 | `0` | 0 most sensitive |
| `wom_threshold` | 1 to 255 | `8` | About 3.9 mg per step |
| `stationary_s` | 1 to 3600 | `3` | Seconds without motion before Stationary |
| `cli` | bool | `true` | The `imu` command |

## Led Manager (`led_manager`), version 1

Under ==All Settings==. [LED patterns](../troubleshooting/led-patterns.md).

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `enabled` | bool | `true` | The LED at all |
| `idle_mode` | `off`, `solid`, `blink_slow` | `solid` | The idle indication's pattern |
| `idle_r`, `idle_g`, `idle_b` | 0 to 255 | `0`, `204`, `255` | The idle colour (cyan) |
| `cli` | bool | `true` | The `led` command |

## System (`system`), version 1

Under ==All Settings==.

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `device_name` | string, 32 | `ESPNetLink` | A name for the device |
| `status_led` | bool | `true` | The uplink and GPS LED policy; off keeps the idle indication |

## Logging (`log_manager`), version 1

Under ==All Settings==. [Logs and system monitor](../tools/logs-and-monitor.md).

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `level` | `none`, `error`, `warn`, `info`, `debug`, `verbose` | `info` | The level at start |
| `console_enabled` | bool | `true` | The console sink |
| `ring_enabled` | bool | `true` | The ring sink |

## Console (`cmdline_manager`), version 1

On the ==Advanced== page. [Console](../tools/console.md).

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `enabled` | bool | `true` | The command line as a whole |
| `uart` | bool | `false` | A second console on the UART |

## USB console (`usb_cli_console`), version 1

On the ==Advanced== page.

| Key | Type | Default | Meaning |
| --- | --- | --- | --- |
| `cli` | bool | `true` | The console's own commands, `echo` and `ota` |

## Status flags (`dev_status_manager`), Restart tracking (`restart_tracker`), Filesystem (`filesystem`), version 1

Under ==All Settings==. One key each: `cli` (`true`), for the `status` and `version`, `restart_tracker` and `fs` commands.
